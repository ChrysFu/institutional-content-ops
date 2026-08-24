"""Batch content scanning with stable findings, audit metadata, and SARIF output."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import quote

CHECK_PATTERN = re.compile(r"\[CHECK(?::[^\]]+)?\]")
SUPPORTED_SUFFIXES = frozenset({".md", ".txt"})
SEVERITIES = frozenset({"error", "warning", "note"})
RULE_TYPES = frozenset({"required_term", "forbidden_term", "regex"})
RULE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
RESERVED_RULE_IDS = frozenset(
    {
        "content.unresolved_check",
        "content.required_term",
        "content.forbidden_term",
    }
)
POLICY_KEYS = frozenset({"required_terms", "forbidden_terms", "case_sensitive", "rules"})
COMMON_RULE_KEYS = frozenset({"id", "type", "severity", "message"})


class ContentScanError(Exception):
    """An expected scan input or policy failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _validate_terms(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(term, str) or not term.strip() for term in value
    ):
        raise ContentScanError("invalid_policy", f"{field} must be a list of non-empty strings")
    return list(value)


def _validate_rule(raw_rule: object, index: int) -> dict[str, str]:
    if not isinstance(raw_rule, dict):
        raise ContentScanError("invalid_policy", f"rules[{index}] must be an object")

    rule_type = raw_rule.get("type")
    if rule_type not in RULE_TYPES:
        raise ContentScanError(
            "invalid_policy",
            f"rules[{index}].type must be one of: {', '.join(sorted(RULE_TYPES))}",
        )

    value_key = "pattern" if rule_type == "regex" else "term"
    allowed_keys = COMMON_RULE_KEYS | {value_key}
    unknown_keys = sorted(set(raw_rule) - allowed_keys)
    missing_keys = sorted(allowed_keys - set(raw_rule))
    if unknown_keys:
        raise ContentScanError(
            "invalid_policy",
            f"rules[{index}] has unsupported fields: {', '.join(unknown_keys)}",
        )
    if missing_keys:
        raise ContentScanError(
            "invalid_policy",
            f"rules[{index}] is missing fields: {', '.join(missing_keys)}",
        )

    for field in ("id", "severity", "message", value_key):
        value = raw_rule[field]
        if not isinstance(value, str) or not value.strip():
            raise ContentScanError(
                "invalid_policy",
                f"rules[{index}].{field} must be a non-empty string",
            )

    rule_id = raw_rule["id"]
    severity = raw_rule["severity"]
    if not RULE_ID_PATTERN.fullmatch(rule_id):
        raise ContentScanError("invalid_policy", f"rules[{index}].id is not a valid rule ID")
    if rule_id in RESERVED_RULE_IDS:
        raise ContentScanError("invalid_policy", f"rules[{index}].id is reserved: {rule_id}")
    if severity not in SEVERITIES:
        raise ContentScanError(
            "invalid_policy",
            f"rules[{index}].severity must be one of: {', '.join(sorted(SEVERITIES))}",
        )
    if rule_type == "regex":
        try:
            re.compile(raw_rule["pattern"])
        except re.error as error:
            raise ContentScanError(
                "invalid_policy",
                f"rules[{index}].pattern is invalid: {error}",
            ) from error

    return {key: raw_rule[key] for key in sorted(allowed_keys)}


def normalize_policy(policy: Mapping[str, object]) -> dict[str, object]:
    """Validate and normalize a policy for deterministic evaluation."""

    if not isinstance(policy, Mapping):
        raise ContentScanError("invalid_policy", "policy must be a JSON object")
    unknown_keys = sorted(set(policy) - POLICY_KEYS)
    if unknown_keys:
        raise ContentScanError(
            "invalid_policy",
            f"unsupported policy keys: {', '.join(unknown_keys)}",
        )

    required_terms = _validate_terms(policy.get("required_terms", []), "required_terms")
    forbidden_terms = _validate_terms(policy.get("forbidden_terms", []), "forbidden_terms")
    case_sensitive = policy.get("case_sensitive", True)
    if not isinstance(case_sensitive, bool):
        raise ContentScanError("invalid_policy", "case_sensitive must be a boolean")

    raw_rules = policy.get("rules", [])
    if not isinstance(raw_rules, list):
        raise ContentScanError("invalid_policy", "rules must be a list of rule objects")
    rules = [_validate_rule(rule, index) for index, rule in enumerate(raw_rules)]
    rule_ids = [rule["id"] for rule in rules]
    duplicate_ids = sorted({rule_id for rule_id in rule_ids if rule_ids.count(rule_id) > 1})
    if duplicate_ids:
        raise ContentScanError(
            "invalid_policy",
            f"rule IDs must be unique: {', '.join(duplicate_ids)}",
        )

    return {
        "required_terms": required_terms,
        "forbidden_terms": forbidden_terms,
        "case_sensitive": case_sensitive,
        "rules": rules,
    }


