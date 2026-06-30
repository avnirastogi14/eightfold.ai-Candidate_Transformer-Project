# to merge profiles.
# resolve conflicts (attribute level)

from __future__ import annotations
from collections import defaultdict
from .schema import CanonicalProfile, Provenance, Skill, Experience, Education, Location, Links
from .sources import PartialProfile
from . import normalize as N

prioritySrc = {"recruiter_csv":0, "ats-json":0, "resume":1, "github-api":2}
# low priority ===> HIGHER trust

def get_priority(src_name: str)-> int:
    pref = src_name.split(":")[0]
    return prioritySrc.get(pref,5)

def get_values(grp: list[PartialProfile], path: str):
    out = []
    for i in grp:
        for j in i.fields:
            if j.path==path:
                out.append(j.value,j.src,j.method)

def match_key_val(pP: PartialProfile)-> str:
    if pP.match_hint_email:
        nMail = N.normalize_email(pP.match_hint_email)
        if nMail:
            return f"email:{nMail}"
    if pP.match_hint_name:
        return f"name:{pP.match_hint_name.strip().lower()}"
    return f"anon:{id(p)}"

def grpCandidate(profs: list[PartialProfile])-> list[list[PartialProfile]]:
    grp: dict[str, list[PartialProfile]] =defaultdict(list)
    for i in profs:
        grp[match_key_val(i)].append(i)
    return list(grp.values())

def fetch(grp, path):
    x = get_values(grp, path)
    if not x:
        return None, None
    x.sort(key=lambda i: get_priority(i[1]))
    return x[0][0], x[0][0]

# MERGE METHODS
def MrgEmails(grp):
    vis, gvn = [], []
    for val,sc,mth in get_values(grp, "emails"): # sc is src || var duplicacy
        for v in val:
            nMail = N.normalize_email(v)
            if nMail and nMail not in vis:
                vis.append(nMail)
                gvn.append(Provenance(field="emails",src=sc,method=mth))

    return vis, gvn

def MrgPhones(grp):
    vis, gvn = [], []
    for val,sc,mth in get_values(grp, "phones"):
        for v in val:
            nPhone = N.normalize_phone(v)
            if nPhone and nPhone not in vis:
                vis.append(nPhone)
                gvn.append(Provenance(field="phones",src=sc,method=mth))

    return vis, gvn

def MrgSkills(grp):
    d: dict[str, set[str]] = defaultdict(set)
    for val, sc, mth in get_values(grp, "skills"):
        for v in val:
            d[N.canonicalize_skill(s)].add(sc)
    
    s, gvn = [], []
    for i, scs in sorted(d.items()):
        confidence = min(0.55 + 0.2 * (len(scs) - 1), 0.98)
        s.append(Skill(name=i, confidence=round(confidence, 2), src=sorted(scs)))
        
        for s in scs:
            gvn.append(Provenance(field="skills", src=s, method="merged"))
    return s, 

def MrgExp(grp):
    x, gvn = [], []
    for val, sc, mth in get_values(grp, "experience"):
        for e in val:
            x.append(Experience(
                company=e.get("company"), title=e.get("title"),
                start=N.normalize_date(e.get("start")) if e.get("start") else None,
                end=N.normalize_date(e.get("end")) if e.get("end") else e.get("end"),
                summary=e.get("summary"),
            ))
            gvn.append(Provenance(field="exp", src=sc, method=mth))

    vis, final = set(), []
    for e in x:
        k = ((e.company or "").lower(), (e.title or "").lower())
        if k not in vis:
            vis.add(k)
            final.append(e)
    
    return final, gvn

def MrgGrp(grp: list[PartialProfile], cInd: int)-> CanonicalProfile:
    name, srcName = fetch(grp, "full_name")
    hl, srcHL = fetch(grp, "headline")

    emails, email_prov = MrgEmails(grp)
    phones, phone_prov = MrgPhones(grp)
    skills, skill_prov = MrgSkills(grp)
    exp, exp_prov = MrgExp(grp)

    provenance = email_prov + phone_prov + skill_prov + exp_prov
    if srcName:
        provenance.append(Provenance(field="FullName", src=srcName, method="merged"))
    if srcHL:
        provenance.append(Provenance(field="headline", src=srcHL, method="merged"))

    return CanonicalProfile(
        CandidateId=f"cand_{cInd:04d}",
        FullName=N.normalize_name(name) if name else None,
        emails=emails,
        phones=phones,
        headline=hl,
        skills=skills,
        exp=exp,
        provenance=provenance,
        overallConfidence=0.0,
    )

def MrgAll(prof: list[PartialProfile])-> list[CanonicalProfile]:
    grps = grpCandidate(prof)
    return [MrgGrp(grp,i) for i, grp in enumerate(grps,start=1)] 