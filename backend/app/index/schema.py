from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
import uuid
import time

class CitationSpan(BaseModel):
    page_number: int = 1
    char_start: int = 0
    char_end: int = 0
    raw_text: str = ""
    section_name: str = ""

class PageIndexNode(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_type: Literal["document", "section", "entry", "sub_entry"] = "entry"
    title: str
    summary: str = Field(description="Dense semantic summary for tree pruning and reasoning")
    key_entities: List[str] = Field(default_factory=list, description="Skills, tools, metrics, dates, companies")
    citation: Optional[CitationSpan] = None
    children: List["PageIndexNode"] = Field(default_factory=list)

class CandidateProfile(BaseModel):
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    candidate_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    file_name: str
    file_type: str
    upload_timestamp: float = Field(default_factory=time.time)
    overall_yoe: float = 0.0
    top_skills: List[str] = Field(default_factory=list)
    raw_text: str = ""
    index_tree: Optional[PageIndexNode] = None

class JobRequirementItem(BaseModel):
    skill_or_requirement: str
    importance: Literal["must_have", "preferred", "bonus"] = "must_have"
    category: Literal["skills", "experience", "education", "domain"] = "skills"

class JobDescription(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    company: Optional[str] = "Tech Innovations Inc."
    raw_text: str
    min_yoe: float = 0.0
    must_have_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

class DimensionScore(BaseModel):
    dimension_name: str
    weight: float
    raw_score: float = Field(ge=0, le=100, description="Score 0 to 100")
    weighted_score: float = 0.0
    rationale: str
    cited_spans: List[CitationSpan] = Field(default_factory=list)
    matched_items: List[str] = Field(default_factory=list)
    missing_items: List[str] = Field(default_factory=list)

class CandidateScorecard(BaseModel):
    candidate_id: str
    candidate_name: str
    job_id: str
    overall_score: float = Field(ge=0, le=100)
    fit_level: Literal["Strong Match", "Good Match", "Moderate Match", "Weak Match"]
    executive_summary: str
    dimension_scores: Dict[str, DimensionScore]
    cited_evidence: List[CitationSpan] = Field(default_factory=list)
    evaluated_at: float = Field(default_factory=time.time)

class CandidateRankItem(BaseModel):
    rank: int
    candidate_id: str
    candidate_name: str
    overall_score: float
    fit_level: str
    skills_score: float
    experience_score: float
    projects_score: float
    education_score: float
    key_strengths: List[str] = Field(default_factory=list)
    concerns_or_gaps: List[str] = Field(default_factory=list)
    comparative_notes: str

class RankingResult(BaseModel):
    job_id: str
    job_title: str
    evaluated_candidates_count: int
    leaderboard: List[CandidateRankItem]
    synthesis_summary: str
    generated_at: float = Field(default_factory=time.time)

class TraversalTraceStep(BaseModel):
    step_num: int
    action: str
    candidate_id: Optional[str] = None
    node_id: Optional[str] = None
    node_title: Optional[str] = None
    reasoning: str
    evidence_gathered: Optional[str] = None

class AgentQueryRequest(BaseModel):
    query: str
    job_id: Optional[str] = None
    candidate_ids: Optional[List[str]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class AgentQueryResponse(BaseModel):
    answer: str
    traversal_steps: List[TraversalTraceStep] = Field(default_factory=list)
    cited_evidence: List[CitationSpan] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)
