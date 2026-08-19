from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.transcript import Transcript
from app.schemas.transcript import TranscriptResponse, SentenceData
import uuid
import re

router = APIRouter()

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

@router.post("/", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 15MB Payload Ingestion DoS Mitigation
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large. Max size is 15MB.")
        
    content = await file.read()
    text = content.decode("utf-8")
    
    # Simple parser for sentences (can be expanded for VTT/JSON)
    raw_sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = [
        SentenceData(text=s.strip(), speaker="Unknown", timestamp="00:00:00").model_dump()
        for s in raw_sentences if s.strip()
    ]
    
    transcript_id = str(uuid.uuid4())
    transcript = Transcript(
        id=transcript_id,
        title=file.filename,
        format=file.filename.split(".")[-1] if "." in file.filename else "txt",
        sentences=sentences
    )
    
    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)
    
    return transcript

@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(transcript_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
        
    return transcript
