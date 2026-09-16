# TrialFlow: Clinical Data Quality Pipeline

TrialFlow is a project that simulates a client data management workflow for a fictional clinical study. It validates synthetic study records against sponsor-specific JSON rules, applies safe corrections, preserves an audit trail, and produces a sponsor-ready CSV plus an Excel quality report.

The project uses **synthetic data only**. It does not contain patient information and is not intended for clinical decision-making.

## Why this project matters

Clinical data teams must deliver accurate files that match each sponsor's specifications. TrialFlow demonstrates how configuration-driven rules can make that work reproducible, traceable, and easier to review.

## Features

- Reproducible synthetic clinical-study data generation
- Sponsor requirements stored in JSON
- Checks for required fields, duplicate sample IDs, allowed visits, dates, numeric results, result ranges, and units
- Safe normalization of common date, visit, and unit variations
- Record-level validation status and issue count
- Audit log showing every automatic correction
- Sponsor-ready file containing only records that pass validation
- CSV quality summary and formatted Excel report
- Automated unit tests using Python's standard library

## Project structure

```text
trialflow-clinical-data-pipeline/
├── config/sponsor_dta_rules.json
├── data/
│   ├── raw/synthetic_clinical_data.csv
│   └── processed/
│       ├── cleaned_clinical_data.csv
│       ├── sponsor_deliverable.csv
│       └── validation_issues.csv
├── docs/
│   ├── data_dictionary.md
│   ├── data_transfer_specification.md
│   └── workflow.md
├── reports/
│   ├── audit_log.csv
│   ├── data_quality_report.xlsx
│   └── quality_summary.csv
├── src/
│   ├── generate_synthetic_data.py
│   └── pipeline.py
├── tests/test_pipeline.py
├── LICENSE
├── requirements.txt
└── run_pipeline.py
```

## Quick start

Requires Python 3.10 or newer. The validation pipeline uses only the Python standard library.

```bash
python run_pipeline.py
python -m unittest discover -s tests -v
```

Running `run_pipeline.py` recreates the raw synthetic dataset and all CSV outputs. The included Excel workbook is a formatted snapshot of the generated results.

## Validation workflow

1. Generate 30 deterministic synthetic records, including several intentional quality problems.
2. Load sponsor rules from `config/sponsor_dta_rules.json`.
3. Normalize safe, unambiguous variations and log every change.
4. Validate each record against the configured requirements.
5. Save the full cleaned dataset with validation status.
6. Release only passing records to the sponsor deliverable.
7. Summarize the results in CSV and Excel.

## Example quality checks

| Check | Example |
|---|---|
| Completeness | Required subject ID is missing |
| Uniqueness | Sample ID appears more than once |
| Conformity | Visit is not in the approved list |
| Validity | Collection date does not match `YYYY-MM-DD` |
| Range | Numeric result falls outside the configured study range |
| Unit | Test result uses an unapproved unit |

## Design decisions

- Rules live in JSON so a new sponsor specification can be supported without rewriting validation logic.
- Raw records are never overwritten.
- Only clear formatting variations are corrected automatically.
- Every correction is recorded in an audit log.
- Records with unresolved errors remain in the cleaned dataset but are excluded from the sponsor deliverable.

## Limitations and next steps

This is an intentionally lightweight demonstration. A production implementation would add a governed database, access controls, encryption, formal schema versioning, electronic approvals, validated deployment controls, and domain-expert review. Possible extensions include SQLite storage, a Streamlit interface, and support for multiple study configurations.



