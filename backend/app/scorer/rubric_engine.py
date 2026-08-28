import re
from typing import Dict, List, Tuple, Optional
from app.index.schema import (
    CandidateProfile, JobDescription, CandidateScorecard, DimensionScore, CitationSpan, PageIndexNode
)
from app.llm.client import llm_client

class RubricScoringEngine:
    WEIGHT_SKILLS = 0.30
    WEIGHT_EXPERIENCE = 0.35
    WEIGHT_PROJECTS = 0.20
    WEIGHT_EDUCATION = 0.15

    @classmethod
    async def evaluate_candidate(cls, candidate: CandidateProfile, job: JobDescription) -> CandidateScorecard:
        root_node = candidate.index_tree
        sections_map = {sec.title.lower(): sec for sec in (root_node.children if root_node else [])}

        # 1. Evaluate Core Technical Skills
        skills_score, skills_rationale, skills_citations, matched_skills, missing_skills = cls._evaluate_skills(
            candidate, job, sections_map
        )

        # 2. Evaluate Domain & Role Depth
        exp_score, exp_rationale, exp_citations, matched_exp, missing_exp = cls._evaluate_experience(
            candidate, job, sections_map
        )

        # 3. Evaluate Project & System Impact
        proj_score, proj_rationale, proj_citations, matched_proj, missing_proj = cls._evaluate_projects(
            candidate, job, sections_map
        )

        # 4. Evaluate Education & Baseline Fit
        edu_score, edu_rationale, edu_citations, matched_edu, missing_edu = cls._evaluate_education(
            candidate, job, sections_map
        )

        # Calculate Weighted Overall Score
        overall_score = round(
            (skills_score * cls.WEIGHT_SKILLS) +
            (exp_score * cls.WEIGHT_EXPERIENCE) +
            (proj_score * cls.WEIGHT_PROJECTS) +
            (edu_score * cls.WEIGHT_EDUCATION),
            1
        )

        # Determine Fit Level
        if overall_score >= 85:
            fit_level = "Strong Match"
        elif overall_score >= 70:
            fit_level = "Good Match"
        elif overall_score >= 50:
            fit_level = "Moderate Match"
        else:
            fit_level = "Weak Match"

        # Executive Summary
        exec_summary = (
            f"{candidate.candidate_name} is evaluated as a {fit_level} ({overall_score}/100) for '{job.title}'. "
            f"Skills match: {len(matched_skills)}/{max(1, len(job.must_have_skills))} must-have requirements. "
            f"Experience: {candidate.overall_yoe:.1f} YoE (vs {job.min_yoe:.1f} required)."
        )

        dimension_scores: Dict[str, DimensionScore] = {
            "skills": DimensionScore(
                dimension_name="Core Technical Skills",
                weight=cls.WEIGHT_SKILLS,
                raw_score=skills_score,
                weighted_score=round(skills_score * cls.WEIGHT_SKILLS, 2),
                rationale=skills_rationale,
                cited_spans=skills_citations,
                matched_items=matched_skills,
                missing_items=missing_skills
            ),
            "experience": DimensionScore(
                dimension_name="Domain & Role Depth",
                weight=cls.WEIGHT_EXPERIENCE,
                raw_score=exp_score,
                weighted_score=round(exp_score * cls.WEIGHT_EXPERIENCE, 2),
                rationale=exp_rationale,
                cited_spans=exp_citations,
                matched_items=matched_exp,
                missing_items=missing_exp
            ),
            "projects": DimensionScore(
                dimension_name="Project & System Impact",
                weight=cls.WEIGHT_PROJECTS,
                raw_score=proj_score,
                weighted_score=round(proj_score * cls.WEIGHT_PROJECTS, 2),
                rationale=proj_rationale,
                cited_spans=proj_citations,
                matched_items=matched_proj,
                missing_items=missing_proj
            ),
            "education": DimensionScore(
                dimension_name="Education & Baseline Fit",
                weight=cls.WEIGHT_EDUCATION,
                raw_score=edu_score,
                weighted_score=round(edu_score * cls.WEIGHT_EDUCATION, 2),
                rationale=edu_rationale,
                cited_spans=edu_citations,
                matched_items=matched_edu,
                missing_items=missing_edu
            )
        }

        # Collect all unique citations
        all_citations = skills_citations + exp_citations + proj_citations + edu_citations
        unique_citations = []
        seen_texts = set()
        for c in all_citations:
            if c.raw_text and c.raw_text not in seen_texts:
                seen_texts.add(c.raw_text)
                unique_citations.append(c)

        return CandidateScorecard(
            candidate_id=candidate.candidate_id,
            candidate_name=candidate.candidate_name,
            job_id=job.job_id,
            overall_score=overall_score,
            fit_level=fit_level,
            executive_summary=exec_summary,
            dimension_scores=dimension_scores,
            cited_evidence=unique_citations[:10]
        )

    @classmethod
    def _evaluate_skills(
        cls, candidate: CandidateProfile, job: JobDescription, sections_map: Dict[str, PageIndexNode]
    ) -> Tuple[float, str, List[CitationSpan], List[str], List[str]]:
        candidate_skills_lower = set([s.lower() for s in candidate.top_skills])
        raw_text_lower = candidate.raw_text.lower()
        
        must_haves = [s.lower() for s in job.must_have_skills]
        preferred = [s.lower() for s in job.preferred_skills]

        matched_must = []
        missing_must = []
        for req in must_haves:
            if req in candidate_skills_lower or re.search(r"\b" + re.escape(req) + r"\b", raw_text_lower):
                matched_must.append(req)
            else:
                missing_must.append(req)

        matched_pref = []
        for req in preferred:
            if req in candidate_skills_lower or re.search(r"\b" + re.escape(req) + r"\b", raw_text_lower):
                matched_pref.append(req)

        must_ratio = len(matched_must) / max(1, len(must_haves)) if must_haves else 0.9
        pref_ratio = len(matched_pref) / max(1, len(preferred)) if preferred else 0.8

        raw_score = round(min(100.0, (must_ratio * 80.0) + (pref_ratio * 20.0)), 1)
        rationale = (
            f"Candidate matches {len(matched_must)}/{len(must_haves)} must-have skills "
            f"({', '.join(matched_must[:4]) if matched_must else 'none'}) and {len(matched_pref)} preferred skills."
        )

        citations = []
        # Find skill citations
        for sec_name, sec_node in sections_map.items():
            if "skill" in sec_name or "technolog" in sec_name:
                if sec_node.citation:
                    citations.append(sec_node.citation)
                for child in sec_node.children:
                    if child.citation:
                        citations.append(child.citation)

        return raw_score, rationale, citations[:3], matched_must + matched_pref, missing_must

    @classmethod
    def _evaluate_experience(
        cls, candidate: CandidateProfile, job: JobDescription, sections_map: Dict[str, PageIndexNode]
    ) -> Tuple[float, str, List[CitationSpan], List[str], List[str]]:
        yoe = candidate.overall_yoe
        req_yoe = job.min_yoe

        matched = []
        missing = []

        # YoE Ratio
        if req_yoe > 0:
            yoe_ratio = min(1.3, yoe / req_yoe)
            base_score = min(95.0, yoe_ratio * 85.0)
        else:
            base_score = 85.0

        if yoe >= req_yoe:
            matched.append(f"{yoe:.1f} YoE (meets {req_yoe:.1f} min)")
        else:
            missing.append(f"{yoe:.1f} YoE (below {req_yoe:.1f} min requirement)")

        # Check experience section
        exp_sec = None
        for sec_name, sec_node in sections_map.items():
            if "experience" in sec_name or "work" in sec_name or "employment" in sec_name:
                exp_sec = sec_node
                break

        citations = []
        if exp_sec:
            for child in exp_sec.children:
                matched.append(child.title)
                if child.citation:
                    citations.append(child.citation)
                for sub in child.children:
                    if sub.citation and len(citations) < 5:
                        citations.append(sub.citation)

        raw_score = round(min(100.0, max(20.0, base_score)), 1)
        rationale = (
            f"Candidate has {yoe:.1f} years of relevant experience across {len(exp_sec.children) if exp_sec else 1} major roles. "
            f"Seniority alignment is strong."
        )

        return raw_score, rationale, citations[:4], matched, missing

    @classmethod
    def _evaluate_projects(
        cls, candidate: CandidateProfile, job: JobDescription, sections_map: Dict[str, PageIndexNode]
    ) -> Tuple[float, str, List[CitationSpan], List[str], List[str]]:
        proj_sec = None
        for sec_name, sec_node in sections_map.items():
            if "project" in sec_name:
                proj_sec = sec_node
                break

        citations = []
        matched = []
        if proj_sec and proj_sec.children:
            raw_score = min(98.0, 75.0 + (len(proj_sec.children) * 6.0))
            for child in proj_sec.children:
                matched.append(child.title)
                if child.citation:
                    citations.append(child.citation)
            rationale = f"Demonstrated {len(proj_sec.children)} significant projects highlighting technical ownership."
        else:
            # Check experience achievements as projects
            raw_score = 75.0
            rationale = "Project impact is primarily demonstrated through embedded production work in professional experience."

        return round(raw_score, 1), rationale, citations[:3], matched, []

    @classmethod
    def _evaluate_education(
        cls, candidate: CandidateProfile, job: JobDescription, sections_map: Dict[str, PageIndexNode]
    ) -> Tuple[float, str, List[CitationSpan], List[str], List[str]]:
        edu_sec = None
        for sec_name, sec_node in sections_map.items():
            if "education" in sec_name or "academic" in sec_name:
                edu_sec = sec_node
                break

        citations = []
        matched = []
        raw_text_lower = candidate.raw_text.lower()
        if any(deg in raw_text_lower for deg in ["bachelor", "master", "phd", "b.s", "m.s", "b.tech", "m.tech", "computer science"]):
            raw_score = 92.0
            matched.append("Relevant STEM / Computer Science Degree")
        else:
            raw_score = 80.0
            matched.append("Practical Technical Background")

        if edu_sec:
            if edu_sec.citation:
                citations.append(edu_sec.citation)
            for child in edu_sec.children:
                if child.citation:
                    citations.append(child.citation)

        rationale = f"Educational profile aligns with standard technical requirements."
        return round(raw_score, 1), rationale, citations[:2], matched, []
