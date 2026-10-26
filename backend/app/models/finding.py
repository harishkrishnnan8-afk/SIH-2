from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    id = Column(String(36), primary_key=True, index=True)  # e.g. "FND-2601"
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True)
    category = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), default="Medium", nullable=False)  # High, Medium, Low
    detected_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    status = Column(String(32), default="Open", nullable=False, index=True)  # Open, Under review, Resolved, Escalated
    reviewer_name = Column(String(128), nullable=True)
    rule = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    next_steps = Column(Text, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    institution = relationship("Institution", back_populates="findings")
    student = relationship("Student", back_populates="findings")
    review_actions = relationship("ReviewAction", back_populates="finding", cascade="all, delete-orphan")
