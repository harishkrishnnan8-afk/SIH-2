from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.core.permissions import Role
from backend.app.database import get_db
from backend.app.models.admission import Admission
from backend.app.models.finding import ValidationFinding
from backend.app.models.institution import Institution
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.upload import UploadBatch
from backend.app.models.user import User
from backend.app.schemas.dashboard import CentralDashboardResponse, CentralInstitutionSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/central", response_model=CentralDashboardResponse)
def get_central_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    institutions = db.query(Institution).all()

    summaries = []
    total_enrolment = 0
    total_intake = 0
    total_findings = 0

    for inst in institutions:
        enrolment = (
            db.query(Admission)
            .filter(
                Admission.institution_id == inst.id,
                Admission.admission_status == "Admitted",
            )
            .count()
        )
        intake_sum = (
            db.query(Programme)
            .filter(Programme.institution_id == inst.id)
            .all()
        )
        approved_intake = sum(p.approved_intake for p in intake_sum) or 1

        findings_count = (
            db.query(ValidationFinding)
            .filter(
                ValidationFinding.institution_id == inst.id,
                ValidationFinding.status.in_(["Open", "Under review", "Escalated"]),
            )
            .count()
        )

        total_students = (
            db.query(Student).filter(Student.institution_id == inst.id).count()
        )
        verified_students = (
            db.query(Student)
            .filter(Student.institution_id == inst.id, Student.status == "Verified")
            .count()
        )
        quality_score = (
            int((verified_students / total_students) * 100) if total_students > 0 else 95
        )

        batches = db.query(UploadBatch).filter(UploadBatch.institution_id == inst.id).count()
        submission_status = "Submitted" if batches > 0 else "In progress"

        total_enrolment += enrolment
        total_intake += approved_intake
        total_findings += findings_count

        summaries.append(
            CentralInstitutionSummary(
                id=inst.id,
                name=inst.name,
                ref=inst.ref,
                status=inst.status,
                state=inst.state,
                enrolment=enrolment,
                intake=approved_intake,
                findings=findings_count,
                submission=submission_status,
                quality=quality_score,
            )
        )

    utilisation_pct = (
        int((total_enrolment / total_intake) * 100) if total_intake > 0 else 0
    )

    return CentralDashboardResponse(
        institutionsInScope=len(institutions),
        totalEnrolment=total_enrolment,
        intakeUtilisationPct=utilisation_pct,
        outstandingFindings=total_findings,
        institutions=summaries,
    )
