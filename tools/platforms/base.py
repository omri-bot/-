"""One interface for all four networks.

Adding a fifth network means adding a directory, not teaching every agent a new
API. Reads are free; writes go through tools.core.approvals and nothing else.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from ..core import approvals, audit, paths


@dataclass
class InsightRow:
    """One day of results for one entity, normalized across networks."""

    entity_id: str
    entity_name: str
    level: str  # campaign | adset | ad
    day: date
    spend: float
    impressions: int
    clicks: int
    conversions: float
    currency: str = "ILS"

    @property
    def cpa(self) -> float | None:
        return self.spend / self.conversions if self.conversions else None

    @property
    def ctr(self) -> float | None:
        return self.clicks / self.impressions if self.impressions else None


class AdPlatform(ABC):
    """Base for meta / tiktok / linkedin / google_ads."""

    name: str

    def __init__(self, client_slug: str) -> None:
        self.client_slug = client_slug

    # --- reads: allowed without approval -----------------------------------
    @abstractmethod
    def read_insights(
        self, since: date, until: date, level: str = "adset"
    ) -> list[InsightRow]:
        """Pull performance data. Must not change any state."""

    @abstractmethod
    def read_structure(self) -> dict[str, Any]:
        """Campaigns, ad sets and ads currently in the account."""

    # --- writes: drafts only ------------------------------------------------
    @abstractmethod
    def build_payload(self, campaign: paths.Campaign, **kwargs: Any) -> dict[str, Any]:
        """Translate a brief into this network's API shape. New campaigns are PAUSED."""

    def draft_campaign(
        self, campaign: paths.Campaign, rationale: str, **kwargs: Any
    ) -> Path:
        """Propose a campaign. Runs compliance, writes to drafts/, never executes."""
        payload = self.build_payload(campaign, **kwargs)
        return approvals.propose(
            campaign,
            action="create_campaign",
            platform=self.name,
            payload=payload,
            rationale=rationale,
        )

    def apply(self, draft: Path) -> dict[str, Any]:
        """Execute an approved draft. Refuses unless a human signed off."""
        data = approvals.require_approval(draft)
        try:
            response = self._execute(data["action"], data["payload"])
        except Exception as exc:
            audit.record(
                self.name, data["action"], self.client_slug,
                request=data["payload"], error=str(exc),
            )
            raise
        audit.record(
            self.name, data["action"], self.client_slug,
            request=data["payload"], response=response,
        )
        return response

    @abstractmethod
    def _execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """The only place a state-changing API call may happen."""
