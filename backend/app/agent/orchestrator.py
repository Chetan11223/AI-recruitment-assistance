import json
import re
from typing import List, Dict, Any, Optional
from app.index.store import store
from app.index.schema import (
    AgentQueryRequest, AgentQueryResponse, TraversalTraceStep, CitationSpan,
    RankingResult, CandidateRankItem, CandidateScorecard, CandidateProfile
)
from app.scorer.rubric_engine import RubricScoringEngine
from app.agent.tools import PageIndexTools
from app.llm.client import llm_client

class AgentOrchestrator:
    @classmethod
    async def rank_candidates_for_job(cls, job_id: str) -> RankingResult:
        job = store.get_job(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        candidates = store.list_candidates()
        if not candidates:
            return RankingResult(
                job_id=job.job_id,
                job_title=job.title,
                evaluated_candidates_count=0,
                leaderboard=[],
                synthesis_summary="No candidates found in repository. Please upload candidate resumes."
            )

        scorecards: List[CandidateScorecard] = []
        for cand in candidates:
            scorecard = await RubricScoringEngine.evaluate_candidate(cand, job)
            store.save_scorecard(scorecard)
            scorecards.append(scorecard)

        # Sort by overall score descending
        scorecards.sort(key=lambda s: s.overall_score, reverse=True)

        leaderboard_items: List[CandidateRankItem] = []
        for rank_idx, sc in enumerate(scorecards, 1):
            cand = store.get_candidate(sc.candidate_id)
            skills_sc = sc.dimension_scores.get("skills")
            exp_sc = sc.dimension_scores.get("experience")
            proj_sc = sc.dimension_scores.get("projects")
            edu_sc = sc.dimension_scores.get("education")

            strengths = (skills_sc.matched_items[:3] if skills_sc else []) + (exp_sc.matched_items[:2] if exp_sc else [])
            concerns = (skills_sc.missing_items[:3] if skills_sc else []) + (exp_sc.missing_items[:1] if exp_sc else [])

            comp_notes = f"Rank #{rank_idx}: {sc.fit_level} ({sc.overall_score}/100). "
            if rank_idx == 1:
                comp_notes += "Top candidate with the strongest overall alignment across technical skills and role experience."
            else:
                top_sc = scorecards[0]
                diff = top_sc.overall_score - sc.overall_score
                comp_notes += f"Trails rank #1 by {diff:.1f} pts primarily due to {concerns[0] if concerns else 'experience depth'}."

            leaderboard_items.append(CandidateRankItem(
                rank=rank_idx,
                candidate_id=sc.candidate_id,
                candidate_name=sc.candidate_name,
                overall_score=sc.overall_score,
                fit_level=sc.fit_level,
                skills_score=skills_sc.raw_score if skills_sc else 0.0,
                experience_score=exp_sc.raw_score if exp_sc else 0.0,
                projects_score=proj_sc.raw_score if proj_sc else 0.0,
                education_score=edu_sc.raw_score if edu_sc else 0.0,
                key_strengths=strengths,
                concerns_or_gaps=concerns,
                comparative_notes=comp_notes
            ))

        synthesis = (
            f"Evaluated {len(scorecards)} candidate(s) for the role '{job.title}'. "
            f"Top ranked candidate is {leaderboard_items[0].candidate_name} ({leaderboard_items[0].overall_score}/100) "
            f"followed by {leaderboard_items[1].candidate_name if len(leaderboard_items) > 1 else 'N/A'}."
        )

        ranking_result = RankingResult(
            job_id=job.job_id,
            job_title=job.title,
            evaluated_candidates_count=len(scorecards),
            leaderboard=leaderboard_items,
            synthesis_summary=synthesis
        )
        store.save_ranking(ranking_result)
        return ranking_result

    @classmethod
    async def answer_recruiter_query(cls, request: AgentQueryRequest) -> AgentQueryResponse:
        query = request.query.strip()
        candidates = store.list_candidates()
        job = store.get_job(request.job_id) if request.job_id else None

        steps: List[TraversalTraceStep] = []
        citations: List[CitationSpan] = []

        # Step 1: Query Intent Analysis & Plan
        steps.append(TraversalTraceStep(
            step_num=1,
            action="Deconstruct Query & Identify Target Entities",
            reasoning=f"Analyzing recruiter query: '{query}'. Determining whether this is a single candidate inspection, a cross-candidate comparison, a skill lookup, or a general ranking request."
        ))

        # Check for specific candidate mentions
        targeted_candidates = []
        if request.candidate_ids:
            for cid in request.candidate_ids:
                c = store.get_candidate(cid)
                if c:
                    targeted_candidates.append(c)

        if not targeted_candidates:
            for c in candidates:
                if c.candidate_name.lower() in query.lower() or c.candidate_id in query.lower():
                    targeted_candidates.append(c)

        # Comparative query detection
        is_comparison = any(w in query.lower() for w in ["compare", "versus", "vs", "who is better", "difference"])
        is_ranking = any(w in query.lower() for w in ["rank", "leaderboard", "best candidate", "top candidate", "score"])

        if is_comparison and len(targeted_candidates) >= 2:
            return await cls._handle_comparison_query(targeted_candidates[:3], query, job, steps)

        if is_ranking and job:
            return await cls._handle_ranking_query(job, query, steps)

        # If targeting specific candidate(s)
        if targeted_candidates:
            return await cls._handle_candidate_deep_dive(targeted_candidates[0], query, job, steps)

        # Keyword / Skill / Concept Search across candidate tree
        return await cls._handle_skill_or_concept_search(query, job, candidates, steps)

    @classmethod
    async def _handle_comparison_query(
        cls, candidates: List[Any], query: str, job: Optional[Any], steps: List[TraversalTraceStep]
    ) -> AgentQueryResponse:
        steps.append(TraversalTraceStep(
            step_num=2,
            action="PageIndex Cross-Tree Comparison",
            reasoning=f"Comparing {len(candidates)} candidates: {', '.join([c.candidate_name for c in candidates])}. Navigating respective Experience and Projects nodes."
        ))

        citations: List[CitationSpan] = []
        comparison_points = []

        for cand in candidates:
            # Inspect experience and projects
            exp_info = PageIndexTools.inspect_section(cand.candidate_id, "experience")
            proj_info = PageIndexTools.inspect_section(cand.candidate_id, "projects")

            cand_summary = f"**{cand.candidate_name}** ({cand.overall_yoe:.1f} YoE):\n"
            cand_summary += f"- Key Skills: {', '.join(cand.top_skills[:8])}\n"
            if exp_info and exp_info["entries"]:
                cand_summary += f"- Roles: {', '.join([e['title'] for e in exp_info['entries'][:2]])}\n"
                for e in exp_info["entries"][:2]:
                    if e.get("citation"):
                        citations.append(CitationSpan.model_validate(e["citation"]))

            if proj_info and proj_info["entries"]:
                cand_summary += f"- Key Projects: {', '.join([p['title'] for p in proj_info['entries'][:2]])}\n"

            comparison_points.append(cand_summary)

        answer = (
            f"### Comparative Evaluation for: *'{query}'*\n\n"
            + "\n".join(comparison_points)
            + "\n\n**Agent Synthesis:**\n"
            f"- **Experience & Seniority:** {candidates[0].candidate_name} has {candidates[0].overall_yoe:.1f} YoE vs {candidates[1].candidate_name} with {candidates[1].overall_yoe:.1f} YoE.\n"
            f"- **Technical Alignment:** Both candidates demonstrate relevant capabilities, but their exact focus areas differ across systems architecture and tooling.\n"
            f"See the cited resume sections below for line-by-line verification."
        )

        return AgentQueryResponse(
            answer=answer,
            traversal_steps=steps,
            cited_evidence=citations[:6],
            suggested_followups=[
                f"What are the main risks with {candidates[0].candidate_name}?",
                f"How do their project impacts compare?",
                "Give me a side-by-side scorecard breakdown"
            ]
        )

    @classmethod
    async def _handle_ranking_query(
        cls, job: Any, query: str, steps: List[TraversalTraceStep]
    ) -> AgentQueryResponse:
        steps.append(TraversalTraceStep(
            step_num=2,
            action="Executing Grounded Rubric Evaluation for All Candidates",
            reasoning=f"Evaluating candidate pool against Job Description '{job.title}' across Skills (30%), Experience (35%), Projects (20%), and Education (15%)."
        ))

        ranking = await cls.rank_candidates_for_job(job.job_id)
        citations: List[CitationSpan] = []

        leaderboard_md = ["| Rank | Candidate | Fit Level | Overall Score | Skills | Exp | YoE |", "| :---: | :--- | :---: | :---: | :---: | :---: | :---: |"]
        for item in ranking.leaderboard:
            cand = store.get_candidate(item.candidate_id)
            yoe = f"{cand.overall_yoe:.1f}y" if cand else "-"
            leaderboard_md.append(f"| #{item.rank} | **{item.candidate_name}** | `{item.fit_level}` | **{item.overall_score}%** | {item.skills_score:.0f}% | {item.experience_score:.0f}% | {yoe} |")

        # Collect top candidate citations
        if ranking.leaderboard:
            top_cand_id = ranking.leaderboard[0].candidate_id
            sc = store.get_scorecard(top_cand_id, job.job_id)
            if sc:
                citations.extend(sc.cited_evidence[:4])

        answer = (
            f"### Candidate Ranking Leaderboard for **{job.title}**\n\n"
            + "\n".join(leaderboard_md)
            + f"\n\n**Executive Synthesis:** {ranking.synthesis_summary}\n\n"
            "You can click on any candidate to inspect their grounded scorecard breakdown and verified resume citations."
        )

        return AgentQueryResponse(
            answer=answer,
            traversal_steps=steps,
            cited_evidence=citations,
            suggested_followups=[
                f"Why is {ranking.leaderboard[0].candidate_name} ranked #1?" if ranking.leaderboard else "Rank all candidates",
                "Compare the top 2 candidates side-by-side",
                "Show candidates with specific framework experience"
            ]
        )

    @classmethod
    async def _handle_candidate_deep_dive(
        cls, candidate: CandidateProfile, query: str, job: Optional[Any], steps: List[TraversalTraceStep]
    ) -> AgentQueryResponse:
        steps.append(TraversalTraceStep(
            step_num=2,
            action="Targeted Node Inspection",
            candidate_id=candidate.candidate_id,
            reasoning=f"Navigating PageIndex tree for {candidate.candidate_name}. Checking Experience, Projects, and Skills nodes."
        ))

        citations: List[CitationSpan] = []
        root = candidate.index_tree
        if root:
            for sec in root.children:
                if sec.citation:
                    citations.append(sec.citation)
                for child in sec.children:
                    if child.citation and len(citations) < 5:
                        citations.append(child.citation)

        answer = (
            f"### Profile Analysis: **{candidate.candidate_name}**\n\n"
            f"- **Overall Experience:** {candidate.overall_yoe:.1f} years\n"
            f"- **Core Skills:** {', '.join(candidate.top_skills)}\n"
            f"- **Executive Summary:** {candidate.index_tree.summary if candidate.index_tree else 'Active candidate profile.'}\n\n"
            f"**Evidence Breakdown from PageIndex:**\n"
        )

        if candidate.index_tree:
            for sec in candidate.index_tree.children:
                answer += f"\n#### {sec.title}\n{sec.summary}\n"
                for entry in sec.children[:3]:
                    answer += f"- **{entry.title}**: {entry.summary}\n"

        return AgentQueryResponse(
            answer=answer,
            traversal_steps=steps,
            cited_evidence=citations[:5],
            suggested_followups=[
                f"How does {candidate.candidate_name} compare to other candidates?",
                f"Score {candidate.candidate_name} against the active JD",
                "What are the top projects built by this candidate?"
            ]
        )

    @classmethod
    async def _handle_skill_or_concept_search(
        cls, query: str, job: Optional[Any], candidates: List[CandidateProfile], steps: List[TraversalTraceStep]
    ) -> AgentQueryResponse:
        # Extract keywords
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9+#.-]+\b", query) if len(w) > 2 and w.lower() not in ["who", "what", "which", "has", "the", "most", "with", "experience", "candidate", "candidates"]]
        
        steps.append(TraversalTraceStep(
            step_num=2,
            action="Vectorless Multi-Tree Keyword & Entity Scan",
            reasoning=f"Scanning PageIndex trees of {len(candidates)} candidate(s) for concept keywords: {', '.join(words[:4])}."
        ))

        matches = []
        citations = []

        for cand in candidates:
            score = 0
            matched_snippets = []
            if cand.index_tree:
                for sec in cand.index_tree.children:
                    for entry in sec.children:
                        entry_text = f"{entry.title} {entry.summary}".lower()
                        for w in words:
                            if w in entry_text or w in [e.lower() for e in entry.key_entities]:
                                score += 1
                                matched_snippets.append(f"{sec.title} → {entry.title}")
                                if entry.citation:
                                    citations.append(entry.citation)

            if score > 0 or any(w in cand.raw_text.lower() for w in words):
                matches.append((cand, score, matched_snippets))

        matches.sort(key=lambda m: (m[1], m[0].overall_yoe), reverse=True)

        if not matches:
            return AgentQueryResponse(
                answer=f"No candidates directly matched the specific criteria in query: '{query}'. Try asking about general roles, languages, or comparing candidates.",
                traversal_steps=steps,
                cited_evidence=[],
                suggested_followups=["Rank all candidates against the JD", "Who has the most overall experience?"]
            )

        answer = f"### Candidates Matching Criteria: *'{query}'*\n\n"
        for cand, score, snippets in matches:
            answer += f"#### 👤 **{cand.candidate_name}** ({cand.overall_yoe:.1f} YoE)\n"
            answer += f"- **Relevant Skills:** {', '.join(cand.top_skills[:8])}\n"
            if snippets:
                answer += f"- **Matched PageIndex Nodes:** {'; '.join(snippets[:3])}\n"
            answer += "\n"

        return AgentQueryResponse(
            answer=answer,
            traversal_steps=steps,
            cited_evidence=citations[:5],
            suggested_followups=[
                f"Compare {matches[0][0].candidate_name} and {matches[1][0].candidate_name}" if len(matches) > 1 else "Rank all candidates against JD",
                f"Show detailed scorecard for {matches[0][0].candidate_name}",
                "Who has more leadership experience?"
            ]
        )
