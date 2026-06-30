from __future__ import annotations
import json
import dataclasses
from pathlib import Path
from typing import Any
from .sources import csv_source, ats_json_source, resume_source, github_source, PartialProfile
from . import merge as M
from . import confidence as C
from . import project as P
from .schema import validate_against_config


def SrcType(path_or_url: str) -> str:
    s = str(path_or_url).strip()
    if s.startswith("http") and "github.com" in s:
        return "github_url"
    if s.startswith("http") and "linkedin.com" in s:
        return "linkedin_url"
    suffix = Path(s).suffix.lower()
    return {".csv": "recruiter_csv", ".json": "ats_json",".pdf": "resume_pdf", ".docx": "resume_docx", ".txt": "recruiter_notes",}.get(suffix, "unknown")


def getAll(inputs: list[str]) -> list[PartialProfile]:
    profiles: list[PartialProfile] = []
    
    for item in inputs:
        kind = SrcType(item)
        try:
            if kind == "recruiter_csv":
                profiles.extend(csv_source.extract(item))
            elif kind == "ats_json":
                profiles.extend(ats_json_source.extract(item))
            elif kind in ("resume_pdf", "resume_docx"):
                profiles.extend(resume_source.extract(item))
            elif kind == "github_url":
                profiles.extend(github_source.extract(item))
            else: # Unknown/unsupported source: skip
                continue
        except Exception:
            continue
    return profiles


def convert(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj):
        return convert(dataclasses.asdict(obj))
    if isinstance(obj, list):
        return [convert(x) for x in obj]
    if isinstance(obj, dict):
        return {k: convert(v) for k, v in obj.items()}
    return obj


def run(inputs: list[str], config: dict | None = None) -> dict: #pipeline execution
    config = config or {}
    raw_profiles = getAll(inputs)
    merged = M.merge_all(raw_profiles)
    merged = C.apply(merged)

    records = [convert(m) for m in merged]
    projected = [P.project(r, config) for r in records]

    errors = []
    for i, rec in enumerate(projected):
        problems = validate_against_config(rec, config)
        if problems:
            errors.append({"record_index": i, "problems": problems})

    return {"records": projected, "errors": errors}
