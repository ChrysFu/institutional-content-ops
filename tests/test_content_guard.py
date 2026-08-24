"""Behavior tests for the content preflight interface and CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.content_guard import preflight

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONTENT_GUARD = REPOSITORY_ROOT / "src" / "content_guard.py"


class PreflightTests(unittest.TestCase):
    def test_existing_preflight_contract_remains_compatible(self) -> None:
        result = preflight(
            "活动于 [CHECK: 日期] 举行。",
            required_terms=["已确认主题"],
            forbidden_terms=["行业第一"],
        )

        self.assertFalse(result["ready_for_human_review"])
        self.assertFalse(result["release_approved"])
        self.assertEqual(
            result["issues"],
            {
                "unresolved_checks": ["[CHECK: 日期]"],
                "missing_required_terms": ["已确认主题"],
                "forbidden_term_hits": [],
            },
        )

    def test_case_insensitive_policy_is_explicit_and_summarized(self) -> None:
        result = preflight(
            "Approved release with INTERNAL note.",
            required_terms=["approved"],
            forbidden_terms=["internal"],
            case_sensitive=False,
        )

        self.assertFalse(result["ready_for_human_review"])
        self.assertEqual(result["issues"]["missing_required_terms"], [])
        self.assertEqual(result["issues"]["forbidden_term_hits"], ["internal"])
        self.assertEqual(
            result["summary"],
            {
                "issue_count": 1,
                "unresolved_check_count": 0,
                "missing_required_term_count": 0,
                "forbidden_term_hit_count": 1,
            },
        )


class ContentGuardCliTests(unittest.TestCase):
    def run_guard(self, *arguments: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CONTENT_GUARD), *arguments],
            cwd=REPOSITORY_ROOT,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_reads_draft_and_policy_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            draft = directory / "draft.md"
            policy = directory / "policy.json"
            draft.write_text("活动围绕已确认主题举行。", encoding="utf-8")
            policy.write_text(
                json.dumps(
                    {
                        "required_terms": ["已确认主题"],
                        "forbidden_terms": ["行业第一"],
                        "case_sensitive": True,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            completed = self.run_guard("--draft", str(draft), "--policy", str(policy))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ready_for_human_review"])
        self.assertFalse(payload["release_approved"])

    def test_cli_can_fail_a_pipeline_when_issues_remain(self) -> None:
        completed = self.run_guard("--draft", "-", "--fail-on-issues", stdin="[CHECK]")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["ready_for_human_review"])
        self.assertFalse(payload["release_approved"])

    def test_cli_writes_result_to_a_nested_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "artifacts" / "preflight.json"

            completed = self.run_guard("--draft", "-", "--output", str(output), stdin="clear draft")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stdout, "")
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["ready_for_human_review"])
        self.assertFalse(payload["release_approved"])

    def test_failed_output_write_does_not_leave_a_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            output = directory / "existing-directory"
            output.mkdir()

            completed = self.run_guard("--draft", "-", "--output", str(output), stdin="draft")
            temporary_files = list(directory.glob(".existing-directory.*.tmp"))

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "output_write_error")
        self.assertEqual(temporary_files, [])

    def test_cli_reports_missing_input_as_structured_error(self) -> None:
        completed = self.run_guard("--draft", "missing-draft.md")

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "draft_not_found")
        self.assertFalse(payload["ready_for_human_review"])
        self.assertFalse(payload["release_approved"])

    def test_cli_rejects_invalid_policy_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            policy = Path(temporary_directory) / "policy.json"
            policy.write_text('{"required_terms": "not-a-list"}', encoding="utf-8")

            completed = self.run_guard("--draft", "-", "--policy", str(policy), stdin="draft")

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "invalid_policy")

    def test_cli_reports_non_utf8_policy_as_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            policy = Path(temporary_directory) / "policy.json"
            policy.write_bytes(b"\xff")

            completed = self.run_guard("--draft", "-", "--policy", str(policy), stdin="draft")

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stderr)
        self.assertEqual(payload["error"]["code"], "policy_encoding_error")

    def test_cli_rejects_invalid_structured_rules(self) -> None:
        invalid_rules = {
            "duplicate IDs": [
                {
                    "id": "STYLE001",
                    "type": "forbidden_term",
                    "term": "maybe",
                    "severity": "warning",
                    "message": "Use direct wording.",
                },
                {
                    "id": "STYLE001",
                    "type": "required_term",
                    "term": "source",
                    "severity": "error",
                    "message": "Add a source.",
                },
            ],
            "invalid regex": [
                {
                    "id": "STYLE002",
                    "type": "regex",
                    "pattern": "[",
                    "severity": "warning",
                    "message": "Invalid pattern.",
                }
            ],
            "invalid severity": [
                {
                    "id": "STYLE003",
                    "type": "forbidden_term",
                    "term": "maybe",
                    "severity": "critical",
                    "message": "Use direct wording.",
                }
            ],
            "unexpected field": [
                {
                    "id": "STYLE004",
                    "type": "forbidden_term",
                    "term": "maybe",
                    "severity": "warning",
                    "message": "Use direct wording.",
                    "replacement": "will",
                }
            ],
            "reserved ID": [
                {
                    "id": "content.unresolved_check",
                    "type": "forbidden_term",
                    "term": "maybe",
                    "severity": "warning",
                    "message": "Use direct wording.",
                }
            ],
        }

        for label, rules in invalid_rules.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary_directory:
                directory = Path(temporary_directory)
                draft = directory / "draft.md"
                policy = directory / "policy.json"
                draft.write_text("draft", encoding="utf-8")
                policy.write_text(json.dumps({"rules": rules}), encoding="utf-8")

                completed = self.run_guard(
                    "--scan",
                    str(draft),
                    "--policy",
                    str(policy),
                )

            self.assertEqual(completed.returncode, 2)
            payload = json.loads(completed.stderr)
            self.assertEqual(payload["error"]["code"], "invalid_policy")

    def test_cli_applies_structured_rules_in_legacy_draft_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            policy = directory / "policy.json"
            policy.write_text(
                json.dumps(
                    {
                        "rules": [
                            {
                                "id": "CLAIM009",
                                "type": "regex",
                                "pattern": "always best",
                                "severity": "error",
                                "message": "Substantiate the claim.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            completed = self.run_guard(
                "--draft",
                "-",
                "--policy",
                str(policy),
                "--fail-on-issues",
                stdin="We are always best.",
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["findings"][0]["rule_id"], "CLAIM009")
        self.assertFalse(payload["ready_for_human_review"])
        self.assertFalse(payload["release_approved"])


if __name__ == "__main__":
    unittest.main()
