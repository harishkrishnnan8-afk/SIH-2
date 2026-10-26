import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Programme(Base):
    __tablename__ = "programmes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(32), nullable=False, index=True)  # e.g. "BT-CSE"
    name = Column(String(128), nullable=False)
    academic_year = Column(String(16), default="2026–27", nullable=False)
    approved_intake = Column(Integer, default=60, nullable=False)
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    policy = Column(String(64), default="Supernumerary excluded", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("institution_id", "code", "academic_year", name="uq_institution_prog_year"),
    )

    institution = relationship("Institution", back_populates="programmes")
    admissions = relationship("Admission", back_populates="programme", cascade="all, delete-orphan")
