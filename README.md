# Multi-Source Candidate Data Transformer

**Author:** Avni Rastogi

---

## Problem Statement

Build an end-to-end transformation pipeline capable of ingesting candidate information from multiple heterogeneous sources (CSV, ATS JSON, Resume PDF/DOCX and GitHub), merging them into a single canonical candidate profile, and producing configurable JSON output with confidence scoring and provenance tracking.

---

## Project Overview

This project implements a modular data transformation pipeline that:

- Accepts multiple candidate data sources.
- Automatically detects the source type.
- Extracts structured and unstructured information.
- Merges duplicate candidate profiles.
- Normalizes extracted fields.
- Computes an overall confidence score.
- Tracks provenance for every extracted field.
- Supports configurable output schemas through runtime configuration.

The implementation follows a pipeline-based architecture where every stage performs a single responsibility, making the system easier to maintain and extend.

---

## Supported Input Sources

### Structured Sources
- Recruiter CSV
- ATS JSON

### Unstructured Sources
- Resume (PDF/DOCX)
- GitHub Profile

---

## Project Structure

```
8fold-transformer/

├── cli.py
├── config/
├── output/
├── sample-ips/
├── tests/
│
└── transformer/
    ├── pipeline.py
    ├── merge_profile.py
    ├── normalize.py
    ├── confidence.py
    ├── project.py
    ├── schema.py
    └── sources/
        ├── struc/
        └── unstruc/
```

---

## Pipeline Flow

```
CLI
 ↓
Source Detection
 ↓
Source Extractors
 ↓
PartialProfile Generation
 ↓
Merge & Normalize
 ↓
Confidence Scoring
 ↓
Projection
 ↓
Validation
 ↓
Canonical JSON Output
```

---

## Installation

Create and activate a virtual environment.

```bash
python -m venv .venv
```

macOS/Linux

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Basic Execution

```bash
python cli.py \
--inputs \
sample-ips/recruiters.csv \
sample-ips/resumes/jane_doe.pdf
```

---

### Save Output

```bash
python cli.py \
--inputs \
sample-ips/recruiters.csv \
sample-ips/resumes/jane_doe.pdf \
--out output/default_output.json
```

---

### Using Custom Projection

```bash
python cli.py \
--inputs \
sample-ips/recruiters.csv \
sample-ips/resumes/jane_doe.pdf \
--config config/example_custom.json \
--out output/custom_output.json
```

---

## Sample Inputs

The repository includes sample inputs inside:

```
sample-ips/

├── recruiters.csv
├── ats_records.json
└── resumes/
      └── jane_doe.pdf
```

These can be combined in different ways while executing the pipeline.

---

## Output

The generated output contains:

- Canonical Candidate Profile
- Contact Information
- Skills
- Experience
- Education
- Provenance
- Overall Confidence Score

Example:

```json
{
  "CandidateId": "cand_0001",
  "FullName": "Jane Doe",
  "emails": [
    "jane.doe@example.com"
  ],
  "overallConfidence": 1.0
}
```

---

## Design Highlights

- Modular pipeline architecture
- Automatic source detection
- Intermediate `PartialProfile` representation
- Structured & unstructured extractors
- Merge and conflict resolution
- Rule-based normalization
- Provenance tracking
- Configurable output projection
- Fault-tolerant processing

---

## Known Limitation

The resume parser currently uses deterministic section-based heuristics. Resumes with significantly different section headings may not have all fields extracted correctly. This can be improved in the future using fuzzy section matching or lightweight NLP techniques while keeping the overall pipeline architecture unchanged.

---

## Future Improvements

- Additional ATS integrations
- More flexible resume section detection
- Better candidate matching strategies
- Improved experience extraction
- Additional external profile sources

---

## Author

**Avni Rastogi**

Built as part of the **Eightfold Engineering Intern Assignment**.
