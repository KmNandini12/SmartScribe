from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class SentenceData(BaseModel):
    text: str
    speaker: Optional[str] = None
    timestamp: Optional[str] = None

class TranscriptCreate(BaseModel):
    title: str
    format: str
    sentences: List[SentenceData]

class TranscriptResponse(BaseModel):
    id: str
    title: Optional[str]
    format: str
    sentences: List[SentenceData]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
