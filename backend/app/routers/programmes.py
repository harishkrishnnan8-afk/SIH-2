from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.core.permissions import Role
from backend.app.database import get_db
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.user import User
from backend.app.schemas.programme import ProgrammeResponse

router = APIRouter(prefix="/programmes", tags=["Programmes"])


@router.get("", response_model=List[ProgrammeResponse])
def list_programmes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Programme)
    if current_user.role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        query = query.filter(Programme.institution_id == current_user.institution_id)

    programmes = query.all()
    results = []
    for p in programmes:
        # Count actual enrolment from real database records
        enrolment_count = (
            db.query(Admission)
            .filter(
                Admission.programme_id == p.id,
                Admission.admission_status == "Admitted",
            )
            .count()
        )
        results.append(
            ProgrammeResponse(
                code=p.code,
                name=p.name,
                year=p.academic_year,
                approvedIntake=p.approved_intake,
                actualEnrolment=enrolment_count,
                institutionId=p.institution_id,
                policy=p.policy,
            )
        )
    return results
