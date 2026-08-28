import os
import traceback
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.config import settings, BASE_DIR
from app.index.store import store
from app.sample_data.generator import SampleDataLoader
from app.api.routes_resumes import router as resumes_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_agent import router as agent_router
from app.api.routes_settings import router as settings_router

def ensure_initial_data():
    if len(store.list_candidates()) == 0:
        try:
            SampleDataLoader.load_all_samples()
        except Exception as e:
            print(f"Non-fatal error initializing sample data: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_initial_data()
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Vectorless Structure-Aware PageIndex RAG + Agentic RAG for Grounded Candidate Scoring & Ranking",
    lifespan=lifespan
)

# Global Exception Handler to avoid opaque 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    err_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(f"Unhandled Exception on {request.url.path}: {err_str}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "path": str(request.url.path), "error_type": type(exc).__name__}
    )

# Enable CORS for all environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware / Hook to ensure data on serverless cold starts
@app.middleware("http")
async def ensure_data_middleware(request: Request, call_next):
    if len(store.list_candidates()) == 0 and not request.url.path.startswith("/assets"):
        ensure_initial_data()
    response = await call_next(request)
    return response

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
    ensure_initial_data()
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "active_provider": settings.active_provider,
        "candidate_count": len(store.list_candidates()),
        "job_count": len(store.list_jobs())
    }

# Check for production frontend build (e.g. on Render or unified containers)
frontend_dist = BASE_DIR.parent / "frontend" / "dist"
if not frontend_dist.exists():
    frontend_dist = Path("/app/frontend/dist")

if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path == "openapi.json":
            raise HTTPException(status_code=404, detail="Not Found")
        
        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        raise HTTPException(status_code=404, detail="Frontend build index not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
