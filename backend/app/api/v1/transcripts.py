from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.transcript import Transcript
from app.schemas.transcript import TranscriptResponse, SentenceData
from app.core.config import settings
import uuid
import re
import hashlib
import redis.asyncio as redis
import json

router = APIRouter()

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

# Initialize async redis client
redis_client = redis.from_url(settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")

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
    
    # SHA-256 Deduplication
    file_hash = hashlib.sha256(content).hexdigest()
    cached_transcript_id = await redis_client.get(f"transcript_hash:{file_hash}")
    
    if cached_transcript_id:
        # Cache hit! Return existing transcript
        result = await db.execute(select(Transcript).where(Transcript.id == cached_transcript_id.decode("utf-8")))
        existing_transcript = result.scalar_one_or_none()
        if existing_transcript:
            return existing_transcript

    text = content.decode("utf-8")
    
    # Advanced parser for identifying speakers
    raw_lines = text.split('\n')
    sentences = []
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
            
        # Ignore purely systemic log lines like "--- 11:45 AM ---"
        if line.startswith('---') and line.endswith('---'):
            continue
            
        speaker = "Unknown"
        timestamp = "00:00:00"
        sentence_text = line
        
        # Match Campfire style: [     Doug A.:] text
        campfire_match = re.match(r'^\[\s*([^\]]+?)\s*\]\s*(.*)', line)
        if campfire_match:
            speaker_raw = campfire_match.group(1).strip()
            if speaker_raw.endswith(':'):
                speaker = speaker_raw[:-1].strip()
            elif re.match(r'^\d{1,2}:\d{2}\s*(AM|PM)?$', speaker_raw):
                timestamp = speaker_raw
                speaker = "System"
            else:
                speaker = speaker_raw
            sentence_text = campfire_match.group(2).strip()
        else:
            # Match standard transcript: "Sarah: Let's do a quick sync"
            standard_match = re.match(r'^([A-Za-z0-9\s_]+):\s*(.*)', line)
            if standard_match:
                speaker = standard_match.group(1).strip()
                sentence_text = standard_match.group(2).strip()
                
        if sentence_text:
            sentences.append(
                SentenceData(text=sentence_text, speaker=speaker, timestamp=timestamp).model_dump()
            )
    
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
    
    # Save to Redis cache
    await redis_client.set(f"transcript_hash:{file_hash}", transcript_id)
    
    return transcript

@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(transcript_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
        
    return transcript
