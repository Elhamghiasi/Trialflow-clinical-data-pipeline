# Data Dictionary

All records are synthetic and belong to the fictional study `TRIAL-001`.

| Field | Type | Description | Example |
|---|---|---|---|
| `study_id` | Text | Study identifier | `TRIAL-001` |
| `subject_id` | Text | Synthetic participant identifier | `SUBJ-001` |
| `sample_id` | Text | Unique synthetic sample identifier | `SMP-0001` |
| `visit_name` | Text | Protocol visit | `Week 4` |
| `collection_date` | Date | Synthetic sample collection date | `2026-01-08` |
| `test_name` | Text | Configured laboratory test | `MRD_SCORE` |
| `test_result` | Decimal | Synthetic test result | `63.38` |
| `result_unit` | Text | Unit defined for the selected test | `score` |
| `validation_status` | Text | Pipeline result | `PASS` or `FAIL` |
| `issue_count` | Integer | Number of unresolved errors for the record | `0` |

The numeric ranges in this project are fictional transfer specifications. They are not medical reference ranges.

