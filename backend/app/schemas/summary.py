from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from datetime import datetime

class SummaryResponse(BaseModel):
    id: str
    job_id: str
    transcript_id: str
    extracted_points: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
