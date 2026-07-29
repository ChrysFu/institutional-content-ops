"""Deterministic preflight checks before a draft enters human review."""

from __future__ import annotations

import argparse
import json
import re
from typing import Iterable


CHECK_PATTERN = re.compile(r"\[CHECK(?::[^\]]+)?\]")


def preflight(
    draft: str,
    *,
    required_terms: Iterable[str] = (),
    forbidden_terms: Iterable[str] = (),
) -> dict[str, object]:
    unresolved = CHECK_PATTERN.findall(draft)
    missing_terms = [term for term in required_terms if term not in draft]
    forbidden_hits = [term for term in forbidden_terms if term in draft]
    issues = {
        "unresolved_checks": unresolved,
        "missing_required_terms": missing_terms,
        "forbidden_term_hits": forbidden_hits,
    }
    return {
        "ready_for_human_review": not any(issues.values()),
        "issues": issues,
        "release_approved": False,
    }


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("self-test: ok")
        return

    result = preflight(
        "活动于 [CHECK: 日期] 举行，围绕已确认主题展开。",
        required_terms=["已确认主题"],
        forbidden_terms=["行业第一", "绝对领先"],
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
