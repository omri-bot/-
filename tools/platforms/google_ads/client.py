"""Google Ads API.

Stage one: reads and drafts only. See policies/platforms/google-ads.md —
Misrepresentation is what suspends accounts here, and the landing page is part
of what gets reviewed.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ...core import config, paths
from ..base import AdPlatform, InsightRow


class Platform(AdPlatform):
    name = "google_ads"

    def read_insights(
        self, since: date, until: date, level: str = "adset"
    ) -> list[InsightRow]:
        # TODO: GoogleAdsService.search_stream with a GAQL query
        raise NotImplementedError("google_ads.read_insights — not wired yet")

    def read_structure(self) -> dict[str, Any]:
        raise NotImplementedError("google_ads.read_structure — not wired yet")

    def build_payload(self, campaign: paths.Campaign, **kwargs: Any) -> dict[str, Any]:
        return {
            "customer_id": config.account_id(self.client_slug, self.name),
            "name": kwargs.get("name", campaign.slug),
            "advertising_channel_type": kwargs.get("channel", "SEARCH"),
            "status": "PAUSED",
            "daily_budget_micros": kwargs.get("daily_budget_micros"),
            "headline": kwargs.get("headline", ""),
            "description": kwargs.get("description", ""),
        }

    def _execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("live writes are disabled in stage one")
