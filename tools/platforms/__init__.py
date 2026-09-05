"""Platform registry. Agents ask for a network by name, never import one directly."""

from __future__ import annotations

import importlib

from .base import AdPlatform, InsightRow

SUPPORTED = ("meta", "tiktok", "linkedin", "google_ads")

__all__ = ["AdPlatform", "InsightRow", "SUPPORTED", "get_platform"]


def get_platform(name: str, client_slug: str) -> AdPlatform:
    if name not in SUPPORTED:
        raise ValueError(f"unknown platform: {name} (supported: {', '.join(SUPPORTED)})")
    module = importlib.import_module(f"{__name__}.{name}")
    return module.Platform(client_slug)
