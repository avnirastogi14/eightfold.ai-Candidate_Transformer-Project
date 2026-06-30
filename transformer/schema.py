# the schema for candidate profile.
# expected / fixed format for every src to get translated into + merges profiles.

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class Provenance: # to allow the traceback and hence the confidence score
    field: str
    src: str
    method: str

@dataclass
class Skill:
    name: str
    confidence: float
    src: list[str] = field(default_factory=list)

@dataclass
class Experience:
    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    summary: Optional[str] = None

@dataclass
class Education:
    institute: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    endYr: Optional[str] = None

@dataclass
class Location:
    city: Optional[str] = None
    rgn: Optional[str] = None
    country: Optional[str] = None

@dataclass
class Links:
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: list[str]=field(default_factory=list)

@dataclass
class CanonicalProfile:
    CandidateId: str
    FullName: Optional[str] = None
    emails: list[str]=field(default_factory=list)
    phones: list[str]=field(default_factory=list)
    location: Location = field(default_factory=Location)
    links: Links = field(default_factory=Links)
    headline: Optional[str] = None
    YoE: Optional[float] = None
    skills: list[Skill] = field(default_factory=list)
    exp: list[Experience] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    provenance: list[Provenance] = field(default_factory=list)
    overallConfidence: float=0.0

    def to_dict(self)->dict:
        return asdict(self)