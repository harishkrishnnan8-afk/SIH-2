from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.permissions import Permission, Role
from backend.app.database import get_db
from backend.app.models.institution import Institution
from backend.app.models.user import User
from backend.app.schemas.institution import InstitutionResponse, InstitutionUpdate

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("", response_model=List[InstitutionResponse])
def list_institutions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Institution)
    # If standard institution user, they only have access to their own institution
    # unless reviewing institutions directory
    institutions = query.all()
    return [
        InstitutionResponse(
            id=i.id,
            name=i.name,
            ref=i.ref,
            status=i.status,
            state=i.state,
        )
        for i in institutions
    ]


@router.patch("/{institution_id}", response_model=InstitutionResponse)
def update_institution(
    institution_id: str,
    payload: InstitutionUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_INSTITUTIONS)),
    db: Session = Depends(get_db),
):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution '{institution_id}' not found.",
        )

    if payload.name is not None:
        inst.name = payload.name
    if payload.state is not None:
        inst.state = payload.state
    if payload.status is not None:
        inst.status = payload.status

    log_audit_event(
        db=db,
        action="Updated institution details",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=inst.id,
        ref=inst.id,
        result="Success",
    )
    db.commit()
    db.refresh(inst)

    return InstitutionResponse(
        id=inst.id,
        name=inst.name,
        ref=inst.ref,
        status=inst.status,
        state=inst.state,
    )
