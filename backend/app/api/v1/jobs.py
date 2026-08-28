from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.job import Job, JobState
from app.models.transcript import Transcript
from app.schemas.job import JobCreate, JobResponse
from app.worker.tasks import summarize_transcript
import uuid

router = APIRouter()

@router.post("/summarize", status_code=status.HTTP_202_ACCEPTED)
async def create_summarize_job(
    request: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify transcript exists
    result = await db.execute(select(Transcript).where(Transcript.id == request.transcript_id))
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
        
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        transcript_id=transcript.id,
        status=JobState.PENDING
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Dispatch Celery task
    summarize_transcript.delay(job_id)
    
    return {"job_id": job_id, "status": "202 Accepted"}

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job

from app.models.summary import Summary

@router.get("/{job_id}/summary")
async def get_job_summary(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Summary).where(Summary.job_id == job_id))
    summary = result.scalar_one_or_none()
    
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
        
    return summary
