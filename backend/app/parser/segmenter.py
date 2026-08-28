import re
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel

class RawSection(BaseModel):
    section_name: str
    normalized_name: str  # experience, education, skills, projects, certifications, summary, contact, other
    raw_text: str
    char_start: int
    char_end: int

class SectionSegmenter:
    # Standard section heading regexes
    SECTION_PATTERNS = [
        (r"^(?:professional\s+|work\s+|employment\s+)?experience\b", "experience"),
        (r"^(?:work\s+history|career\s+history|employment\s+history)\b", "experience"),
        (r"^(?:technical\s+|core\s+|key\s+)?skills\b", "skills"),
        (r"^(?:technologies|technical\s+proficiencies|tech\s+stack|competencies)\b", "skills"),
        (r"^(?:education|academic\s+background|academic\s+qualifications)\b", "education"),
        (r"^(?:projects|key\s+projects|notable\s+projects|personal\s+projects)\b", "projects"),
        (r"^(?:certifications|licenses\s+and\s+certifications|credentials|certificates)\b", "certifications"),
        (r"^(?:professional\s+summary|executive\s+summary|summary|profile|about\s+me|objective)\b", "summary"),
        (r"^(?:awards|honors|publications|patents|volunteer\s+experience)\b", "awards_and_others"),
    ]

    @classmethod
    def segment(cls, full_text: str) -> List[RawSection]:
        lines = full_text.splitlines()
        found_headings: List[Tuple[int, int, str, str]] = []  # (line_idx, char_pos, raw_heading, normalized_name)

        current_char_pos = 0
        for idx, line in enumerate(lines):
            line_len = len(line) + 1  # include newline
            stripped = line.strip()

            if stripped and len(stripped) < 60:
                # Check if line looks like a heading
                norm_name = cls._classify_heading(stripped)
                if norm_name:
                    found_headings.append((idx, current_char_pos, stripped, norm_name))

            current_char_pos += line_len

        if not found_headings:
            # Fallback: treat entire document as a single general section
            return [
                RawSection(
                    section_name="Full Resume",
                    normalized_name="summary",
                    raw_text=full_text,
                    char_start=0,
                    char_end=len(full_text)
                )
            ]

        # Extract content between headings
        sections: List[RawSection] = []

        # If there is content before the first heading (usually contact / header / name)
        first_heading_char = found_headings[0][1]
        if first_heading_char > 0:
            header_text = full_text[:first_heading_char].strip()
            if header_text:
                sections.append(RawSection(
                    section_name="Contact & Header",
                    normalized_name="contact",
                    raw_text=header_text,
                    char_start=0,
                    char_end=first_heading_char
                ))

        for i, (line_idx, char_pos, heading_str, norm_name) in enumerate(found_headings):
            end_pos = found_headings[i + 1][1] if i + 1 < len(found_headings) else len(full_text)
            section_content = full_text[char_pos:end_pos].strip()

            sections.append(RawSection(
                section_name=heading_str,
                normalized_name=norm_name,
                raw_text=section_content,
                char_start=char_pos,
                char_end=end_pos
            ))

        return sections

    @classmethod
    def _classify_heading(cls, text: str) -> Optional[str]:
        cleaned = re.sub(r"[#\-*_:]", "", text).strip().lower()
        if not cleaned:
            return None

        # Check against patterns
        for pattern, norm_name in cls.SECTION_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                return norm_name

        # If ALL CAPS or Title Case and matches single word headings
        if cleaned in ["experience", "education", "skills", "projects", "certifications", "summary", "profile", "contact"]:
            return cleaned

        return None
