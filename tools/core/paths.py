"""Conventional locations in the clients/ tree. Nothing else should hardcode paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIENTS = ROOT / "clients"
POLICIES = ROOT / "policies"
DATA = ROOT / "data"

TEMPLATE = "_template"
PLATFORMS = ("meta", "tiktok", "linkedin", "google_ads")


@dataclass(frozen=True)
class Campaign:
    client: str
    slug: str
    path: Path

    @property
    def brief(self) -> Path:
        return self.path / "brief.md"

    @property
    def state(self) -> Path:
        return self.path / "state.yaml"

    @property
    def optimization_log(self) -> Path:
        return self.path / "optimization-log.md"

    @property
    def reports(self) -> Path:
        return self.path / "reports"

    @property
    def drafts(self) -> Path:
        return self.path / "drafts"


def client_dir(slug: str) -> Path:
    path = CLIENTS / slug
    if not path.is_dir():
        raise FileNotFoundError(f"unknown client: {slug}")
    return path


def client_slugs() -> list[str]:
    if not CLIENTS.is_dir():
        return []
    return sorted(
        p.name for p in CLIENTS.iterdir() if p.is_dir() and p.name != TEMPLATE
    )


def offerings(slug: str) -> list[Path]:
    root = client_dir(slug) / "offerings"
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and p.name != TEMPLATE)


def campaigns(slug: str) -> list[Campaign]:
    root = client_dir(slug) / "campaigns"
    if not root.is_dir():
        return []
    return [
        Campaign(client=slug, slug=p.name, path=p)
        for p in sorted(root.iterdir())
        if p.is_dir() and p.name != TEMPLATE
    ]


def campaign(client: str, campaign_slug: str) -> Campaign:
    path = client_dir(client) / "campaigns" / campaign_slug
    if not path.is_dir():
        raise FileNotFoundError(f"unknown campaign: {client}/{campaign_slug}")
    return Campaign(client=client, slug=campaign_slug, path=path)
