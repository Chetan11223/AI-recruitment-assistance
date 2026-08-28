from fastapi import APIRouter, HTTPException
from app.index.store import store
from app.index.schema import (
    AgentQueryRequest, AgentQueryResponse, RankingResult, CandidateScorecard
)
from app.agent.orchestrator import AgentOrchestrator
from app.scorer.rubric_engine import RubricScoringEngine

router = APIRouter(prefix="/api/agent", tags=["Agentic RAG"])

@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(request: AgentQueryRequest):
    try:
        response = await AgentOrchestrator.answer_recruiter_query(request)
        return response
    except Exception as e:
        print(f"Error in query_agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rank/{job_id}", response_model=RankingResult)
async def rank_candidates_against_job(job_id: str):
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        result = await AgentOrchestrator.rank_candidates_for_job(job_id)
        return result
    except Exception as e:
        print(f"Error in rank_candidates_against_job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ranking/{job_id}", response_model=RankingResult)
async def get_ranking(job_id: str):
    ranking = store.get_ranking(job_id)
    if not ranking:
        # Run ranking if not previously cached
        job = store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        ranking = await AgentOrchestrator.rank_candidates_for_job(job_id)
    return ranking

@router.get("/scorecard/{candidate_id}/{job_id}", response_model=CandidateScorecard)
async def get_candidate_scorecard(candidate_id: str, job_id: str):
    cand = store.get_candidate(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    scorecard = store.get_scorecard(candidate_id, job_id)
    if not scorecard:
        scorecard = await RubricScoringEngine.evaluate_candidate(cand, job)
        store.save_scorecard(scorecard)

    return scorecard
