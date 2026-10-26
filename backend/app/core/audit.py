import random
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditEvent


def log_audit_event(
    db: Session,
    action: str,
    actor_name: str,
    actor_role: str,
    ref: str = "—",
    result: str = "Success",
    institution_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditEvent:
    """Record an immutable audit event without sensitive personal data."""
    # Generate sequential/unique audit identifier
    rnd_suffix = random.randint(1000, 9999)
    event_id = f"AUD-{rnd_suffix}"
    
    # Ensure ID uniqueness
    while db.query(AuditEvent).filter(AuditEvent.id == event_id).first():
        rnd_suffix = random.randint(1000, 9999)
        event_id = f"AUD-{rnd_suffix}"

    event = AuditEvent(
        id=event_id,
        institution_id=institution_id,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        ref=ref,
        result=result,
        details=details,
        ip_address=ip_address,
    )
    db.add(event)
    db.flush()
    return event
