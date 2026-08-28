import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.index.store import store
from app.sample_data.generator import SampleDataLoader
from app.api.routes_resumes import router as resumes_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_agent import router as agent_router
from app.api.routes_settings import router as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # If store is empty on launch, automatically preload realistic samples
    if len(store.list_candidates()) == 0:
        print("Preloading initial sample resumes and jobs...")
        SampleDataLoader.load_all_samples()
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Vectorless Structure-Aware PageIndex RAG + Agentic RAG for Grounded Candidate Scoring & Ranking",
    lifespan=lifespan
)

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(agent_router)
app.include_router(settings_router)

@app.post("/api/preload-samples")
async def preload_samples():
    result = SampleDataLoader.load_all_samples()
    return result

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "active_provider": settings.active_provider,
        "candidate_count": len(store.list_candidates()),
        "job_count": len(store.list_jobs())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
