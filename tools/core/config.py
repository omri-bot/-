"""Environment and per-client configuration.

Secrets live in .env only. client.yaml holds account identifiers, never tokens.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import yaml

from . import paths

_ENV_KEYS = {
    "meta": ("META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN"),
    "tiktok": ("TIKTOK_APP_ID", "TIKTOK_APP_SECRET", "TIKTOK_ACCESS_TOKEN"),
    "linkedin": ("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_ACCESS_TOKEN"),
    "google_ads": (
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
    ),
}


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(paths.ROOT / ".env")


def live_writes_allowed() -> bool:
    load_env()
    return os.getenv("ALLOW_LIVE_WRITES", "false").strip().lower() == "true"


def credentials(platform: str) -> dict[str, str]:
    load_env()
    keys = _ENV_KEYS.get(platform)
    if keys is None:
        raise ValueError(f"unknown platform: {platform}")
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"missing credentials for {platform}: {', '.join(missing)} (see .env.example)"
        )
    return {k: os.environ[k] for k in keys}


@lru_cache(maxsize=None)
def client(slug: str) -> dict[str, Any]:
    with (paths.client_dir(slug) / "client.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def account_id(slug: str, platform: str) -> str | None:
    accounts = client(slug).get("accounts") or {}
    entry = accounts.get(platform) or {}
    for key in ("ad_account_id", "advertiser_id", "account_id", "customer_id"):
        if entry.get(key):
            return str(entry[key])
    return None


def active_platforms(slug: str) -> list[str]:
    return [p for p in paths.PLATFORMS if account_id(slug, p)]
