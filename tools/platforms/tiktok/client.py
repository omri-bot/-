"""TikTok Business API.

Stage one: reads and drafts only. See policies/platforms/tiktok.md — creative
quality is a policy condition here, and health/appearance rules are stricter
than on any other network.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ...core import config, paths
from ..base import AdPlatform, InsightRow


class Platform(AdPlatform):
    name = "tiktok"

    def read_insights(
        self, since: date, until: date, level: str = "adset"
    ) -> list[InsightRow]:
        # TODO: /open_api/v1.3/report/integrated/get/
        raise NotImplementedError("tiktok.read_insights — not wired yet")

    def read_structure(self) -> dict[str, Any]:
        raise NotImplementedError("tiktok.read_structure — not wired yet")

    def build_payload(self, campaign: paths.Campaign, **kwargs: Any) -> dict[str, Any]:
        return {
            "advertiser_id": config.account_id(self.client_slug, self.name),
            "campaign_name": kwargs.get("name", campaign.slug),
            "objective_type": kwargs.get("objective", "LEAD_GENERATION"),
            "operation_status": "DISABLE",  # TikTok's PAUSED
            "budget": kwargs.get("daily_budget"),
            "ad_text": kwargs.get("ad_text", ""),
        }

    def _execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("live writes are disabled in stage one")
