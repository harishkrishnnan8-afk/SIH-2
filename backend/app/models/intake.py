import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class IntakeConfig(Base):
    __tablename__ = "intake_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(16), default="2026–27", nullable=False)
    supernumerary_excluded = Column(Boolean, default=True, nullable=False)
    nri_counted_separately = Column(Boolean, default=False, nullable=False)
    oci_special_quota = Column(Boolean, default=False, nullable=False)
    warn_threshold_pct = Column(Integer, default=95, nullable=False)
    max_overrun_allowed = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("institution_id", "academic_year", name="uq_institution_intake_year"),
    )

    institution = relationship("Institution", back_populates="intake_configs")
