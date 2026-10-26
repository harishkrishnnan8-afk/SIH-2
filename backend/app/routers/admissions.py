from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.core.permissions import Role
from backend.app.database import get_db
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.schemas.student import StudentResponse

router = APIRouter(prefix="/admissions", tags=["Admissions"])


@router.get("", response_model=List[StudentResponse])
def list_admissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Student, Admission, Programme)
        .join(Admission, Admission.student_id == Student.id)
        .join(Programme, Programme.id == Admission.programme_id)
    )

    if current_user.role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        query = query.filter(Admission.institution_id == current_user.institution_id)

    results = query.order_by(Admission.created_at.desc()).all()

    return [
        StudentResponse(
            id=s.id,
            name=s.name,
            apaar=s.masked_apaar,
            programme=prog.code,
            admissionYear=adm.admission_year,
            category=adm.category,
            status=s.status,
            updated=adm.updated_at.isoformat(),
            dob=s.dob,
            gender=s.gender,
            email=s.email or f"{s.id.lower()}@example.edu",
            institutionId=adm.institution_id,
        )
        for s, adm, prog in results
    ]
