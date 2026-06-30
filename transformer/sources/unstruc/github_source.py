from __future__ import annotations
import re
import urllib.request
import json
from urllib.error import URLError, HTTPError

from .__init__ import PartialProfile

uNameRegex = re.compile(r"github\.com/([A-Za-z0-9\-]+)/?$")


def getUname(url: str) -> str | None:
    m = uNameRegex.search(url.strip())
    return m.group(1) if m else None

def extract(url: str, timeout: float = 6.0) -> list[PartialProfile]:
    username = getUname(url)
    if not username:
        return []

    source_name = f"github_api:{username}"
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{username}",
            headers={"User-Agent": "candidate-transformer", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)

        req2 = urllib.request.Request(
            f"https://api.github.com/users/{username}/repos?per_page=100",
            headers={"User-Agent": "candidate-transformer"},
        )
        with urllib.request.urlopen(req2, timeout=timeout) as resp2:
            repos = json.load(resp2)

    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, dict) or data.get("message") == "Not Found":
        return []

    p = PartialProfile(
        match_hint_name=data.get("name"), source_name=source_name,
        source_group="unstructured",
    )
    if data.get("name"):
        p.add("full_name", data["name"], "api_field")
    if data.get("bio"):
        p.add("headline", data["bio"], "api_field")
    if data.get("location"):
        p.add("location_raw", data["location"], "api_field")
    if data.get("blog"):
        p.add("links.portfolio", data["blog"], "api_field")
    p.add("links.github", f"https://github.com/{username}", "direct_field")

    languages = sorted({
        r["language"] for r in repos if isinstance(r, dict) and r.get("language")
    }) if isinstance(repos, list) else []
    if languages:
        p.add("skills", languages, "heuristic")

    if isinstance(repos, list) and repos:
        p.add("github_repo_count", len(repos), "api_field")

    return [p]
