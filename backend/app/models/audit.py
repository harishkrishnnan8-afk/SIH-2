from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, index=True)  # e.g. "AUD-9001"
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_name = Column(String(128), nullable=False)
    actor_role = Column(String(32), nullable=False)
    action = Column(String(128), nullable=False, index=True)
    ref = Column(String(64), nullable=False, default="—")
    result = Column(String(16), default="Success", nullable=False)  # Success, Denied, Failed
    details = Column(Text, nullable=True)  # Non-sensitive contextual description
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
