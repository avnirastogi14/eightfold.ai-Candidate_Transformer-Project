# unstructured data source.

from __future__ import annotations
import re
from pathlib import Path
import pdfplumber
from .__init__ import PartialProfile
import docx

# regex for matching
regexEmail = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+")
regexPhone = re.compile(r"(\+?\d[\d\-\.\(\)\s]{8,}\d)")

# std resume headers as per req
headers = ["experience", "work experience", "employment", "education", "skills"]


def _read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        return "\n".join(text)
    elif path.suffix.lower() == ".docx":
        d = docx.Document(str(path))
        return "\n".join(p.text for p in d.paragraphs)
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


def _split_sections(text: str) -> dict[str, str]:
    lines = text.split("\n")
    sections: dict[str, list[str]] = {}
    current = "header"
    sections[current] = []
    for line in lines:
        stripped = line.strip().lower().rstrip(":")
        if stripped in headers:
            current = stripped
            sections[current] = []
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def extract(path: str | Path) -> list[PartialProfile]:
    path = Path(path)
    if not path.exists():
        return []

    try:
        text = _read_text(path)
    except Exception:
        return []  # corrupt/unsupported file -> no data, no crash

    if not text or not text.strip():
        return []

    source_name = f"resume:{path.name}"
    p = PartialProfile(source_name=source_name, source_group="unstructured")

    email_match = regexEmail.search(text)
    if email_match:
        p.add("emails", [email_match.group(0)], "regex_extract")
        p.match_hint_email = email_match.group(0)

    phone_match = regexPhone.search(text)
    if phone_match:
        candidate = phone_match.group(0).strip()
        if sum(c.isdigit() for c in candidate) >= 7:
            p.add("phones", [candidate], "regex_extract")


    # note: heuristic :: method

    # Edge Case:
    # when line === non empty && !email || !phone ==> NAME
    for line in text.split("\n")[:5]:
        line = line.strip()
        if line and not regexEmail.search(line) and not regexPhone.search(line) and len(line) < 60:
            p.add("full_name", line, "heuristic") 
            p.match_hint_name = line
            break

    sections = _split_sections(text)

    skills_block = sections.get("skills", "")
    if skills_block.strip():
        raw_skills = re.split(r"[,•|\n/]", skills_block)
        skills = [s.strip() for s in raw_skills if s.strip() and len(s.strip()) < 40]
        if skills:
            p.add("skills", skills, "heuristic")

    exp_block = sections.get("experience") or sections.get("work experience") or sections.get("employment")
    if exp_block and exp_block.strip():
        p.add("experience_raw_text", exp_block.strip(), "heuristic")

    edu_block = sections.get("education")
    if edu_block and edu_block.strip():
        p.add("education_raw_text", edu_block.strip(), "heuristic")

    return [p]