
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawFieldValue:
    path: str          
    value: Any
    src: str # for traceability
    method: str 

@dataclass
class PartialProfile:
    # content / profile data fetched for 1 candidate
    match_hint_email: str | None = None
    match_hint_name: str | None = None
    source_name: str = ""
    source_group: str = ""   # "structured" or "unstructured"
    fields: list[RawFieldValue] = field(default_factory=list)

    def add(self, path: str, value: Any, method: str):
        if value in (None, "", [], {}):
            return
        self.fields.append(RawFieldValue(path, value, self.source_name, method))