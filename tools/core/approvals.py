"""The single gate every state-changing platform call must pass through.

Stage one of this project is read + drafts: nothing is written live. An action is
proposed as a JSON draft, a human approves it, and only then may it execute.
See policies/approvals.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import compliance, config, paths


class ApprovalRequired(RuntimeError):
    """Raised when code attempts a live write without an approved draft."""


class ComplianceFailure(RuntimeError):
    """Raised when a payload fails policy checks. Fix the content, not the gate."""


def propose(
    campaign: paths.Campaign,
    action: str,
    platform: str,
    payload: dict[str, Any],
    rationale: str,
) -> Path:
    """Write an action to drafts/ after it passes compliance. Never executes."""
    report = compliance.check_fields(_texts(payload), platform)
    if report.blocked:
        raise ComplianceFailure(
            "הטיוטה נחסמה:\n" + "\n".join(str(f) for f in report.findings)
        )

    campaign.drafts.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    target = campaign.drafts / f"{stamp}-{platform}-{action}.json"
    target.write_text(
        json.dumps(
            {
                "action": action,
                "platform": platform,
                "client": campaign.client,
                "campaign": campaign.slug,
                "rationale": rationale,
                "compliance": report.as_dict(),
                "approved_by": None,
                "payload": payload,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return target


def require_approval(draft: Path) -> dict[str, Any]:
    """Load a draft and refuse unless a human approved it and live writes are on."""
    data = json.loads(draft.read_text(encoding="utf-8"))
    if not data.get("approved_by"):
        raise ApprovalRequired(
            f"{draft.name}: אין אישור אדם. ראה policies/approvals.md"
        )
    if not config.live_writes_allowed():
        raise ApprovalRequired(
            "ALLOW_LIVE_WRITES=false — כתיבה חיה מושבתת בשלב הנוכחי"
        )
    if not data.get("compliance", {}).get("passed"):
        raise ComplianceFailure(f"{draft.name}: הטיוטה לא עברה בדיקת ציות")
    return data


def _texts(payload: dict[str, Any]) -> dict[str, str]:
    return {k: v for k, v in payload.items() if isinstance(v, str)}
