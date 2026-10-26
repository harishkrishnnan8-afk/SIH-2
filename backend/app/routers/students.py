import random
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.masking import hash_apaar, mask_apaar
from backend.app.core.permissions import Permission, Role, require_institution_access
from backend.app.database import get_db
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.rules.engine import persist_findings, validate_student_record
from backend.app.schemas.student import SaveStudentResult, StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


def generate_student_id(db: Session) -> str:
    for _ in range(100):
        rnd = random.randint(1001, 9999)
        sid = f"STU-{rnd}"
        if not db.query(Student).filter(Student.id == sid).first():
            return sid
    return f"STU-{random.randint(10000, 99999)}"


@router.get("", response_model=List[StudentResponse])
def list_students(
    q: Optional[str] = None,
    programme: Optional[str] = None,
    status: Optional[str] = None,
    institution_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Student, Admission, Programme).join(
        Admission, Admission.student_id == Student.id
    ).join(
        Programme, Programme.id == Admission.programme_id
    )

    # Tenant isolation enforcement
    if current_user.role in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        if institution_id:
            query = query.filter(Student.institution_id == institution_id)
    else:
        query = query.filter(Student.institution_id == current_user.institution_id)

    if programme and programme != "all":
        query = query.filter(Programme.code == programme)

    if status and status != "all":
        query = query.filter(Student.status == status)

    if q:
        search = f"%{q.strip().lower()}%"
        query = query.filter(
            (Student.name.ilike(search))
            | (Student.id.ilike(search))
            | (Student.masked_apaar.ilike(search))
        )

    results = query.order_by(Student.updated_at.desc()).all()

    items = []
    for s, adm, prog in results:
        items.append(
            StudentResponse(
                id=s.id,
                name=s.name,
                apaar=s.masked_apaar,  # Masked by default
                programme=prog.code,
                admissionYear=adm.admission_year,
                category=adm.category,
                status=s.status,
                updated=s.updated_at.isoformat(),
                dob=s.dob,
                gender=s.gender,
                email=s.email or f"{s.id.lower()}@example.edu",
                institutionId=s.institution_id,
            )
        )
    return items


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(Student, Admission, Programme)
        .join(Admission, Admission.student_id == Student.id)
        .join(Programme, Programme.id == Admission.programme_id)
        .filter(Student.id == student_id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record '{student_id}' not found.",
        )

    student, admission, programme = record

    # Tenant isolation check
    require_institution_access(current_user, student.institution_id)

    return StudentResponse(
        id=student.id,
        name=student.name,
        apaar=student.masked_apaar,
        programme=programme.code,
        admissionYear=admission.admission_year,
        category=admission.category,
        status=student.status,
        updated=student.updated_at.isoformat(),
        dob=student.dob,
        gender=student.gender,
        email=student.email or f"{student.id.lower()}@example.edu",
        institutionId=student.institution_id,
    )


@router.post("", response_model=SaveStudentResult)
def create_student(
    payload: StudentCreate,
    current_user: User = Depends(require_permission(Permission.CREATE_STUDENT)),
    db: Session = Depends(get_db),
):
    target_inst_id = current_user.institution_id or "INS-001"

    # Find programme
    programme = (
        db.query(Programme)
        .filter(
            Programme.institution_id == target_inst_id,
            Programme.code == payload.programme,
        )
        .first()
    )
    if not programme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Programme '{payload.programme}' is not offered by institution {target_inst_id}.",
        )

    # Run deterministic validation rules
    findings_data = validate_student_record(
        db=db,
        institution_id=target_inst_id,
        name=payload.name,
        raw_apaar=payload.apaar,
        programme_code=payload.programme,
        admission_category=payload.category,
        dob=payload.dob or "2006-01-01",
        is_oci=payload.oci,
        oci_card_number=payload.ociCard,
    )

    clean_digits = re.sub(r"\D", "", payload.apaar)
    masked = mask_apaar(clean_digits)
    apaar_h = hash_apaar(clean_digits) if len(clean_digits) == 12 else None

    # Determine status based on findings
    initial_status = "Pending review" if findings_data else "Verified"

    student_id = generate_student_id(db)

    new_student = Student(
        id=student_id,
        institution_id=target_inst_id,
        name=payload.name.strip(),
        dob=payload.dob or "2006-01-01",
        gender=payload.gender or "Not specified",
        email=payload.email or f"{payload.name.split()[0].lower()}.{student_id.lower()}@example.edu",
        masked_apaar=masked,
        apaar_hash=apaar_h,
        status=initial_status,
    )
    db.add(new_student)
    db.flush()

    # Parse admission year integer
    adm_year_int = 2026
    year_match = re.search(r"(\d{4})", payload.year or "")
    if year_match:
        adm_year_int = int(year_match.group(1))

    new_admission = Admission(
        student_id=new_student.id,
        programme_id=programme.id,
        institution_id=target_inst_id,
        academic_year=payload.year or "2026–27",
        admission_year=adm_year_int,
        category=payload.category,
        admission_status="Admitted",
        is_nri=payload.nri,
        is_oci=payload.oci,
        oci_card_number=payload.ociCard,
        is_foreign=payload.foreign,
        nationality=payload.nationality,
    )
    db.add(new_admission)

    # Persist findings if any rule triggered
    if findings_data:
        persist_findings(
            db=db,
            institution_id=target_inst_id,
            findings_data=findings_data,
            student_id=new_student.id,
        )

    # Record audit event
    log_audit_event(
        db=db,
        action="Updated admission record",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=target_inst_id,
        ref=student_id,
        result="Success",
        details=f"Registered student with {len(findings_data)} findings generated",
    )

    db.commit()

    return SaveStudentResult(
        persisted=True,
        student_id=student_id,
        findings_count=len(findings_data),
        message="Student identity and admission record persisted successfully.",
    )
