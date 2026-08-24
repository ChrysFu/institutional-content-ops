"""Behavior tests for batch content scanning and report formats."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.content_scan import scan_paths, to_sarif

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONTENT_GUARD = REPOSITORY_ROOT / "src" / "content_guard.py"


class ContentScanTests(unittest.TestCase):
    def test_batch_scan_reports_rule_metadata_and_audit_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "ready.md").write_text("来源：会议纪要。", encoding="utf-8")
            (root / "blocked.md").write_text("这是绝对领先的成果。", encoding="utf-8")
            (root / "ignored.csv").write_text("绝对领先", encoding="utf-8")
            policy = {
                "required_terms": ["来源："],
                "forbidden_terms": [],
                "case_sensitive": True,
                "rules": [
                    {
                        "id": "CONTENT001",
                        "type": "regex",
                        "pattern": "绝对领先",
                        "severity": "error",
                        "message": "Avoid unqualified superlatives.",
                    }
                ],
            }

            result = scan_paths(
                [root],
                policy,
                audit_context={
                    "content_id": "campaign-42",
                    "revision": "7",
                    "policy_version": "2026-08",
                },
            )
            repeated = scan_paths(
                [root],
                policy,
                audit_context={
                    "content_id": "campaign-42",
                    "revision": "7",
                    "policy_version": "2026-08",
                },
            )

        self.assertFalse(result["ready_for_human_review"])
        self.assertFalse(result["release_approved"])
        self.assertEqual(result["summary"]["document_count"], 2)
        self.assertEqual(result["summary"]["error_count"], 2)
        self.assertTrue(all(not Path(document["path"]).is_absolute() for document in result["documents"]))
        self.assertEqual(result["audit"]["content_id"], "campaign-42")
        self.assertEqual(result["audit"]["revision"], "7")
        self.assertEqual(result["audit"]["policy_version"], "2026-08")
        self.assertRegex(result["audit"]["policy_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(result["audit"]["scan_id"], r"^[0-9a-f]{64}$")

        self.assertEqual(repeated["audit"]["scan_id"], result["audit"]["scan_id"])

        findings = [
            finding
            for document in result["documents"]
            for finding in document["findings"]
        ]
        self.assertEqual(
            {(finding["rule_id"], finding["severity"]) for finding in findings},
            {("content.required_term", "error"), ("CONTENT001", "error")},
        )
        regex_finding = next(finding for finding in findings if finding["rule_id"] == "CONTENT001")
        self.assertEqual(regex_finding["location"], {"line": 1, "column": 3})

    def test_warning_findings_do_not_block_human_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            draft = Path(temporary_directory) / "draft.md"
            draft.write_text("Maybe review this wording.", encoding="utf-8")

            result = scan_paths(
                [draft],
                {
                    "rules": [
                        {
                            "id": "STYLE001",
                            "type": "forbidden_term",
                            "term": "Maybe",
                            "severity": "warning",
                            "message": "Prefer direct wording.",
                        }
                    ]
                },
            )

        self.assertTrue(result["ready_for_human_review"])
        self.assertEqual(result["summary"]["warning_count"], 1)
        self.assertEqual(result["summary"]["error_count"], 0)

    def test_scan_id_is_independent_of_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "drafts" / "draft.md"
            source.parent.mkdir()
            source.write_text("Clear draft", encoding="utf-8")
            first = scan_paths([source], {})
            previous_directory = Path.cwd()
            try:
                os.chdir(source.parent)
                second = scan_paths([source], {})
            finally:
                os.chdir(previous_directory)

        self.assertEqual(first["audit"]["scan_id"], second["audit"]["scan_id"])
        self.assertEqual(first["documents"][0]["path"], "draft.md")

    def test_case_insensitive_location_preserves_original_unicode_offset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            draft = Path(temporary_directory) / "draft.md"
            draft.write_text("ßX", encoding="utf-8")

            result = scan_paths(
                [draft],
                {
                    "case_sensitive": False,
                    "rules": [
                        {
                            "id": "STYLE005",
                            "type": "forbidden_term",
                            "term": "x",
                            "severity": "warning",
                            "message": "Matched X.",
                        }
                    ],
                },
            )

        self.assertEqual(result["documents"][0]["findings"][0]["location"]["column"], 2)

    def test_sarif_report_uses_rule_ids_levels_and_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            draft = Path(temporary_directory) / "draft.md"
            draft.write_text("Internal only", encoding="utf-8")
            scan = scan_paths(
                [draft],
                {
                    "rules": [
                        {
                            "id": "POLICY007",
                            "type": "forbidden_term",
                            "term": "Internal",
                            "severity": "warning",
                            "message": "Remove internal-only wording.",
                        }
                    ]
                },
            )

            sarif = to_sarif(scan)

        self.assertEqual(sarif["version"], "2.1.0")
        run = sarif["runs"][0]
        self.assertEqual(run["tool"]["driver"]["name"], "institutional-content-ops")
        self.assertEqual(run["tool"]["driver"]["rules"][0]["id"], "POLICY007")
        self.assertEqual(run["results"][0]["ruleId"], "POLICY007")
        self.assertEqual(run["results"][0]["level"], "warning")
        region = run["results"][0]["locations"][0]["physicalLocation"]["region"]
        self.assertEqual(region, {"startLine": 1, "startColumn": 1})


class ContentScanCliTests(unittest.TestCase):
    def run_guard(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CONTENT_GUARD), *arguments],
            cwd=REPOSITORY_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_scans_directory_and_writes_sarif(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            drafts = root / "drafts"
            drafts.mkdir()
            (drafts / "one.md").write_text("[CHECK: source]", encoding="utf-8")
            output = root / "reports" / "content.sarif"

            completed = self.run_guard(
                "--scan",
                str(drafts),
                "--format",
                "sarif",
                "--output",
                str(output),
                "--content-id",
                "launch",
                "--revision",
                "3",
                "--policy-version",
                "v2",
                "--fail-on-issues",
            )

            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(payload["runs"][0]["properties"]["content_id"], "launch")

    def test_cli_fails_closed_when_scan_has_no_supported_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "ignored.csv").write_text("content", encoding="utf-8")

            completed = self.run_guard("--scan", str(root))

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "scan_no_documents")


if __name__ == "__main__":
    unittest.main()
