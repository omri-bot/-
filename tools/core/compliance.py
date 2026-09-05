"""Pre-flight policy enforcement.

Every piece of outgoing copy and every payload passes through here before it may
be written to drafts/. Rules live in policies/checks.yaml so that policy changes
do not require code changes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import yaml

from . import paths

BLOCK = "block"
WARN = "warn"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    excerpt: str
    reference: str

    def __str__(self) -> str:
        mark = "✗" if self.severity == BLOCK else "⚠"
        return f"{mark} [{self.rule_id}] {self.message} — \"{self.excerpt}\" ({self.reference})"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(f.severity == BLOCK for f in self.findings)

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == WARN]

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": not self.blocked,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "message": f.message,
                    "excerpt": f.excerpt,
                    "reference": f.reference,
                }
                for f in self.findings
            ],
        }


@lru_cache(maxsize=1)
def _policy() -> dict[str, Any]:
    with (paths.POLICIES / "checks.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _applies(rule: dict[str, Any], platform: str | None) -> bool:
    scope = rule.get("platforms", "all")
    if scope == "all":
        return True
    return platform is not None and platform in scope


def check_text(text: str, platform: str | None = None) -> Report:
    report = Report()
    for rule in _policy().get("rules", []):
        if not _applies(rule, platform):
            continue
        for pattern in rule.get("patterns", []):
            match = re.search(pattern, text)
            if match:
                report.findings.append(
                    Finding(
                        rule_id=rule["id"],
                        severity=rule.get("severity", BLOCK),
                        message=rule.get("message", ""),
                        excerpt=_excerpt(text, match),
                        reference=rule.get("reference", "policies/compliance.md"),
                    )
                )
                break
    return report


def check_fields(fields: dict[str, str], platform: str) -> Report:
    """Check per-field text and the platform's length limits."""
    report = Report()
    limits = _policy().get("limits", {}).get(platform, {})
    for name, value in fields.items():
        if not isinstance(value, str):
            continue
        report.findings.extend(check_text(value, platform).findings)
        limit = limits.get(name)
        if limit and len(value) > limit:
            report.findings.append(
                Finding(
                    rule_id="field_length",
                    severity=BLOCK,
                    message=f"{name}: {len(value)} תווים, המגבלה היא {limit}",
                    excerpt=value[:40],
                    reference=f"platforms/{platform}.md",
                )
            )
    return report


def _excerpt(text: str, match: re.Match[str], span: int = 20) -> str:
    start = max(0, match.start() - span)
    end = min(len(text), match.end() + span)
    return text[start:end].replace("\n", " ").strip()
