"""Meta (Facebook / Instagram) Marketing API.

Stage one: reads and drafts only. See policies/platforms/meta.md — the account
killer here is Personal Attributes, and Special Ad Category must be set for
credit, housing, employment and politics even when the copy is clean.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ...core import config, paths
from ..base import AdPlatform, InsightRow

SPECIAL_AD_CATEGORIES = {
    "credit": "CREDIT",
    "housing": "HOUSING",
    "employment": "EMPLOYMENT",
    "politics": "ISSUES_ELECTIONS_POLITICS",
}


class Platform(AdPlatform):
    name = "meta"

    def read_insights(
        self, since: date, until: date, level: str = "adset"
    ) -> list[InsightRow]:
        # TODO: facebook_business SDK — AdAccount(act_id).get_insights(...)
        raise NotImplementedError("meta.read_insights — not wired yet")

    def read_structure(self) -> dict[str, Any]:
        raise NotImplementedError("meta.read_structure — not wired yet")

    def build_payload(self, campaign: paths.Campaign, **kwargs: Any) -> dict[str, Any]:
        cfg = config.client(self.client_slug)
        categories = [
            SPECIAL_AD_CATEGORIES[c]
            for c in cfg.get("restricted_categories", [])
            if c in SPECIAL_AD_CATEGORIES
        ]
        return {
            "account_id": config.account_id(self.client_slug, self.name),
            "name": kwargs.get("name", campaign.slug),
            "objective": kwargs.get("objective", "OUTCOME_LEADS"),
            "status": "PAUSED",
            "special_ad_categories": categories,
            "daily_budget": kwargs.get("daily_budget"),
            "primary_text": kwargs.get("primary_text", ""),
            "headline": kwargs.get("headline", ""),
            "description": kwargs.get("description", ""),
        }

    def _execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("live writes are disabled in stage one")
