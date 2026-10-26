import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, index=True)  # e.g. "STU-1001" or UUID
    internal_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    dob = Column(String(16), nullable=False)  # YYYY-MM-DD
    gender = Column(String(16), default="Not specified", nullable=False)
    email = Column(String(128), nullable=True)
    masked_apaar = Column(String(32), nullable=False)  # e.g. "•••• •••• 9012"
    apaar_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hash for exact-match indexing
    status = Column(String(32), default="Pending review", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        Index("ix_student_inst_name_dob", "institution_id", "name", "dob"),
    )

    institution = relationship("Institution", back_populates="students")
    admissions = relationship("Admission", back_populates="student", cascade="all, delete-orphan")
    findings = relationship("ValidationFinding", back_populates="student", cascade="all, delete-orphan")
    consent_statuses = relationship("ConsentStatus", back_populates="student", cascade="all, delete-orphan")
