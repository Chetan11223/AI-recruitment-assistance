from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.config import settings

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    active_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    model_name: Optional[str] = None

@router.get("")
async def get_settings():
    def mask_key(k: str) -> str:
        if not k:
            return ""
        if len(k) <= 8:
            return "********"
        return k[:4] + "..." + k[-4:]

    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "active_provider": settings.active_provider,
        "model_name": settings.model_name,
        "has_gemini_key": bool(settings.gemini_api_key),
        "has_openai_key": bool(settings.openai_api_key),
        "has_anthropic_key": bool(settings.anthropic_api_key),
        "has_groq_key": bool(settings.groq_api_key),
        "gemini_masked": mask_key(settings.gemini_api_key),
        "openai_masked": mask_key(settings.openai_api_key),
        "anthropic_masked": mask_key(settings.anthropic_api_key),
        "groq_masked": mask_key(settings.groq_api_key)
    }

@router.post("")
async def update_settings(payload: SettingsUpdateRequest):
    if payload.active_provider:
        settings.active_provider = payload.active_provider
    if payload.gemini_api_key is not None:
        settings.gemini_api_key = payload.gemini_api_key
    if payload.openai_api_key is not None:
        settings.openai_api_key = payload.openai_api_key
    if payload.anthropic_api_key is not None:
        settings.anthropic_api_key = payload.anthropic_api_key
    if payload.groq_api_key is not None:
        settings.groq_api_key = payload.groq_api_key
    if payload.model_name is not None:
        settings.model_name = payload.model_name

    return {"status": "success", "active_provider": settings.active_provider}