def _source_documents(sources: Sequence[str | Path]) -> tuple[Path, list[Path]]:
    documents: set[Path] = set()
    source_parents: list[Path] = []
    for raw_source in sources:
        source = Path(raw_source).resolve()
        if not source.exists():
            raise ContentScanError("scan_source_not_found", f"scan source not found: {source}")
        source_parents.append(source.parent)
        if source.is_dir():
            documents.update(
                candidate.resolve()
                for candidate in source.rglob("*")
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES
            )
        elif source.is_file() and source.suffix.lower() in SUPPORTED_SUFFIXES:
            documents.add(source.resolve())
        elif not source.is_file():
            raise ContentScanError("scan_source_invalid", f"scan source is not a file: {source}")
    if not documents:
        raise ContentScanError(
            "scan_no_documents",
            "scan sources contain no supported .md or .txt documents",
        )
    scan_root = Path(os.path.commonpath(source_parents))
    return scan_root, sorted(documents, key=lambda path: path.as_posix())


def _location(content: str, offset: int) -> dict[str, int]:
    line = content.count("\n", 0, offset) + 1
    previous_newline = content.rfind("\n", 0, offset)
    column = offset + 1 if previous_newline < 0 else offset - previous_newline
    return {"line": line, "column": column}


def _report_path(path: Path, scan_root: Path) -> str:
    return path.relative_to(scan_root).as_posix()


def _find_offset(content: str, value: str, case_sensitive: bool) -> int:
    if case_sensitive:
        return content.find(value)
    folded_content: list[str] = []
    original_offsets: list[int] = []
    for original_offset, character in enumerate(content):
        folded_character = character.casefold()
        folded_content.append(folded_character)
        original_offsets.extend([original_offset] * len(folded_character))
    folded_offset = "".join(folded_content).find(value.casefold())
    return original_offsets[folded_offset] if folded_offset >= 0 else -1


def _finding(
    rule_id: str,
    severity: str,
    message: str,
    *,
    location: dict[str, int] | None = None,
    value: str | None = None,
) -> dict[str, object]:
    finding: dict[str, object] = {
        "rule_id": rule_id,
        "severity": severity,
        "message": message,
    }
    if location is not None:
        finding["location"] = location
    if value is not None:
        finding["value"] = value
    return finding


