"""Unit tests for core TrialFlow validation behavior."""

import unittest
from pathlib import Path

from src.generate_synthetic_data import generate_records
from src.pipeline import load_rules, process_records


PROJECT_DIR = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = load_rules(PROJECT_DIR / "config" / "sponsor_dta_rules.json")

    def test_known_format_variations_are_corrected(self) -> None:
        rows, _, audit = process_records(generate_records(), self.rules)
        self.assertEqual(rows[3]["visit_name"], "Week 4")
        self.assertEqual(rows[7]["collection_date"], "2026-02-14")
        self.assertEqual(rows[11]["result_unit"], "cells/uL")
        self.assertGreaterEqual(len(audit), 4)

    def test_invalid_records_fail(self) -> None:
        rows, issues, _ = process_records(generate_records(), self.rules)
        self.assertEqual(rows[19]["validation_status"], "FAIL")
        self.assertTrue(any(issue["rule"] == "numeric" for issue in issues))
        self.assertTrue(any(issue["rule"] == "result_range" for issue in issues))

    def test_sponsor_ready_rows_have_no_issues(self) -> None:
        rows, _, _ = process_records(generate_records(), self.rules)
        passing = [row for row in rows if row["validation_status"] == "PASS"]
        self.assertTrue(passing)
        self.assertTrue(all(row["issue_count"] == 0 for row in passing))


if __name__ == "__main__":
    unittest.main()

