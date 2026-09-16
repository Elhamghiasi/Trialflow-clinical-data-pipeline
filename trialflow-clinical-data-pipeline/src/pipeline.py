"""Configuration-driven cleaning and validation for synthetic clinical data."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


OUTPUT_FIELDS = [
    "study_id",
    "subject_id",
    "sample_id",
    "visit_name",
    "collection_date",
    "test_name",
    "test_result",
    "result_unit",
    "validation_status",
    "issue_count",
]


def load_rules(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _normalize_record(
    record: dict[str, str], rules: dict[str, Any], row_number: int
) -> tuple[dict[str, str], list[dict[str, str]]]:
    cleaned = {key: (value.strip() if isinstance(value, str) else value) for key, value in record.items()}
    changes: list[dict[str, str]] = []

    def change(field: str, new_value: str, reason: str) -> None:
        old_value = cleaned.get(field, "")
        if old_value != new_value:
            cleaned[field] = new_value
            changes.append(
                {
                    "row_number": str(row_number),
                    "sample_id": cleaned.get("sample_id", ""),
                    "field": field,
                    "original_value": old_value,
                    "cleaned_value": new_value,
                    "reason": reason,
                }
            )

    original_subject = record.get("subject_id", "")
    if original_subject != cleaned.get("subject_id", ""):
        changes.append(
            {
                "row_number": str(row_number),
                "sample_id": cleaned.get("sample_id", ""),
                "field": "subject_id",
                "original_value": original_subject,
                "cleaned_value": cleaned.get("subject_id", ""),
                "reason": "Trimmed surrounding whitespace",
            }
        )

    visit = cleaned.get("visit_name", "")
    alias = rules.get("visit_aliases", {}).get(visit.lower())
    if alias:
        change("visit_name", alias, "Mapped approved visit alias")

    date_text = cleaned.get("collection_date", "")
    if date_text:
        try:
            datetime.strptime(date_text, rules["date_format"])
        except ValueError:
            for alternative in rules.get("alternative_date_formats", []):
                try:
                    parsed = datetime.strptime(date_text, alternative)
                    change(
                        "collection_date",
                        parsed.strftime(rules["date_format"]),
                        "Converted date to sponsor format",
                    )
                    break
                except ValueError:
                    continue

    test_name = cleaned.get("test_name", "")
    test_rule = rules.get("tests", {}).get(test_name, {})
    unit = cleaned.get("result_unit", "")
    unit_alias = test_rule.get("unit_aliases", {}).get(unit)
    if unit_alias:
        change("result_unit", unit_alias, "Mapped approved unit alias")

    return cleaned, changes


def process_records(
    records: list[dict[str, str]], rules: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    """Normalize and validate records, returning cleaned rows, issues, and audit changes."""
    normalized: list[dict[str, str]] = []
    audit_log: list[dict[str, str]] = []
    for row_number, record in enumerate(records, start=2):
        cleaned, changes = _normalize_record(record, rules, row_number)
        normalized.append(cleaned)
        audit_log.extend(changes)

    unique_fields = rules.get("unique_fields", [])
    duplicate_counts = {
        field: Counter(row.get(field, "") for row in normalized if row.get(field, ""))
        for field in unique_fields
    }

    issues: list[dict[str, str]] = []
    output_rows: list[dict[str, Any]] = []

    def add_issue(row_number: int, row: dict[str, str], field: str, rule: str, message: str) -> None:
        issues.append(
            {
                "row_number": str(row_number),
                "sample_id": row.get("sample_id", ""),
                "field": field,
                "rule": rule,
                "severity": "Error",
                "message": message,
            }
        )

    for row_number, row in enumerate(normalized, start=2):
        start_count = len(issues)
        for field in rules["required_columns"]:
            if not row.get(field, ""):
                add_issue(row_number, row, field, "required", f"{field} is required")

        if row.get("study_id") and row["study_id"] != rules["study_id"]:
            add_issue(row_number, row, "study_id", "study_match", "Study ID does not match the specification")

        if row.get("visit_name") and row["visit_name"] not in rules["allowed_visits"]:
            add_issue(row_number, row, "visit_name", "allowed_values", "Visit is not approved")

        date_text = row.get("collection_date", "")
        if date_text:
            try:
                datetime.strptime(date_text, rules["date_format"])
            except ValueError:
                add_issue(row_number, row, "collection_date", "date_format", "Date must use YYYY-MM-DD")

        for field in unique_fields:
            value = row.get(field, "")
            if value and duplicate_counts[field][value] > 1:
                add_issue(row_number, row, field, "unique", f"Duplicate {field}: {value}")

        test_name = row.get("test_name", "")
        test_rule = rules.get("tests", {}).get(test_name)
        if test_name and not test_rule:
            add_issue(row_number, row, "test_name", "known_test", "Test name is not configured")
        elif test_rule:
            value_text = row.get("test_result", "")
            if value_text:
                try:
                    value = float(value_text)
                    if not test_rule["minimum"] <= value <= test_rule["maximum"]:
                        add_issue(
                            row_number,
                            row,
                            "test_result",
                            "result_range",
                            f"Result must be between {test_rule['minimum']} and {test_rule['maximum']}",
                        )
                except ValueError:
                    add_issue(row_number, row, "test_result", "numeric", "Result must be numeric")

            unit = row.get("result_unit", "")
            if unit and unit not in test_rule["allowed_units"]:
                add_issue(row_number, row, "result_unit", "allowed_unit", "Unit is not approved for this test")

        issue_count = len(issues) - start_count
        enriched: dict[str, Any] = dict(row)
        enriched["validation_status"] = "PASS" if issue_count == 0 else "FAIL"
        enriched["issue_count"] = issue_count
        output_rows.append(enriched)

    return output_rows, issues, audit_log


def build_summary(
    rows: list[dict[str, Any]], issues: list[dict[str, str]], audit_log: list[dict[str, str]]
) -> list[dict[str, Any]]:
    passed = sum(row["validation_status"] == "PASS" for row in rows)
    failed = len(rows) - passed
    metrics: list[tuple[str, Any]] = [
        ("Total records", len(rows)),
        ("Passing records", passed),
        ("Failing records", failed),
        ("Pass rate", round(passed / len(rows), 4) if rows else 0),
        ("Total validation issues", len(issues)),
        ("Automatic corrections", len(audit_log)),
        ("Sponsor-ready records", passed),
    ]
    rule_counts = Counter(issue["rule"] for issue in issues)
    metrics.extend((f"Issues: {rule}", count) for rule, count in sorted(rule_counts.items()))
    return [{"metric": metric, "value": value} for metric, value in metrics]


def run_pipeline(base_dir: Path) -> dict[str, int]:
    rules = load_rules(base_dir / "config" / "sponsor_dta_rules.json")
    records = read_csv(base_dir / "data" / "raw" / "synthetic_clinical_data.csv")
    rows, issues, audit_log = process_records(records, rules)
    deliverable = [row for row in rows if row["validation_status"] == "PASS"]
    summary = build_summary(rows, issues, audit_log)

    write_csv(base_dir / "data" / "processed" / "cleaned_clinical_data.csv", rows, OUTPUT_FIELDS)
    write_csv(base_dir / "data" / "processed" / "sponsor_deliverable.csv", deliverable, OUTPUT_FIELDS[:-2])
    write_csv(
        base_dir / "data" / "processed" / "validation_issues.csv",
        issues,
        ["row_number", "sample_id", "field", "rule", "severity", "message"],
    )
    write_csv(
        base_dir / "reports" / "audit_log.csv",
        audit_log,
        ["row_number", "sample_id", "field", "original_value", "cleaned_value", "reason"],
    )
    write_csv(base_dir / "reports" / "quality_summary.csv", summary, ["metric", "value"])
    return {
        "records": len(rows),
        "passed": len(deliverable),
        "failed": len(rows) - len(deliverable),
        "issues": len(issues),
        "corrections": len(audit_log),
    }