def _evaluate_document(content: str, policy: Mapping[str, object]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    case_sensitive = bool(policy["case_sensitive"])

    for match in CHECK_PATTERN.finditer(content):
        findings.append(
            _finding(
                "content.unresolved_check",
                "error",
                f"Resolve verification marker: {match.group(0)}",
                location=_location(content, match.start()),
                value=match.group(0),
            )
        )

    for term in policy["required_terms"]:
        assert isinstance(term, str)
        if _find_offset(content, term, case_sensitive) < 0:
            findings.append(
                _finding(
                    "content.required_term",
                    "error",
                    f"Required term is missing: {term}",
                    value=term,
                )
            )

    for term in policy["forbidden_terms"]:
        assert isinstance(term, str)
        offset = _find_offset(content, term, case_sensitive)
        if offset >= 0:
            findings.append(
                _finding(
                    "content.forbidden_term",
                    "error",
                    f"Forbidden term found: {term}",
                    location=_location(content, offset),
                    value=term,
                )
            )

    for rule in policy["rules"]:
        assert isinstance(rule, dict)
        rule_type = rule["type"]
        if rule_type == "required_term":
            offset = _find_offset(content, rule["term"], case_sensitive)
            if offset < 0:
                findings.append(_finding(rule["id"], rule["severity"], rule["message"]))
        elif rule_type == "forbidden_term":
            offset = _find_offset(content, rule["term"], case_sensitive)
            if offset >= 0:
                findings.append(
                    _finding(
                        rule["id"],
                        rule["severity"],
                        rule["message"],
                        location=_location(content, offset),
                    )
                )
        else:
            flags = 0 if case_sensitive else re.IGNORECASE
            for match in re.finditer(rule["pattern"], content, flags):
                findings.append(
                    _finding(
                        rule["id"],
                        rule["severity"],
                        rule["message"],
                        location=_location(content, match.start()),
                    )
                )

    return findings


def scan_content(content: str, policy: Mapping[str, object]) -> list[dict[str, object]]:
    """Evaluate in-memory content through the canonical rule engine."""

    return _evaluate_document(content, normalize_policy(policy))


def _rule_catalog(policy: Mapping[str, object]) -> list[dict[str, str]]:
    catalog = [
        {
            "id": rule["id"],
            "type": rule["type"],
            "severity": rule["severity"],
            "message": rule["message"],
        }
        for rule in policy["rules"]
    ]
    if policy["required_terms"]:
        catalog.append(
            {
                "id": "content.required_term",
                "type": "required_term",
                "severity": "error",
                "message": "Include every required policy term.",
            }
        )
    if policy["forbidden_terms"]:
        catalog.append(
            {
                "id": "content.forbidden_term",
                "type": "forbidden_term",
                "severity": "error",
                "message": "Remove forbidden policy terms.",
            }
        )
    catalog.append(
        {
            "id": "content.unresolved_check",
            "type": "regex",
            "severity": "error",
            "message": "Resolve verification markers before human review.",
        }
    )
    return catalog


def scan_paths(
    sources: Sequence[str | Path],
    policy: Mapping[str, object],
    audit_context: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Scan supported files under ``sources`` and return a deterministic report."""

    normalized_policy = normalize_policy(policy)
    documents: list[dict[str, object]] = []
    scan_root, source_documents = _source_documents(sources)
    for path in source_documents:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise ContentScanError(
                "scan_encoding_error",
                f"scan source is not valid UTF-8: {path}",
            ) from error
        except OSError as error:
            raise ContentScanError("scan_read_error", f"cannot read scan source: {path}") from error
        findings = _evaluate_document(content, normalized_policy)
        report_path = _report_path(path, scan_root)
        documents.append(
            {
                "path": report_path,
                "sha256": _sha256_text(content),
                "ready_for_human_review": not any(
                    finding["severity"] == "error" for finding in findings
                ),
                "findings": findings,
            }
        )

    all_findings = [finding for document in documents for finding in document["findings"]]
    summary = {
        "document_count": len(documents),
        "finding_count": len(all_findings),
        "error_count": sum(finding["severity"] == "error" for finding in all_findings),
        "warning_count": sum(finding["severity"] == "warning" for finding in all_findings),
        "note_count": sum(finding["severity"] == "note" for finding in all_findings),
    }
    policy_sha256 = _sha256_text(_canonical_json(normalized_policy))
    supplied_audit = dict(audit_context or {})
    audit = {
        "content_id": str(supplied_audit.get("content_id", "")),
        "revision": str(supplied_audit.get("revision", "")),
        "policy_version": str(supplied_audit.get("policy_version", "")),
        "policy_sha256": policy_sha256,
    }
    scan_identity = {
        "audit": audit,
        "documents": [
            {"path": document["path"], "sha256": document["sha256"]} for document in documents
        ],
    }
    audit["scan_id"] = _sha256_text(_canonical_json(scan_identity))
    return {
        "ready_for_human_review": summary["error_count"] == 0,
        "release_approved": False,
        "summary": summary,
        "audit": audit,
        "rules": _rule_catalog(normalized_policy),
        "documents": documents,
    }


def to_sarif(scan: Mapping[str, Any]) -> dict[str, object]:
    """Convert a scan report to SARIF 2.1.0 for code-scanning consumers."""

    rules = [
        {
            "id": rule["id"],
            "name": rule["id"],
            "shortDescription": {"text": rule["message"]},
            "defaultConfiguration": {"level": rule["severity"]},
            "properties": {"type": rule["type"]},
        }
        for rule in scan["rules"]
    ]
    results: list[dict[str, object]] = []
    for document in scan["documents"]:
        for finding in document["findings"]:
            result: dict[str, object] = {
                "ruleId": finding["rule_id"],
                "level": finding["severity"],
                "message": {"text": finding["message"]},
            }
            physical_location: dict[str, object] = {
                "artifactLocation": {"uri": quote(document["path"], safe="/.:_-~")}
            }
            if "location" in finding:
                physical_location["region"] = {
                    "startLine": finding["location"]["line"],
                    "startColumn": finding["location"]["column"],
                }
            result["locations"] = [{"physicalLocation": physical_location}]
            results.append(result)

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "institutional-content-ops",
                        "informationUri": "https://github.com/ChrysFu/institutional-content-ops",
                        "rules": rules,
                    }
                },
                "properties": dict(scan["audit"]),
                "results": results,
            }
        ],
    }
