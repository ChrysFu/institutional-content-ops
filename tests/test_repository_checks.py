"""Behavior tests for repository-level documentation checks."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.repository_checks import validate_repository


class RepositoryCheckTests(unittest.TestCase):
    def test_reports_missing_local_markdown_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "[missing](docs/missing.md)\n![missing image](assets/missing.svg)\n",
                encoding="utf-8",
            )

            issues = validate_repository(root)

        self.assertEqual(len(issues), 2)
        self.assertTrue(all(issue.code == "missing_local_target" for issue in issues))

    def test_ignores_external_mail_and_same_document_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "[web](https://example.org) [mail](mailto:team@example.org) [section](#usage)\n",
                encoding="utf-8",
            )

            issues = validate_repository(root)

        self.assertEqual(issues, [])

    def test_reports_invalid_json_with_location(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "policy.json").write_text('{"required_terms": [}', encoding="utf-8")

            issues = validate_repository(root)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "invalid_json")
        self.assertEqual(issues[0].path, Path("policy.json"))

    def test_reports_non_utf8_documents_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "broken.md").write_bytes(b"\xff")
            (root / "broken.json").write_bytes(b"\xff")

            issues = validate_repository(root)

        self.assertEqual(
            [(issue.path, issue.code) for issue in issues],
            [
                (Path("broken.json"), "invalid_utf8"),
                (Path("broken.md"), "invalid_utf8"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
