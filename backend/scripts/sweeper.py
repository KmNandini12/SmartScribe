import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.job import Job, JobState

async def sweep_zombie_tasks():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Sweeper starting...")
    timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=10)
    
    async with async_session_maker() as session:
        # Find jobs stuck in PROCESSING for more than 10 minutes
        # created_at/updated_at can be used
        result = await session.execute(
            select(Job).where(
                Job.status == JobState.PROCESSING,
                Job.updated_at < timeout_threshold
            )
        )
        zombie_jobs = result.scalars().all()
        
        for job in zombie_jobs:
            print(f"Marking job {job.id} as FAILED_TIMEOUT")
            job.status = JobState.FAILED_TIMEOUT
            job.error_message = "Worker timeout - stuck in processing for > 10 minutes"
            
        if zombie_jobs:
            await session.commit()
            print(f"Sweeper finished. Swept {len(zombie_jobs)} jobs.")
        else:
            print("Sweeper finished. No zombie jobs found.")

if __name__ == "__main__":
    asyncio.run(sweep_zombie_tasks())
