"""Validate local documentation links and JSON configuration files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
MARKDOWN_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ANCHOR_PATTERN = re.compile(r"<a\s+[^>]*id=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
NON_ANCHOR_CHARACTER_PATTERN = re.compile(r"[^\w\- ]", re.UNICODE)
IGNORED_DIRECTORIES = frozenset({".git", ".readme-architect", "__pycache__"})


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic repository validation finding."""

    code: str
    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.code}: {self.message}"


def _repository_files(root: Path, suffix: str) -> list[Path]:
    return sorted(
        path
        for path in root.rglob(f"*{suffix}")
        if not any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts)
    )


def _read_utf8(root: Path, document: Path) -> tuple[str | None, ValidationIssue | None]:
    try:
        return document.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as error:
        return None, ValidationIssue(
            "invalid_utf8",
            document.relative_to(root),
            f"byte {error.start}: {error.reason}",
        )
    except OSError as error:
        return None, ValidationIssue(
            "read_error",
            document.relative_to(root),
            str(error),
        )


def _validate_markdown(root: Path, document: Path, content: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    relative_document = document.relative_to(root)
    anchors = set(EXPLICIT_ANCHOR_PATTERN.findall(content))
    anchor_counts: dict[str, int] = {}
    for heading in MARKDOWN_HEADING_PATTERN.findall(content):
        base_anchor = NON_ANCHOR_CHARACTER_PATTERN.sub("", heading).strip().lower().replace(" ", "-")
        occurrence = anchor_counts.get(base_anchor, 0)
        anchors.add(base_anchor if occurrence == 0 else f"{base_anchor}-{occurrence}")
        anchor_counts[base_anchor] = occurrence + 1

    for raw_target in MARKDOWN_LINK_PATTERN.findall(content):
        target = raw_target.strip("<>")
        parsed = urlsplit(target)
        if target.startswith("#"):
            anchor = unquote(parsed.fragment)
            if anchor and anchor not in anchors:
                issues.append(
                    ValidationIssue(
                        "missing_local_anchor",
                        relative_document,
                        f"anchor does not exist: {target}",
                    )
                )
            continue
        if parsed.scheme or target.startswith(("/", "//")):
            continue
        local_path = unquote(parsed.path)
        if not local_path:
            continue
        resolved_target = (document.parent / local_path).resolve()
        try:
            resolved_target.relative_to(root.resolve())
        except ValueError:
            issues.append(
                ValidationIssue(
                    "local_target_outside_repository",
                    relative_document,
                    f"target escapes repository: {target}",
                )
            )
            continue
        if not resolved_target.exists():
            issues.append(
                ValidationIssue(
                    "missing_local_target",
                    relative_document,
                    f"target does not exist: {target}",
                )
            )
    return issues


def _validate_json(root: Path, document: Path, content: str) -> list[ValidationIssue]:
    try:
        json.loads(content)
    except json.JSONDecodeError as error:
        return [
            ValidationIssue(
                "invalid_json",
                document.relative_to(root),
                f"line {error.lineno}, column {error.colno}: {error.msg}",
            )
        ]
    return []


def validate_repository(root: Path) -> list[ValidationIssue]:
    """Return all deterministic validation findings under ``root``."""

    root = root.resolve()
    issues: list[ValidationIssue] = []
    for document in _repository_files(root, ".md"):
        content, read_issue = _read_utf8(root, document)
        if read_issue:
            issues.append(read_issue)
        else:
            assert content is not None
            issues.extend(_validate_markdown(root, document, content))
    for document in _repository_files(root, ".json"):
        content, read_issue = _read_utf8(root, document)
        if read_issue:
            issues.append(read_issue)
        else:
            assert content is not None
            issues.extend(_validate_json(root, document, content))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.message))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()

    issues = validate_repository(args.root)
    for issue in issues:
        print(issue)
    if issues:
        print(f"repository-checks: failed ({len(issues)} issue(s))")
        return 1
    print("repository-checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
