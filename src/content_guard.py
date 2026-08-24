"""Deterministic preflight checks before a draft enters human review."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Iterable, Sequence
from pathlib import Path

try:
    from .content_scan import ContentScanError, normalize_policy, scan_content, scan_paths, to_sarif
except ImportError:  # Support direct execution: python src/content_guard.py
    from content_scan import ContentScanError, normalize_policy, scan_content, scan_paths, to_sarif


DEFAULT_DRAFT = "活动于 [CHECK: 日期] 举行，围绕已确认主题展开。"
DEFAULT_REQUIRED_TERMS = ("已确认主题",)
DEFAULT_FORBIDDEN_TERMS = ("行业第一", "绝对领先")


class ContentGuardError(Exception):
    """An expected input, policy, or output failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def preflight(
    draft: str,
    *,
    required_terms: Iterable[str] = (),
    forbidden_terms: Iterable[str] = (),
    case_sensitive: bool = True,
) -> dict[str, object]:
    """Evaluate a draft without granting publication approval.

    Term matching remains case-sensitive by default for backward compatibility.
    Callers may opt into Unicode-aware case-insensitive matching.
    """

    findings = scan_content(
        draft,
        {
            "required_terms": list(required_terms),
            "forbidden_terms": list(forbidden_terms),
            "case_sensitive": case_sensitive,
        },
    )
    return _legacy_result(findings)


def _legacy_result(findings: Sequence[dict[str, object]]) -> dict[str, object]:
    unresolved = [
        finding["value"]
        for finding in findings
        if finding["rule_id"] == "content.unresolved_check"
    ]
    missing_terms = [
        finding["value"]
        for finding in findings
        if finding["rule_id"] == "content.required_term"
    ]
    forbidden_hits = [
        finding["value"]
        for finding in findings
        if finding["rule_id"] == "content.forbidden_term"
    ]
    issues = {
        "unresolved_checks": unresolved,
        "missing_required_terms": missing_terms,
        "forbidden_term_hits": forbidden_hits,
    }
    summary = {
        "issue_count": sum(len(values) for values in issues.values()),
        "unresolved_check_count": len(unresolved),
        "missing_required_term_count": len(missing_terms),
        "forbidden_term_hit_count": len(forbidden_hits),
    }
    return {
        "ready_for_human_review": not any(issues.values()),
        "issues": issues,
        "summary": summary,
        "release_approved": False,
    }


def load_policy(path: Path) -> dict[str, object]:
    """Load and validate a JSON policy used by the command-line adapter."""

    try:
        raw_policy = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ContentGuardError("policy_not_found", f"policy file not found: {path}") from error
    except UnicodeDecodeError as error:
        raise ContentGuardError(
            "policy_encoding_error",
            f"policy is not valid UTF-8: {path}",
        ) from error
    except OSError as error:
        raise ContentGuardError("policy_read_error", f"cannot read policy file: {path}") from error

    try:
        policy = json.loads(raw_policy)
    except json.JSONDecodeError as error:
        raise ContentGuardError(
            "invalid_policy",
            f"policy is not valid JSON at line {error.lineno}, column {error.colno}",
        ) from error

    if not isinstance(policy, dict):
        raise ContentGuardError("invalid_policy", "policy must be a JSON object")

    try:
        return normalize_policy(policy)
    except ContentScanError as error:
        raise ContentGuardError(error.code, str(error)) from error


def read_draft(source: str) -> str:
    """Read a UTF-8 draft from a file path or standard input (`-`)."""

    if source == "-":
        return sys.stdin.read()

    path = Path(source)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ContentGuardError("draft_not_found", f"draft file not found: {path}") from error
    except UnicodeDecodeError as error:
        raise ContentGuardError("draft_encoding_error", f"draft is not valid UTF-8: {path}") from error
    except OSError as error:
        raise ContentGuardError("draft_read_error", f"cannot read draft file: {path}") from error


def write_result(path: Path, payload: str) -> None:
    """Atomically write a JSON result so interrupted runs do not leave partial data."""

    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(payload)
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise ContentGuardError("output_write_error", f"cannot write result file: {path}") from error


def run_self_test() -> None:
    blocked = preflight(
        "活动于 [CHECK: 日期] 举行。",
        required_terms=["已确认主题"],
        forbidden_terms=["行业第一"],
    )
    assert blocked["ready_for_human_review"] is False
    clear = preflight("活动围绕已确认主题举行。", required_terms=["已确认主题"])
    assert clear["ready_for_human_review"] is True
    assert clear["release_approved"] is False


def _emit_error(error: ContentGuardError) -> int:
    payload = {
        "error": {"code": error.code, "message": str(error)},
        "ready_for_human_review": False,
        "release_approved": False,
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    return 2


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run built-in smoke checks")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--draft", metavar="PATH", help="UTF-8 draft path, or - for standard input")
    inputs.add_argument(
        "--scan",
        metavar="PATH",
        action="append",
        help="scan a UTF-8 Markdown/text file or directory; repeat for multiple sources",
    )
    parser.add_argument("--policy", type=Path, help="JSON file containing content policy terms")
    parser.add_argument("--format", choices=("json", "sarif"), default="json")
    parser.add_argument("--content-id", default="", help="content identifier recorded in scan audit data")
    parser.add_argument("--revision", default="", help="content revision recorded in scan audit data")
    parser.add_argument("--policy-version", default="", help="policy version recorded in scan audit data")
    parser.add_argument("--output", type=Path, help="write the result atomically to this path")
    parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="return exit code 1 when the draft is not ready for human review",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.self_test:
        run_self_test()
        print("self-test: ok")
        return 0

    try:
        if args.scan:
            policy = load_policy(args.policy) if args.policy else normalize_policy({})
            result = scan_paths(
                args.scan,
                policy,
                audit_context={
                    "content_id": args.content_id,
                    "revision": args.revision,
                    "policy_version": args.policy_version,
                },
            )
            report = to_sarif(result) if args.format == "sarif" else result
        elif args.draft is None:
            draft = DEFAULT_DRAFT
            policy = {
                "required_terms": list(DEFAULT_REQUIRED_TERMS),
                "forbidden_terms": list(DEFAULT_FORBIDDEN_TERMS),
                "case_sensitive": True,
            }
            result = preflight(draft, **policy)
            report = result
        else:
            draft = read_draft(args.draft)
            policy = load_policy(args.policy) if args.policy else normalize_policy({})
            findings = scan_content(draft, policy)
            result = _legacy_result(findings)
            custom_rule_ids = {rule["id"] for rule in policy["rules"]}
            custom_findings = [
                finding for finding in findings if finding["rule_id"] in custom_rule_ids
            ]
            if custom_findings:
                result["findings"] = custom_findings
                result["summary"]["rule_finding_count"] = len(custom_findings)
                result["summary"]["issue_count"] += len(custom_findings)
                result["ready_for_human_review"] = result["ready_for_human_review"] and not any(
                    finding["severity"] == "error" for finding in custom_findings
                )
            report = result

        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            write_result(args.output, payload)
        else:
            sys.stdout.write(payload)
        return 1 if args.fail_on_issues and not result["ready_for_human_review"] else 0
    except ContentScanError as error:
        return _emit_error(ContentGuardError(error.code, str(error)))
    except ContentGuardError as error:
        return _emit_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
