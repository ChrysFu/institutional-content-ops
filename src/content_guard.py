"""Deterministic preflight checks before a draft enters human review."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import json
import os
from pathlib import Path
import re
import sys
import tempfile


CHECK_PATTERN = re.compile(r"\[CHECK(?::[^\]]+)?\]")
DEFAULT_DRAFT = "活动于 [CHECK: 日期] 举行，围绕已确认主题展开。"
DEFAULT_REQUIRED_TERMS = ("已确认主题",)
DEFAULT_FORBIDDEN_TERMS = ("行业第一", "绝对领先")
POLICY_KEYS = frozenset({"required_terms", "forbidden_terms", "case_sensitive"})


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

    required = list(required_terms)
    forbidden = list(forbidden_terms)
    searchable_draft = draft if case_sensitive else draft.casefold()

    def contains(term: str) -> bool:
        candidate = term if case_sensitive else term.casefold()
        return candidate in searchable_draft

    unresolved = CHECK_PATTERN.findall(draft)
    missing_terms = [term for term in required if not contains(term)]
    forbidden_hits = [term for term in forbidden if contains(term)]
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


def _validate_terms(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(term, str) or not term.strip() for term in value
    ):
        raise ContentGuardError(
            "invalid_policy",
            f"{field} must be a list of non-empty strings",
        )
    return value


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

    unknown_keys = sorted(set(policy) - POLICY_KEYS)
    if unknown_keys:
        raise ContentGuardError(
            "invalid_policy",
            f"unsupported policy keys: {', '.join(unknown_keys)}",
        )

    required_terms = _validate_terms(policy.get("required_terms", []), "required_terms")
    forbidden_terms = _validate_terms(policy.get("forbidden_terms", []), "forbidden_terms")
    case_sensitive = policy.get("case_sensitive", True)
    if not isinstance(case_sensitive, bool):
        raise ContentGuardError("invalid_policy", "case_sensitive must be a boolean")

    return {
        "required_terms": required_terms,
        "forbidden_terms": forbidden_terms,
        "case_sensitive": case_sensitive,
    }


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
    parser.add_argument("--draft", metavar="PATH", help="UTF-8 draft path, or - for standard input")
    parser.add_argument("--policy", type=Path, help="JSON file containing content policy terms")
    parser.add_argument("--output", type=Path, help="write JSON result atomically to this path")
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
        if args.draft is None:
            draft = DEFAULT_DRAFT
            policy = {
                "required_terms": list(DEFAULT_REQUIRED_TERMS),
                "forbidden_terms": list(DEFAULT_FORBIDDEN_TERMS),
                "case_sensitive": True,
            }
        else:
            draft = read_draft(args.draft)
            policy = load_policy(args.policy) if args.policy else {
                "required_terms": [],
                "forbidden_terms": [],
                "case_sensitive": True,
            }

        result = preflight(draft, **policy)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            write_result(args.output, payload)
        else:
            sys.stdout.write(payload)
        return 1 if args.fail_on_issues and not result["ready_for_human_review"] else 0
    except ContentGuardError as error:
        return _emit_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
