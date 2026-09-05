"""Copy generation. Every generated string is compliance-checked before it returns."""

from __future__ import annotations

from ..core import compliance


def generate(prompt: str, platform: str, *, variations: int = 3) -> list[str]:
    """Generate ad copy for one platform.

    Wire this to the Anthropic API. Whatever the model returns must pass through
    filter_compliant() before it reaches a file — the model is not the gate.
    """
    raise NotImplementedError("ai.copy.generate — not wired yet")


def filter_compliant(texts: list[str], platform: str) -> tuple[list[str], list[str]]:
    """Split generated copy into (usable, rejected-with-reason)."""
    usable: list[str] = []
    rejected: list[str] = []
    for text in texts:
        report = compliance.check_text(text, platform)
        if report.blocked:
            reasons = "; ".join(str(f) for f in report.findings)
            rejected.append(f"{text}\n  → {reasons}")
        else:
            usable.append(text)
    return usable, rejected
