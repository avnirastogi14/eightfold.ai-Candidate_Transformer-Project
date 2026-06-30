from __future__ import annotations
import re
from typing import Any

from . import normalize as N

regex = re.compile(r"^([^\[\]]+)(\[(\d*)\])?$")


def get_path(obj: Any, path: str) -> Any:
    curr = obj
    for part in path.split("."):
        m = regex.match(part)
        if not m:
            return None
        key, has_index, index = m.group(1), m.group(2), m.group(3)
        if isinstance(curr, dict):
            curr = curr.get(key)
        else:
            return None
        if has_index is not None and index != "":
            if not isinstance(curr, list):
                return None
            idx = int(index)
            curr = curr[idx] if 0 <= idx < len(curr) else None
    return curr


def solve(obj: Any, path: str) -> Any:
    if "[]" not in path:
        return get_path(obj, path)

    pre, post = path.split("[]", 1)
    pre = pre.rstrip(".")
    seq = get_path(obj, pre)
    if not isinstance(seq, list):
        return None
    post = post.lstrip(".")
    if not post:
        return seq
    return [get_path(item, post) for item in seq]


normzr = {
    "E164": lambda v: N.normalize_phone(v) if isinstance(v, str) else v,
    "canonical": lambda v: (
        [N.canonicalize_skill(x) for x in v] if isinstance(v, list)
        else N.canonicalize_skill(v) if isinstance(v, str) else v
    ),
}


def project(record: dict, config: dict) -> dict:
    fields_cfg = config.get("fields")
    missTrue = config.get("missTrue", "null")
    conf = config.get("conf", True)
    prov = config.get("prov", True)

    if not fields_cfg:
        out = dict(record)
        if not conf:
            out.pop("overall_confidence", None)
        if not prov:
            out.pop("provenance", None)
        return out

    out: dict = {}
    for f in fields_cfg:
        out_path = f["path"]
        source_path = f.get("from", out_path)
        value = solve(record, source_path)

        norm = f.get("normalize")
        if norm and norm in normzr and value is not None:
            value = normzr[norm](value)

        missFlag = value in (None, [], "")
        if missFlag and missTrue == "omit":
            continue
        out[out_path] = value if not missFlag else None

    if conf:
        out["_confidence"] = record.get("overall_confidence")
    if prov:
        top_level_fields = {f["path"].split(".")[0].split("[")[0] for f in fields_cfg}
        out["_provenance"] = [
            pr for pr in record.get("provenance", [])
            if pr.get("field") in top_level_fields
        ]

    return out
