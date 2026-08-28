from typing import List, Dict, Any, Optional
from app.index.store import store
from app.index.schema import PageIndexNode, CitationSpan, CandidateProfile

class PageIndexTools:
    @staticmethod
    def get_candidate_overview(candidate_id: str) -> Optional[Dict[str, Any]]:
        cand = store.get_candidate(candidate_id)
        if not cand or not cand.index_tree:
            return None
        return {
            "candidate_id": cand.candidate_id,
            "candidate_name": cand.candidate_name,
            "overall_yoe": cand.overall_yoe,
            "top_skills": cand.top_skills,
            "summary": cand.index_tree.summary,
            "sections_available": [sec.title for sec in cand.index_tree.children]
        }

    @staticmethod
    def inspect_section(candidate_id: str, section_keyword: str) -> Optional[Dict[str, Any]]:
        cand = store.get_candidate(candidate_id)
        if not cand or not cand.index_tree:
            return None

        kw = section_keyword.lower()
        target_sec = None
        for sec in cand.index_tree.children:
            if kw in sec.title.lower() or (sec.citation and kw in sec.citation.section_name.lower()):
                target_sec = sec
                break

        if not target_sec:
            return None

        entries_summary = []
        for entry in target_sec.children:
            entries_summary.append({
                "node_id": entry.node_id,
                "title": entry.title,
                "summary": entry.summary,
                "key_entities": entry.key_entities,
                "has_sub_entries": len(entry.children) > 0,
                "citation": entry.citation.model_dump() if entry.citation else None
            })

        return {
            "section_title": target_sec.title,
            "section_summary": target_sec.summary,
            "entries_count": len(target_sec.children),
            "entries": entries_summary
        }

    @staticmethod
    def inspect_node_deep(candidate_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        cand = store.get_candidate(candidate_id)
        if not cand or not cand.index_tree:
            return None

        # DFS search for node
        def find_node(curr: PageIndexNode) -> Optional[PageIndexNode]:
            if curr.node_id == node_id:
                return curr
            for child in curr.children:
                res = find_node(child)
                if res:
                    return res
            return None

        target = find_node(cand.index_tree)
        if not target:
            return None

        return {
            "node_id": target.node_id,
            "title": target.title,
            "summary": target.summary,
            "key_entities": target.key_entities,
            "citation": target.citation.model_dump() if target.citation else None,
            "sub_entries": [
                {
                    "node_id": sub.node_id,
                    "title": sub.title,
                    "summary": sub.summary,
                    "citation": sub.citation.model_dump() if sub.citation else None
                } for sub in target.children
            ]
        }

    @staticmethod
    def find_candidates_with_entity(entity: str) -> List[Dict[str, Any]]:
        matched = []
        e_lower = entity.lower()
        for cand in store.list_candidates():
            has_skill = any(e_lower in s.lower() for s in cand.top_skills)
            in_raw = e_lower in cand.raw_text.lower()
            if has_skill or in_raw:
                matched.append({
                    "candidate_id": cand.candidate_id,
                    "candidate_name": cand.candidate_name,
                    "overall_yoe": cand.overall_yoe,
                    "top_skills": cand.top_skills
                })
        return matched
