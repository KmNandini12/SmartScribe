from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import transcripts, jobs

app = FastAPI(title="SmartScribe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcripts.router, prefix="/api/v1/transcripts", tags=["Transcripts"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
