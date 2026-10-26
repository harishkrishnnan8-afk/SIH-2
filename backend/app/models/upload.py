import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id = Column(String(36), primary_key=True, index=True)  # e.g. "BATCH-0412"
    institution_id = Column(String(64), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    uploaded_by_name = Column(String(128), nullable=False)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), default="Processing", nullable=False)  # Completed, Completed with errors, Failed, Processing
    total = Column(Integer, default=0, nullable=False)
    accepted = Column(Integer, default=0, nullable=False)
    rejected = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    institution = relationship("Institution", back_populates="upload_batches")
    row_results = relationship("UploadRowResult", back_populates="batch", cascade="all, delete-orphan")


class UploadRowResult(Base):
    __tablename__ = "upload_row_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("upload_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    field = Column(String(64), nullable=True)
    raw_value = Column(String(255), nullable=True)
    rule = Column(Text, nullable=False)
    is_error = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    batch = relationship("UploadBatch", back_populates="row_results")
