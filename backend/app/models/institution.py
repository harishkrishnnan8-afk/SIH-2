from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String(64), primary_key=True, index=True)  # e.g. "INS-001"
    name = Column(String(255), nullable=False)
    ref = Column(String(64), unique=True, nullable=False, index=True)  # e.g. "DEMO-AICTE-0001"
    state = Column(String(64), nullable=False)
    status = Column(String(32), default="Active", nullable=False)  # "Active", "Under review", "Suspended"
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="institution", cascade="all, delete-orphan")
    programmes = relationship("Programme", back_populates="institution", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="institution", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="institution", cascade="all, delete-orphan")
    upload_batches = relationship("UploadBatch", back_populates="institution", cascade="all, delete-orphan")
    findings = relationship("ValidationFinding", back_populates="institution", cascade="all, delete-orphan")
    intake_configs = relationship("IntakeConfig", back_populates="institution", cascade="all, delete-orphan")
