from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, func
from app.models.base import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    transcript_id = Column(String, ForeignKey("transcripts.id"), nullable=False, index=True)
    
    # Store verbatim extracted points, directly mapped to source timestamps/speaker tags
    extracted_points = Column(JSON, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
