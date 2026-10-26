from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.permissions import Permission, Role
from backend.app.database import get_db
from backend.app.models.audit import AuditEvent
from backend.app.models.user import User
from backend.app.schemas.audit import AuditEntryResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("", response_model=List[AuditEntryResponse])
def list_audit_events(
    actor: Optional[str] = None,
    action: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.VIEW_AUDIT)),
    db: Session = Depends(get_db),
):
    query = db.query(AuditEvent)
    if current_user.role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        query = query.filter(AuditEvent.institution_id == current_user.institution_id)

    if actor and actor != "all":
        query = query.filter(AuditEvent.actor_name.ilike(f"%{actor}%"))

    if action and action != "all":
        query = query.filter(AuditEvent.action.ilike(f"%{action}%"))

    audits = query.order_by(AuditEvent.timestamp.desc()).limit(100).all()

    return [
        AuditEntryResponse(
            id=a.id,
            at=a.timestamp.isoformat(),
            actor=a.actor_name,
            role=a.actor_role,
            action=a.action,
            ref=a.ref,
            result=a.result,
        )
        for a in audits
    ]
