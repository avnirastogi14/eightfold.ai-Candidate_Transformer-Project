from __future__ import annotations
from collections import Counter

from .schema import CanonicalProfile

wght = {"FullName": 0.15, "emails": 0.15, "phones": 0.10,"headline": 0.05, "skills": 0.25, "exp": 0.25}

def score(prof: CanonicalProfile) -> float:
    coverVal = 0.0
    if prof.FullName:
        coverVal += wght["FullName"]
    if prof.emails:
        coverVal += wght["emails"]
    if prof.phones:
        coverVal += wght["phones"]
    if prof.headline:
        coverVal += wght["headline"]
    if prof.skills:
        coverVal += wght["skills"]
    if prof.exp:
        coverVal += wght["exp"]

    diffSrc = len({p.src.split(":")[0] for p in prof.provenance})
    bonus = min(0.15 * max(diffSrc-1,0),0.3)

    return round(min(coverVal+bonus,1.0), 2)


def apply(profiles: list[CanonicalProfile]) -> list[CanonicalProfile]:
    for p in profiles:
        p.overallConfidence = score(p)
    return profiles