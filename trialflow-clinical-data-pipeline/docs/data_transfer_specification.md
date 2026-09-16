# Fictional Data Transfer Specification

## Study

- Study ID: `TRIAL-001`
- Specification version: `1.0`
- Delivery format: UTF-8 CSV with a header row
- Date format: `YYYY-MM-DD`
- Unique record key: `sample_id`

## Required fields

`study_id`, `subject_id`, `sample_id`, `visit_name`, `collection_date`, `test_name`, `test_result`, and `result_unit`.

## Approved visits

- Screening
- Baseline
- Week 4
- Week 8

## Tests

| Test | Configured range | Approved unit |
|---|---:|---|
| MRD_SCORE | 0–100 | score |
| CELL_COUNT | 0–5,000 | cells/uL |

These ranges are fictional and exist only to demonstrate configurable validation.

## Release rule

Only records with no unresolved validation errors may be included in `sponsor_deliverable.csv`. All automatic corrections must appear in `reports/audit_log.csv`.

