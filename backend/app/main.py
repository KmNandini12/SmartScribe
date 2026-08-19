from fastapi import FastAPI
from app.api.v1 import transcripts, jobs

app = FastAPI(title="SmartScribe API", version="1.0.0")

app.include_router(transcripts.router, prefix="/api/v1/transcripts", tags=["Transcripts"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
