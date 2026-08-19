from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.job import JobState

class JobCreate(BaseModel):
    transcript_id: str

class JobResponse(BaseModel):
    id: str
    transcript_id: str
    status: JobState
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
