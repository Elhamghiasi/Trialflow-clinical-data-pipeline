"""Generate a deterministic synthetic study dataset with known quality issues."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


FIELDS = [
    "study_id",
    "subject_id",
    "sample_id",
    "visit_name",
    "collection_date",
    "test_name",
    "test_result",
    "result_unit",
]


def generate_records(count: int = 30, seed: int = 42) -> list[dict[str, str]]:
    """Return synthetic records and add intentional errors for validation."""
    rng = random.Random(seed)
    visits = ["Screening", "Baseline", "Week 4", "Week 8"]
    start = date(2026, 1, 5)
    records: list[dict[str, str]] = []

    for index in range(1, count + 1):
        test_name = "MRD_SCORE" if index % 2 else "CELL_COUNT"
        result = rng.uniform(2, 98) if test_name == "MRD_SCORE" else rng.uniform(500, 4200)
        records.append(
            {
                "study_id": "TRIAL-001",
                "subject_id": f"SUBJ-{((index - 1) // 4) + 1:03d}",
                "sample_id": f"SMP-{index:04d}",
                "visit_name": visits[(index - 1) % 4],
                "collection_date": (start + timedelta(days=index * 3)).isoformat(),
                "test_name": test_name,
                "test_result": f"{result:.2f}",
                "result_unit": "score" if test_name == "MRD_SCORE" else "cells/uL",
            }
        )

    # Correctable format variations.
    records[3]["visit_name"] = "week4"
    records[7]["collection_date"] = "02/14/2026"
    records[11]["result_unit"] = "cells/ul"
    records[15]["subject_id"] = " SUBJ-004 "

    # Unresolved errors intentionally retained for quality-control testing.
    records[19]["subject_id"] = ""
    records[21]["sample_id"] = records[20]["sample_id"]
    records[23]["visit_name"] = "Month 6"
    records[25]["test_result"] = "not_available"
    records[26]["test_result"] = "125.00"
    records[29]["result_unit"] = "mg/dL"
    return records


def write_dataset(path: Path, count: int = 30, seed: int = 42) -> None:
    """Write the generated records to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(generate_records(count=count, seed=seed))
