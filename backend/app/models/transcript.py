from sqlalchemy import Column, String, JSON, DateTime, func
from app.models.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=True)
    format = Column(String, nullable=False)  # txt, vtt, srt, json
    sentences = Column(JSON, nullable=False) # Store arrays of sentence data (text, speaker, timestamp)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
