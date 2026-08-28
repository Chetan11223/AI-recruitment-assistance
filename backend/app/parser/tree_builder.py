import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from app.index.schema import PageIndexNode, CitationSpan, CandidateProfile
from app.parser.document_loader import ParsedDocument
from app.parser.segmenter import SectionSegmenter, RawSection

COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "golang", "go", "rust", "c#", "ruby", "php", "swift", "kotlin",
    "react", "next.js", "vue", "angular", "node.js", "express", "fastapi", "django", "flask", "spring boot",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "sqlite",
    "aws", "gcp", "azure", "kubernetes", "docker", "terraform", "ci/cd", "kafka", "rabbitmq", "graphql", "rest", "grpc",
    "pytorch", "tensorflow", "scikit-learn", "huggingface", "llms", "rag", "langchain", "llamaindex", "pandas", "numpy",
    "spark", "hadoop", "airflow", "snowflake", "dbt", "databricks", "git", "linux", "distributed systems", "microservices"
}

class PageIndexTreeBuilder:
    @classmethod
    def build_tree(cls, parsed_doc: ParsedDocument, candidate_id: Optional[str] = None) -> CandidateProfile:
        cand_id = candidate_id or str(uuid.uuid4())[:8]
        raw_text = parsed_doc.full_text
        sections = SectionSegmenter.segment(raw_text)

        # Extract Candidate Name & Contact info
        candidate_name, email, phone = cls._extract_candidate_identity(raw_text, sections, parsed_doc.file_name)

        # Build Section & Entry nodes
        section_nodes: List[PageIndexNode] = []
        all_extracted_skills = set()
        total_calculated_yoe = 0.0

        for raw_sec in sections:
            sec_node = cls._build_section_node(raw_sec, parsed_doc)
            section_nodes.append(sec_node)
            all_extracted_skills.update([e.lower() for e in sec_node.key_entities])

            if raw_sec.normalized_name == "experience":
                total_calculated_yoe += cls._estimate_experience_years(raw_sec.raw_text)

        if total_calculated_yoe == 0.0:
            total_calculated_yoe = cls._estimate_experience_years(raw_text)

        # Build Top-Level Document Node
        top_skills_list = sorted(list(all_extracted_skills))[:15]
        doc_summary = (
            f"Candidate profile for {candidate_name} with approximately {total_calculated_yoe:.1f} years of experience. "
            f"Key strengths: {', '.join(top_skills_list[:8]) if top_skills_list else 'Technical software engineering'}."
        )

        root_node = PageIndexNode(
            node_id=f"doc_{cand_id}",
            node_type="document",
            title=f"Resume: {candidate_name}",
            summary=doc_summary,
            key_entities=top_skills_list,
            citation=CitationSpan(page_number=1, char_start=0, char_end=min(500, len(raw_text)), raw_text=raw_text[:300], section_name="Root"),
            children=section_nodes
        )

        return CandidateProfile(
            candidate_id=cand_id,
            candidate_name=candidate_name,
            contact_email=email,
            contact_phone=phone,
            file_name=parsed_doc.file_name,
            file_type=parsed_doc.file_type,
            overall_yoe=round(total_calculated_yoe, 1),
            top_skills=top_skills_list,
            raw_text=raw_text,
            index_tree=root_node
        )

    @classmethod
    def _build_section_node(cls, raw_sec: RawSection, parsed_doc: ParsedDocument) -> PageIndexNode:
        sec_id = f"sec_{raw_sec.normalized_name}_{uuid.uuid4().hex[:6]}"
        sec_text = raw_sec.raw_text
        entities = cls._extract_entities_from_text(sec_text)

        entry_nodes = []
        if raw_sec.normalized_name == "experience":
            entry_nodes = cls._parse_experience_entries(raw_sec, parsed_doc)
        elif raw_sec.normalized_name == "projects":
            entry_nodes = cls._parse_project_entries(raw_sec, parsed_doc)
        elif raw_sec.normalized_name == "education":
            entry_nodes = cls._parse_education_entries(raw_sec, parsed_doc)
        elif raw_sec.normalized_name == "skills":
            entry_nodes = cls._parse_skills_entries(raw_sec, parsed_doc)
        else:
            entry_nodes = cls._parse_generic_entries(raw_sec, parsed_doc)

        sec_summary = cls._generate_section_summary(raw_sec.normalized_name, sec_text, entry_nodes, entities)

        cit_info = parsed_doc.get_citation_span(raw_sec.raw_text[:200], start_hint=raw_sec.char_start)

        return PageIndexNode(
            node_id=sec_id,
            node_type="section",
            title=raw_sec.section_name.title(),
            summary=sec_summary,
            key_entities=entities,
            citation=CitationSpan(
                page_number=cit_info["page_number"],
                char_start=raw_sec.char_start,
                char_end=raw_sec.char_end,
                raw_text=raw_sec.raw_text[:300],
                section_name=raw_sec.normalized_name
            ),
            children=entry_nodes
        )

    @classmethod
    def _parse_experience_entries(cls, raw_sec: RawSection, parsed_doc: ParsedDocument) -> List[PageIndexNode]:
        entries: List[PageIndexNode] = []
        lines = [line.strip() for line in raw_sec.raw_text.splitlines() if line.strip()]

        # Detect job blocks by date patterns or role patterns
        current_title = ""
        current_lines = []
        current_start_idx = raw_sec.char_start

        date_regex = re.compile(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*20\d\d\s*[-–—to]+\s*(?:Present|Current|20\d\d|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?",
            re.IGNORECASE
        )

        for line in lines[1:]:  # skip heading
            is_job_header = bool(date_regex.search(line)) or any(role in line.lower() for role in ["engineer", "developer", "architect", "manager", "lead", "specialist", "scientist", "intern", "consultant"]) and len(line) < 90

            if is_job_header and current_lines:
                entry = cls._create_job_entry_node(current_title, current_lines, raw_sec, parsed_doc)
                if entry:
                    entries.append(entry)
                current_title = line
                current_lines = []
            else:
                if not current_title and is_job_header:
                    current_title = line
                else:
                    current_lines.append(line)

        if current_title or current_lines:
            entry = cls._create_job_entry_node(current_title or "Role & Responsibilities", current_lines, raw_sec, parsed_doc)
            if entry:
                entries.append(entry)

        return entries

    @classmethod
    def _create_job_entry_node(cls, title: str, lines: List[str], raw_sec: RawSection, parsed_doc: ParsedDocument) -> Optional[PageIndexNode]:
        full_entry_text = f"{title}\n" + "\n".join(lines)
        if not full_entry_text.strip():
            return None

        entities = cls._extract_entities_from_text(full_entry_text)
        cit_info = parsed_doc.get_citation_span(full_entry_text[:200])

        # Sub-entry bullet nodes
        sub_entries = []
        for line in lines:
            if line.startswith(("-", "•", "*", "–")) or len(line) > 30:
                sub_cit = parsed_doc.get_citation_span(line)
                sub_entities = cls._extract_entities_from_text(line)
                sub_entries.append(PageIndexNode(
                    node_id=f"sub_{uuid.uuid4().hex[:6]}",
                    node_type="sub_entry",
                    title="Key Contribution / Achievement",
                    summary=line,
                    key_entities=sub_entities,
                    citation=CitationSpan(
                        page_number=sub_cit["page_number"],
                        char_start=sub_cit["char_start"],
                        char_end=sub_cit["char_end"],
                        raw_text=line,
                        section_name="experience"
                    ),
                    children=[]
                ))

        summary = f"Experience role: {title}. Focus on: {', '.join(entities[:5]) if entities else 'software development'}."

        return PageIndexNode(
            node_id=f"exp_{uuid.uuid4().hex[:6]}",
            node_type="entry",
            title=title if len(title) < 100 else title[:97] + "...",
            summary=summary,
            key_entities=entities,
            citation=CitationSpan(
                page_number=cit_info["page_number"],
                char_start=cit_info["char_start"],
                char_end=cit_info["char_end"],
                raw_text=full_entry_text[:400],
                section_name="experience"
            ),
            children=sub_entries
        )

    @classmethod
    def _parse_project_entries(cls, raw_sec: RawSection, parsed_doc: ParsedDocument) -> List[PageIndexNode]:
        entries: List[PageIndexNode] = []
        lines = [l.strip() for l in raw_sec.raw_text.splitlines() if l.strip()]
        
        current_proj_title = ""
        current_proj_lines = []

        for line in lines[1:]:
            if (len(line) < 80 and not line.startswith(("-", "•", "*", "–")) and any(c in line for c in ["|", ":", "-", "–", "("])) or not current_proj_title:
                if current_proj_title and current_proj_lines:
                    entries.append(cls._create_project_entry_node(current_proj_title, current_proj_lines, parsed_doc))
                    current_proj_lines = []
                current_proj_title = line
            else:
                current_proj_lines.append(line)

        if current_proj_title or current_proj_lines:
            entries.append(cls._create_project_entry_node(current_proj_title or "Project", current_proj_lines, parsed_doc))

        return [e for e in entries if e]

    @classmethod
    def _create_project_entry_node(cls, title: str, lines: List[str], parsed_doc: ParsedDocument) -> PageIndexNode:
        full_text = f"{title}\n" + "\n".join(lines)
        entities = cls._extract_entities_from_text(full_text)
        cit_info = parsed_doc.get_citation_span(full_text[:200])

        return PageIndexNode(
            node_id=f"proj_{uuid.uuid4().hex[:6]}",
            node_type="entry",
            title=title[:80],
            summary=f"Project details: {title}. Technologies: {', '.join(entities[:5])}.",
            key_entities=entities,
            citation=CitationSpan(
                page_number=cit_info["page_number"],
                char_start=cit_info["char_start"],
                char_end=cit_info["char_end"],
                raw_text=full_text[:350],
                section_name="projects"
            ),
            children=[]
        )

    @classmethod
    def _parse_education_entries(cls, raw_sec: RawSection, parsed_doc: ParsedDocument) -> List[PageIndexNode]:
        entries = []
        lines = [l.strip() for l in raw_sec.raw_text.splitlines() if l.strip()]
        for line in lines[1:]:
            cit_info = parsed_doc.get_citation_span(line)
            entities = cls._extract_entities_from_text(line)
            entries.append(PageIndexNode(
                node_id=f"edu_{uuid.uuid4().hex[:6]}",
                node_type="entry",
                title=line[:80],
                summary=f"Education: {line}",
                key_entities=entities,
                citation=CitationSpan(
                    page_number=cit_info["page_number"],
                    char_start=cit_info["char_start"],
                    char_end=cit_info["char_end"],
                    raw_text=line,
                    section_name="education"
                ),
                children=[]
            ))
        return entries

    @classmethod
    def _parse_skills_entries(cls, raw_sec: RawSection, parsed_doc: ParsedDocument) -> List[PageIndexNode]:
        entries = []
        lines = [l.strip() for l in raw_sec.raw_text.splitlines() if l.strip()]
        for line in lines[1:]:
            cit_info = parsed_doc.get_citation_span(line)
            entities = cls._extract_entities_from_text(line)
            category_title = line.split(":")[0] if ":" in line else "Skillset Group"
            entries.append(PageIndexNode(
                node_id=f"sk_{uuid.uuid4().hex[:6]}",
                node_type="entry",
                title=category_title[:60],
                summary=line,
                key_entities=entities,
                citation=CitationSpan(
                    page_number=cit_info["page_number"],
                    char_start=cit_info["char_start"],
                    char_end=cit_info["char_end"],
                    raw_text=line,
                    section_name="skills"
                ),
                children=[]
            ))
        return entries

    @classmethod
    def _parse_generic_entries(cls, raw_sec: RawSection, parsed_doc: ParsedDocument) -> List[PageIndexNode]:
        cit_info = parsed_doc.get_citation_span(raw_sec.raw_text[:200])
        entities = cls._extract_entities_from_text(raw_sec.raw_text)
        return [
            PageIndexNode(
                node_id=f"gen_{uuid.uuid4().hex[:6]}",
                node_type="entry",
                title=raw_sec.section_name[:60],
                summary=raw_sec.raw_text[:200],
                key_entities=entities,
                citation=CitationSpan(
                    page_number=cit_info["page_number"],
                    char_start=cit_info["char_start"],
                    char_end=cit_info["char_end"],
                    raw_text=raw_sec.raw_text[:300],
                    section_name=raw_sec.normalized_name
                ),
                children=[]
            )
        ]

    @classmethod
    def _generate_section_summary(cls, section_type: str, raw_text: str, entries: List[PageIndexNode], entities: List[str]) -> str:
        if section_type == "experience":
            roles = [e.title for e in entries if e.title]
            return f"Experience section with {len(entries)} recorded roles: {'; '.join(roles[:3])}. Core skills applied: {', '.join(entities[:6])}."
        elif section_type == "skills":
            return f"Technical skills repository covering: {', '.join(entities[:10])}."
        elif section_type == "projects":
            proj_names = [e.title for e in entries]
            return f"Projects portfolio featuring {len(entries)} key initiatives: {'; '.join(proj_names[:3])}."
        elif section_type == "education":
            return f"Educational credentials: {raw_text[:120]}."
        elif section_type == "certifications":
            return f"Professional certifications and credentials: {raw_text[:120]}."
        else:
            return raw_text[:200]

    @classmethod
    def _extract_entities_from_text(cls, text: str) -> List[str]:
        found = []
        lower_text = text.lower()
        for skill in COMMON_SKILLS:
            # Word boundary check
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, lower_text):
                found.append(skill)
        return sorted(list(set(found)))

    @classmethod
    def _estimate_experience_years(cls, text: str) -> float:
        # Look for explicit statements like "5+ years", "8 years of experience"
        yoe_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s+(?:of\s+)?experience", text, re.IGNORECASE)
        if yoe_match:
            try:
                return float(yoe_match.group(1))
            except ValueError:
                pass

        # Calculate span of years found (e.g. 2018 - 2024, 2019 - Present)
        years = [int(y) for y in re.findall(r"\b(20\d\d|19\d\d)\b", text)]
        if years:
            min_year = min(years)
            max_year = max(years)
            if "present" in text.lower() or "current" in text.lower():
                max_year = 2026
            span = max(0, max_year - min_year)
            return min(25.0, float(span) if span > 0 else 1.0)

        return 2.0

    @classmethod
    def _extract_candidate_identity(cls, raw_text: str, sections: List[RawSection], file_name: str) -> Tuple[str, Optional[str], Optional[str]]:
        email = None
        phone = None

        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", raw_text)
        if email_match:
            email = email_match.group(0)

        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", raw_text)
        if phone_match:
            phone = phone_match.group(0)

        # Detect candidate name from the first non-empty lines
        name = ""
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        for line in lines[:5]:
            # Clean line
            cleaned = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            words = cleaned.split()
            if 2 <= len(words) <= 4 and not any(w.lower() in ["resume", "curriculum", "vitae", "summary", "experience", "page", "developer", "engineer"] for w in words):
                name = cleaned.title()
                break

        if not name:
            # Derive name from file name
            base = re.sub(r"[-_]", " ", file_name.split(".")[0])
            name = " ".join([w.capitalize() for w in base.split() if w.lower() not in ["resume", "cv"]])
            if not name:
                name = "Candidate Profile"

        return name, email, phone
