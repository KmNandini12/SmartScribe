from sqlalchemy import Column, String, DateTime, ForeignKey, func, Enum
from app.models.base import Base
import enum

class JobState(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    FAILED_TIMEOUT = "FAILED_TIMEOUT"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    transcript_id = Column(String, ForeignKey("transcripts.id"), nullable=False, index=True)
    status = Column(Enum(JobState), default=JobState.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(String, nullable=True)
