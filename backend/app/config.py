import os
import tempfile
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

# Check if running in serverless / read-only environment (e.g. Vercel, AWS Lambda)
is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("SERVERLESS"))

if is_serverless:
    DATA_DIR = Path(tempfile.gettempdir()) / "resume_data"
else:
    try:
        DATA_DIR = BASE_DIR / "data"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        DATA_DIR = Path(tempfile.gettempdir()) / "resume_data"

UPLOADS_DIR = DATA_DIR / "uploads"
INDEX_STORE_DIR = DATA_DIR / "indexes"
JOBS_DIR = DATA_DIR / "jobs"

for d in [DATA_DIR, UPLOADS_DIR, INDEX_STORE_DIR, JOBS_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

class Settings(BaseModel):
    app_name: str = "Resume Intelligence (PageIndex + Agentic RAG)"
    app_version: str = "1.0.0"
    active_provider: str = os.getenv("LLM_PROVIDER", "mock")  # "gemini", "openai", "anthropic", "groq", "mock"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")

settings = Settings()
