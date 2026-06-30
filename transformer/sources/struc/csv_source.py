# Structured source: Recruiter CSV export.

from __future__ import annotations
import csv
from pathlib import Path

from .. import PartialProfile

EXPECTED_COLS = {"name", "email", "phone", "current_company", "title"}

def extract(path: str | Path) -> list[PartialProfile]:
    path = Path(path)
    profiles: list[PartialProfile] = []
    if not path.exists():
        return profiles

    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                return profiles
            for i, row in enumerate(reader):
                row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
                
                #skipping blank rows
                if not any(row.values()):
                    continue

                source_name = f"recruiter_csv:row{i+2}"
                p = PartialProfile(
                    match_hint_email=row.get("email") or None,
                    match_hint_name=row.get("name") or None,
                    source_name=source_name,
                    source_group="structured",
                )
                
                if row.get("name"):
                    p.add("full_name", row["name"], "direct_field")
                if row.get("email"):
                    p.add("emails", [row["email"]], "direct_field")
                if row.get("phone"):
                    p.add("phones", [row["phone"]], "direct_field")
                if row.get("current_company") or row.get("title"):
                    p.add("experience", [{"company": row.get("current_company") or None, "title": row.get("title") or None, "start": None, "end": "present", "summary": None, }], "direct_field")
                profiles.append(p)
    
    except (csv.Error, UnicodeDecodeError, OSError):
        return [] # uncompatible file to result "No Result" instead of wrong / crashed system

    return profiles