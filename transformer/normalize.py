from __future__ import annotations
import re
from typing import Optional

import phonenumbers

skillSet={
    "js": "JavaScript", "javascript": "JavaScript", "node": "Node.js",
    "nodejs": "Node.js", "node.js": "Node.js", "node.js": "Node.js",
    "py": "Python", "python3": "Python", "python": "Python",
    "reactjs": "React", "react.js": "React", "react": "React",
    "golang": "Go", "go": "Go",
    "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    "tf": "TensorFlow", "tensorflow": "TensorFlow",
    "pytorch": "PyTorch", "torch": "PyTorch",
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "nlp": "Natural Language Processing",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "c++": "C++", "cpp": "C++",
    "aws": "AWS", "amazon web services": "AWS",
    "gcp": "GCP", "google cloud": "GCP",
    "sql": "SQL",
    "docker": "Docker", 
    "java": "Java",
    "typescript": "TypeScript", "ts": "TypeScript",
}

def canonicalize_skill(raw: str) -> str:
    key = raw.strip().lower()
    if key in skillSet:
        return skillSet[key] # Title-case unknown skills as a sane default rather than inventing data
    return raw.strip()


def normalize_phone(raw: str, default_region: str = "US") -> Optional[str]:
    """Best-effort E.164 normalization. Returns None if the input can't be confidently parsed."""
    if not raw or not raw.strip():
        return None
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return None


_EMAIL_RE = re.compile(r"^[\w.\-+]+@[\w\-]+\.[\w.\-]+$")


def normalize_email(raw: str) -> Optional[str]:
    if not raw:
        return None
    e = raw.strip().lower()
    return e if _EMAIL_RE.match(e) else None


_MONTHS = { m.lower(): i for i, m in enumerate(
        ["", "January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]) if m}
for k in list(_MONTHS):
    _MONTHS[k[:3]] = _MONTHS[k]  # add 3-letter abbrevs


def normalize_date(raw: str) -> Optional[str]:
    """Normalize a wide variety of date strings to YYYY-MM. Returns None when the input can't be confidently parsed."""
    if not raw:
        return None
    raw = raw.strip()
    if raw.lower() in ("present", "current", "now", "ongoing"):
        return "present"

    m = re.match(r"^(\d{4})[-/](\d{1,2})$", raw)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"

    m = re.match(r"^(\d{4})$", raw)
    if m:
        return f"{m.group(1)}-01"

    m = re.match(r"^([A-Za-z]+)\.?,?\s+(\d{4})$", raw)
    if m and m.group(1).lower() in _MONTHS:
        return f"{m.group(2)}-{_MONTHS[m.group(1).lower()]:02d}"

    m = re.match(r"^(\d{1,2})/(\d{4})$", raw)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"

    m = re.match(r"^(\d{4})-(\d{2})-\d{2}", raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    return None


def normalize_name(raw: str) -> Optional[str]:
    if not raw:
        return None
    cleaned = re.sub(r"\s+", " ", raw.strip())
    return cleaned.title() if cleaned.isupper() or cleaned.islower() else cleaned


cntry = { "usa": "US", "united states": "US", "u.s.": "US", "us": "US",
    "india": "IN",
    "uk": "GB", "united kingdom": "GB",
    "canada": "CA",
    "germany": "DE",
}


def normalize_country(raw: str) -> Optional[str]:
    if not raw:
        return None
    key = raw.strip().lower()
    if key in cntry:
        return cntry[key]
    if len(raw.strip()) == 2:
        return raw.strip().upper()
    return None

