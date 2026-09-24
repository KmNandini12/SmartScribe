import asyncio
from celery import Task
from app.core.celery_app import celery_app
from app.core.database import async_session_maker
from app.models.job import Job, JobState
from app.models.transcript import Transcript
from app.models.summary import Summary
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import numpy as np
import uuid
from datetime import datetime, timezone

# Singleton model loader
class MLModelSingleton:
    _instance = None

    @classmethod
    def get_model(cls):
        if cls._instance is None:
            # Load the embedding model once
            cls._instance = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._instance

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

async def process_summary_async(job_id: str):
    db_url = settings.DATABASE_URL or f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    local_engine = create_async_engine(db_url, poolclass=None)
    local_session_maker = async_sessionmaker(local_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with local_session_maker() as session:
        # Fetch Job
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            await local_engine.dispose()
            return
            
        job.status = JobState.PROCESSING
        await session.commit()
        
        try:
            # Fetch Transcript
            result = await session.execute(select(Transcript).where(Transcript.id == job.transcript_id))
            transcript = result.scalar_one_or_none()
            
            if not transcript or not transcript.sentences:
                raise ValueError("Transcript not found or has no sentences")
                
            sentences_data = transcript.sentences
            texts = [s["text"] for s in sentences_data]
            
            # Load model and compute embeddings
            model = MLModelSingleton.get_model()
            embeddings = model.encode(texts)
            
            # K-Means clustering (deterministic by fixing random_state)
            num_clusters = min(len(texts), 5) # E.g. extract 5 points
            kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init="auto")
            kmeans.fit(embeddings)
            
            # Find closest sentence to each centroid
            extracted_points = []
            for i in range(num_clusters):
                centroid = kmeans.cluster_centers_[i]
                distances = np.linalg.norm(embeddings - centroid, axis=1)
                closest_idx = int(np.argmin(distances))
                
                extracted_points.append({
                    "text": sentences_data[closest_idx]["text"],
                    "speaker": sentences_data[closest_idx].get("speaker"),
                    "timestamp": sentences_data[closest_idx].get("timestamp"),
                })
                
            # Create Summary
            summary_id = str(uuid.uuid4())
            summary = Summary(
                id=summary_id,
                job_id=job.id,
                transcript_id=transcript.id,
                extracted_points=extracted_points
            )
            session.add(summary)
            
            job.status = JobState.COMPLETED
            await session.commit()
            
        except Exception as e:
            job.status = JobState.FAILED
            job.error_message = str(e)
            await session.commit()
            raise e
        finally:
            await local_engine.dispose()

@celery_app.task(bind=True, name="summarize_transcript", time_limit=300, soft_time_limit=240, max_retries=3)
def summarize_transcript(self, job_id: str):
    try:
        asyncio.run(process_summary_async(job_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
