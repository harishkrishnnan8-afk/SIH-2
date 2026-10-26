import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Admission(Base):
    __tablename__ = "admissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    programme_id = Column(String(36), ForeignKey("programmes.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(16), default="2026–27", nullable=False, index=True)
    admission_year = Column(Integer, default=2026, nullable=False)
    category = Column(String(32), default="General", nullable=False, index=True)  # General, Supernumerary, NRI, OCI, Foreign National
    admission_status = Column(String(32), default="Admitted", nullable=False)
    is_nri = Column(Boolean, default=False, nullable=False)
    is_oci = Column(Boolean, default=False, nullable=False)
    oci_card_number = Column(String(64), nullable=True)
    is_foreign = Column(Boolean, default=False, nullable=False)
    nationality = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        Index("ix_admission_prog_year_cat", "programme_id", "academic_year", "category"),
    )

    student = relationship("Student", back_populates="admissions")
    programme = relationship("Programme", back_populates="admissions")
    institution = relationship("Institution", back_populates="admissions")
