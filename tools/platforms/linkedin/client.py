"""LinkedIn Marketing Developer Platform.

Stage one: reads and drafts only. See policies/platforms/linkedin.md — recruiting
ads must never reference age, gender or family status, in copy or in targeting.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ...core import config, paths
from ..base import AdPlatform, InsightRow


class Platform(AdPlatform):
    name = "linkedin"

    def read_insights(
        self, since: date, until: date, level: str = "adset"
    ) -> list[InsightRow]:
        # TODO: /rest/adAnalytics
        raise NotImplementedError("linkedin.read_insights — not wired yet")

    def read_structure(self) -> dict[str, Any]:
        raise NotImplementedError("linkedin.read_structure — not wired yet")

    def build_payload(self, campaign: paths.Campaign, **kwargs: Any) -> dict[str, Any]:
        return {
            "account": config.account_id(self.client_slug, self.name),
            "name": kwargs.get("name", campaign.slug),
            "objectiveType": kwargs.get("objective", "LEAD_GENERATION"),
            "status": "PAUSED",
            "dailyBudget": kwargs.get("daily_budget"),
            "intro_text": kwargs.get("intro_text", ""),
            "headline": kwargs.get("headline", ""),
        }

    def _execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("live writes are disabled in stage one")
