"""Which campaigns are due for an optimization round.

Cadence is per client, in client.yaml. See policies/optimization-loop.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from . import config, paths

CADENCE_DAYS = {
    "daily": 1,
    "every_3_days": 3,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
}

REPORT_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-analyst\.md$")


@dataclass
class DueCampaign:
    client: str
    campaign: str
    last_report: date | None
    days_since: int | None
    cadence: str
    min_spend: int

    @property
    def reason(self) -> str:
        if self.last_report is None:
            return "אין דוח קודם"
        return f"{self.days_since} ימים מאז {self.last_report.isoformat()}"


def last_report_date(campaign: paths.Campaign) -> date | None:
    if not campaign.reports.is_dir():
        return None
    dates = [
        date.fromisoformat(m.group(1))
        for p in campaign.reports.iterdir()
        if (m := REPORT_NAME.match(p.name))
    ]
    return max(dates) if dates else None


def due(today: date | None = None) -> list[DueCampaign]:
    today = today or date.today()
    result: list[DueCampaign] = []

    for slug in paths.client_slugs():
        cfg = config.client(slug)
        if cfg.get("status") != "active":
            continue
        opt = cfg.get("optimization") or {}
        cadence = opt.get("cadence", "weekly")
        interval = CADENCE_DAYS.get(cadence, 7)
        floor_days = int(opt.get("min_days_since_last", 0))
        threshold = max(interval, floor_days)

        for campaign in paths.campaigns(slug):
            if _campaign_status(campaign) == "ended":
                continue
            last = last_report_date(campaign)
            days = (today - last).days if last else None
            if last is not None and days < threshold:
                continue
            result.append(
                DueCampaign(
                    client=slug,
                    campaign=campaign.slug,
                    last_report=last,
                    days_since=days,
                    cadence=cadence,
                    min_spend=int(opt.get("min_spend_since_last", 0)),
                )
            )
    return result


def _campaign_status(campaign: paths.Campaign) -> str:
    state: Path = campaign.state
    if not state.is_file():
        return "draft"
    data = yaml.safe_load(state.read_text(encoding="utf-8")) or {}
    return str(data.get("status", "draft"))
