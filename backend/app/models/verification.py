import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class VerificationAttempt(Base):
    __tablename__ = "verification_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    apaar_query_masked = Column(String(32), nullable=False)
    mode = Column(String(32), default="simulated", nullable=False)  # format, internal, simulated, external
    format_valid = Column(Boolean, default=False, nullable=False)
    internal_match = Column(Boolean, default=False, nullable=False)
    matched_student_id = Column(String(36), ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    provider_status = Column(String(32), default="Mock provider", nullable=False)  # Mock provider, Online, Unavailable
    is_simulated = Column(Boolean, default=True, nullable=False)
    simulation_label = Column(String(64), default="SIMULATED — NOT OFFICIAL APAAR VERIFICATION", nullable=False)
    raw_response_summary = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ConsentStatus(Base):
    __tablename__ = "consent_statuses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_given = Column(Boolean, default=True, nullable=False)
    consent_type = Column(String(64), default="apaar_verification_and_storage", nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    student = relationship("Student", back_populates="consent_statuses")
