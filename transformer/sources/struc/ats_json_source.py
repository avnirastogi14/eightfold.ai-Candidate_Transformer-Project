from __future__ import annotations
import json
from pathlib import Path

from .. import PartialProfile


def get(d: dict, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] not in (None, ""):
            return d[k]
    return default


def fetch(path: str | Path) -> list[PartialProfile]:
    path = Path(path)
    if not path.exists():
        return []

    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []

    records = data if isinstance(data, list) else [data]
    profiles: list[PartialProfile] = []

    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            continue
        contact = rec.get("contact", {}) if isinstance(rec.get("contact"), dict) else {}
        name = get(rec, "candidate_name", "full_name", "name")
        email = get(contact, "email_address", "email") or get(rec, "email")
        phone = get(contact, "phone_number", "phone") or get(rec, "phone")

        source_name = f"ats_json:record{i}"
        p = PartialProfile( match_hint_email=email, match_hint_name=name,source_name=source_name, source_group="structured",)
        if name:
            p.add("full_name", name, "api_field")
        if email:
            p.add("emails", [email], "api_field")
        if phone:
            p.add("phones", [phone], "api_field")

        jobs = rec.get("work_history") or rec.get("positions") or []
        exp = []
        for j in jobs if isinstance(jobs, list) else []:
            if not isinstance(j, dict):
                continue
            exp.append({
                "company": get(j, "employer", "company"),
                "title": get(j, "role", "title"),
                "start": get(j, "from", "start_date"),
                "end": get(j, "to", "end_date"),
                "summary": get(j, "description"),
            })
        if exp:
            p.add("experience", exp, "api_field")

        skills = rec.get("skills") or rec.get("tags")
        if isinstance(skills, list) and skills:
            p.add("skills", skills, "api_field")

        profiles.append(p)

    return profiles
