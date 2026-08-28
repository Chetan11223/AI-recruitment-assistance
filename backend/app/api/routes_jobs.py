import re
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.index.store import store
from app.index.schema import JobDescription
from app.parser.tree_builder import COMMON_SKILLS

router = APIRouter(prefix="/api/jobs", tags=["Job Descriptions"])

class CreateJobRequest(BaseModel):
    title: str
    company: Optional[str] = "Tech Innovations Inc."
    raw_text: str
    min_yoe: Optional[float] = None
    must_have_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None

@router.post("", response_model=JobDescription)
async def create_job(payload: CreateJobRequest):
    raw_text = payload.raw_text

    # Extract skills if not provided
    found_skills = []
    lower_text = raw_text.lower()
    for s in COMMON_SKILLS:
        if re.search(r"\b" + re.escape(s) + r"\b", lower_text):
            found_skills.append(s.title())

    must_haves = payload.must_have_skills or found_skills[:6]
    preferred = payload.preferred_skills or found_skills[6:12]

    # Extract YoE if not provided
    yoe = payload.min_yoe
    if yoe is None:
        yoe_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s+(?:of\s+)?experience", raw_text, re.IGNORECASE)
        yoe = float(yoe_match.group(1)) if yoe_match else 3.0

    # Extract responsibilities from bullet points
    responsibilities = []
    for line in raw_text.splitlines():
        line_clean = line.strip()
        if line_clean.startswith(("-", "•", "*", "–")) and len(line_clean) > 20:
            responsibilities.append(line_clean.lstrip("-•*– "))

    job = JobDescription(
        job_id=str(uuid.uuid4())[:8],
        title=payload.title,
        company=payload.company or "Tech Innovations Inc.",
        raw_text=raw_text,
        min_yoe=yoe,
        must_have_skills=must_haves,
        preferred_skills=preferred,
        responsibilities=responsibilities[:8],
        education_requirements=["Bachelor's degree in Computer Science, Engineering, or equivalent practical experience."]
    )

    store.add_job(job)
    return job

@router.get("", response_model=List[JobDescription])
async def list_jobs():
    return store.list_jobs()

@router.get("/{job_id}", response_model=JobDescription)
async def get_job(job_id: str):
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/{job_id}")
async def delete_job(job_id: str):
    success = store.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "success", "message": f"Job {job_id} deleted"}
