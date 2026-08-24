# Domain Glossary

## Rule

A named content requirement with a stable identifier and severity. A Rule states what must be present or what must not be present; it does not approve publication.

## Finding

Evidence that one Rule was triggered for one document. A Finding identifies the Rule, severity, message, document, and location when a concrete location exists.

## Scan

The deterministic evaluation of one or more documents against one policy. A Scan is ready for human review only when it contains no blocking Findings.

## Audit Context

Caller-supplied traceability data that associates a Scan with a content item, revision, and policy version. Audit Context records provenance but does not change rule evaluation.
