import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transformer import normalize as N
from transformer.pipeline import run

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "sample_inputs"


def test_phone_normalization():
    assert N.normalize_phone("+1 415-555-0199") == "+14155550199"
    assert N.normalize_phone("9876543210", default_region="IN") == "+919876543210"
    assert N.normalize_phone("not a phone") is None
    assert N.normalize_phone("") is None


def test_date_normalization():
    assert N.normalize_date("March 2021") == "2021-03"
    assert N.normalize_date("2021-03") == "2021-03"
    assert N.normalize_date("present") == "present"
    assert N.normalize_date("garbage") is None


def test_skill_canonicalization():
    assert N.canonicalize_skill("js") == "JavaScript"
    assert N.canonicalize_skill("Python3") == "Python"
    assert N.canonicalize_skill("SomeNicheTool") == "SomeNicheTool"


def test_default_pipeline_end_to_end():
    inputs = [
        str(SAMPLES / "recruiters.csv"),
        str(SAMPLES / "resumes" / "jane_doe.pdf"),
        str(SAMPLES / "ats_records.json"),
    ]
    result = run(inputs, {})
    assert result["errors"] == []
    names = {r["full_name"] for r in result["records"] if r["full_name"]}
    assert "Jane Doe" in names
    assert "Priya Sharma" in names

    jane = next(r for r in result["records"] if r["full_name"] == "Jane Doe")
    assert jane["emails"] == ["jane.doe@example.com"]
    assert jane["phones"] == ["+14155550199"]
    assert any(s["name"] == "Python" for s in jane["skills"])
    assert jane["overall_confidence"] > 0
    assert len(jane["provenance"]) > 0


def test_cross_source_merge_by_email():
    inputs = [str(SAMPLES / "recruiters.csv"), str(SAMPLES / "ats_records.json")]
    result = run(inputs, {})
    priya_records = [r for r in result["records"] if r["full_name"] == "Priya Sharma"]
    assert len(priya_records) == 1
    rec = priya_records[0]
    skill_names = {s["name"] for s in rec["skills"]}
    assert "Python" in skill_names and "PyTorch" in skill_names
    assert rec["experience"][0]["company"] == "DataWorks"


def test_custom_config_projection():
    config = {
        "fields": [
            {"path": "full_name", "type": "string", "required": True},
            {"path": "primary_email", "from": "emails[0]", "type": "string"},
            {"path": "phone", "from": "phones[0]", "normalize": "E164"},
        ],
        "conf": True,
        "prov": False,
        "missTrue": "null",
    }
    result = run([str(SAMPLES / "recruiters.csv")], config)
    rec = next(r for r in result["records"] if r["full_name"] == "Jane Doe")
    assert set(rec.keys()) == {"full_name", "primary_email", "phone", "_confidence"}
    assert rec["primary_email"] == "jane.doe@example.com"
    assert rec["phone"].startswith("+1")


def test_on_missing_error_surfaces_validation_problem():
    config = {
        "fields": [{"path": "full_name", "required": True}],
        "missTrue": "error",
        "conf": False,
        "prov": False,
    }
    result = run([str(SAMPLES / "ats_records.json")], config)
    assert len(result["errors"]) >= 1


def test_missing_file_degrades_gracefully(): # expected behaviour is NO CRASH
    result = run(["does_not_exist.csv", "also_missing.pdf"], {})
    assert result["records"] == []
    assert result["errors"] == []


def test_malformed_csv_row_does_not_crash():
    result = run([str(SAMPLES / "recruiters.csv")], {})
    blanks = [r for r in result["records"] if r["full_name"] is None]
    assert len(blanks) >= 1
    assert blanks[0]["emails"] == [] or blanks[0]["emails"] is None


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL  {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
