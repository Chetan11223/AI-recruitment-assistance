import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import UPLOADS_DIR
from app.parser.document_loader import DocumentLoader
from app.parser.tree_builder import PageIndexTreeBuilder
from app.index.store import store
from app.index.schema import CandidateProfile

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

@router.post("/upload", response_model=List[CandidateProfile])
async def upload_resumes(files: List[UploadFile] = File(...)):
    parsed_candidates = []
    for file in files:
        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            parsed_doc = DocumentLoader.load_file(str(file_path))
            candidate_profile = PageIndexTreeBuilder.build_tree(parsed_doc)
            store.add_candidate(candidate_profile)
            parsed_candidates.append(candidate_profile)
        except Exception as e:
            print(f"Error parsing file {file.filename}: {e}")
            # Clean up on failure
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail=f"Failed to parse {file.filename}: {str(e)}")

    return parsed_candidates

@router.get("", response_model=List[CandidateProfile])
async def list_resumes():
    return store.list_candidates()

@router.get("/{candidate_id}", response_model=CandidateProfile)
async def get_resume(candidate_id: str):
    cand = store.get_candidate(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return cand

@router.delete("/{candidate_id}")
async def delete_resume(candidate_id: str):
    success = store.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "success", "message": f"Candidate {candidate_id} deleted"}
