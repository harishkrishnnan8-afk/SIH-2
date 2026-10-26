import csv
import io
from typing import Any, Dict, List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.masking import sanitize_csv_cell
from backend.app.core.permissions import Permission, Role
from backend.app.database import get_db
from backend.app.models.admission import Admission
from backend.app.models.audit import AuditEvent
from backend.app.models.finding import ValidationFinding
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.upload import UploadBatch
from backend.app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])


def get_report_rows(
    report_key: str,
    institution_id: str,
    user_role: str,
    db: Session,
) -> Tuple[List[str], List[List[Any]]]:
    if report_key == "enrolment":
        programmes = db.query(Programme)
        if user_role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
            programmes = programmes.filter(Programme.institution_id == institution_id)
        progs = programmes.all()
        header = ["Programme", "Enrolled"]
        data = []
        for p in progs:
            count = (
                db.query(Admission)
                .filter(Admission.programme_id == p.id, Admission.admission_status == "Admitted")
                .count()
            )
            data.append([p.code, count])
        return header, data

    elif report_key == "intake":
        programmes = db.query(Programme)
        if user_role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
            programmes = programmes.filter(Programme.institution_id == institution_id)
        progs = programmes.all()
        header = ["Programme", "Approved", "Enrolled", "Utilisation %"]
        data = []
        for p in progs:
            count = (
                db.query(Admission)
                .filter(Admission.programme_id == p.id, Admission.admission_status == "Admitted")
                .count()
            )
            pct = round((count / p.approved_intake) * 100) if p.approved_intake > 0 else 0
            data.append([p.code, p.approved_intake, count, pct])
        return header, data

    elif report_key == "findings":
        q = db.query(ValidationFinding)
        if user_role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
            q = q.filter(ValidationFinding.institution_id == institution_id)
        findings = q.order_by(ValidationFinding.detected_at.desc()).all()
        header = ["Reference", "Category", "Severity", "Status"]
        data = [[f.id, f.category, f.severity, f.status] for f in findings]
        return header, data

    elif report_key == "imports":
        q = db.query(UploadBatch)
        if user_role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
            q = q.filter(UploadBatch.institution_id == institution_id)
        batches = q.order_by(UploadBatch.created_at.desc()).all()
        header = ["Batch", "File", "Accepted", "Rejected"]
        data = [[b.id, b.filename, b.accepted, b.rejected] for b in batches]
        return header, data

    elif report_key == "quality":
        q = db.query(Student)
        if user_role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
            q = q.filter(Student.institution_id == institution_id)
        students = q.all()
        statuses = ["Verified", "Pending review", "Flagged", "Correction requested", "Draft"]
        header = ["Status", "Records"]
        data = [[st, sum(1 for s in students if s.status == st)] for st in statuses]
        return header, data

    elif report_key == "audit":
        q = db.query(AuditEvent)
        if user_role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
            q = q.filter(AuditEvent.institution_id == institution_id)
        audits = q.order_by(AuditEvent.timestamp.desc()).limit(100).all()
        header = ["Timestamp", "Actor", "Action", "Result"]
        data = [[a.timestamp.isoformat(), a.actor_name, a.action, a.result] for a in audits]
        return header, data

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown report key '{report_key}'.",
        )


@router.get("/data")
def get_report_data(
    key: str = Query("enrolment"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    header, rows = get_report_rows(
        report_key=key,
        institution_id=current_user.institution_id or "INS-001",
        user_role=current_user.role,
        db=db,
    )
    return {"headers": header, "rows": rows}


@router.get("/export")
def export_report_csv(
    key: str = Query("enrolment"),
    current_user: User = Depends(require_permission(Permission.EXPORT_REPORTS)),
    db: Session = Depends(get_db),
):
    header, rows = get_report_rows(
        report_key=key,
        institution_id=current_user.institution_id or "INS-001",
        user_role=current_user.role,
        db=db,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    # Header disclaimer banner
    writer.writerow(["DEMO ENVIRONMENT — SYNTHETIC DATA"])
    # Sanitized header
    writer.writerow([sanitize_csv_cell(h) for h in header])
    # Sanitized data rows (mitigating formula injection)
    for r in rows:
        writer.writerow([sanitize_csv_cell(cell) for cell in r])

    # Record report export audit event
    log_audit_event(
        db=db,
        action="Exported report",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=current_user.institution_id,
        ref=f"RPT-{key.upper()}",
        result="Success",
        details=f"Exported {key} report with {len(rows)} records",
    )
    db.commit()

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="DEMO_{key}_report.csv"'},
    )
