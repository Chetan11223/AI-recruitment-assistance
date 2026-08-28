import pytest
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.parser.document_loader import ParsedDocument, DocumentPage
from app.parser.segmenter import SectionSegmenter
from app.parser.tree_builder import PageIndexTreeBuilder
from app.scorer.rubric_engine import RubricScoringEngine
from app.agent.orchestrator import AgentOrchestrator
from app.index.store import store
from app.index.schema import JobDescription, AgentQueryRequest
from app.sample_data.generator import SAMPLE_RESUMES, SAMPLE_JOBS, SampleDataLoader

@pytest.fixture(autouse=True)
def setup_store():
    SampleDataLoader.load_all_samples()

def test_document_loader_and_segmenter():
    sample_text = SAMPLE_RESUMES[0]["text"]
    sections = SectionSegmenter.segment(sample_text)
    assert len(sections) >= 3
    section_names = [s.normalized_name for s in sections]
    assert "experience" in section_names
    assert "skills" in section_names

def test_pageindex_tree_builder():
    sample_text = SAMPLE_RESUMES[0]["text"]
    pages = [DocumentPage(page_number=1, text=sample_text, char_start_offset=0)]
    parsed_doc = ParsedDocument(
        file_name="alex_test.txt",
        file_type="txt",
        full_text=sample_text,
        pages=pages
    )
    profile = PageIndexTreeBuilder.build_tree(parsed_doc)
    assert profile.candidate_name == "Alex Rivera"
    assert profile.overall_yoe >= 7.0
    assert "golang" in [s.lower() for s in profile.top_skills] or "rust" in [s.lower() for s in profile.top_skills]
    
    # Check tree hierarchy
    root = profile.index_tree
    assert root is not None
    assert root.node_type == "document"
    assert len(root.children) >= 3
    
    # Check experience section
    exp_sec = next((c for c in root.children if "experience" in c.title.lower()), None)
    assert exp_sec is not None
    assert len(exp_sec.children) >= 2
    assert exp_sec.citation is not None

@pytest.mark.asyncio
async def test_rubric_scoring_engine():
    candidates = store.list_candidates()
    jobs = store.list_jobs()
    assert len(candidates) > 0
    assert len(jobs) > 0

    alex = next((c for c in candidates if "Alex" in c.candidate_name), candidates[0])
    backend_job = next((j for j in jobs if "Backend" in j.title), jobs[0])

    scorecard = await RubricScoringEngine.evaluate_candidate(alex, backend_job)
    assert scorecard.overall_score >= 70.0
    assert scorecard.fit_level in ["Strong Match", "Good Match"]
    assert "skills" in scorecard.dimension_scores
    assert "experience" in scorecard.dimension_scores
    assert len(scorecard.cited_evidence) > 0

@pytest.mark.asyncio
async def test_agent_orchestrator_ranking_and_query():
    jobs = store.list_jobs()
    backend_job = next((j for j in jobs if "Backend" in j.title), jobs[0])

    # Test ranking
    ranking = await AgentOrchestrator.rank_candidates_for_job(backend_job.job_id)
    assert ranking.evaluated_candidates_count >= 3
    assert len(ranking.leaderboard) >= 3
    assert ranking.leaderboard[0].rank == 1
    assert ranking.leaderboard[0].overall_score >= ranking.leaderboard[1].overall_score

    # Test conversational query
    query_req = AgentQueryRequest(
        query="Who has the most experience with Kafka and distributed caching?",
        job_id=backend_job.job_id
    )
    resp = await AgentOrchestrator.answer_recruiter_query(query_req)
    assert resp.answer != ""
    assert len(resp.traversal_steps) >= 2
    assert len(resp.cited_evidence) > 0
