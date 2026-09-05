"""Visual generation from a designer brief.

Visual policy (no before/after, no body-focused framing, no fake UI) lives in
policies/compliance.md and the client's brand/visual-identity.md. A generated
image is reviewed by a human before it reaches creatives/.
"""

from __future__ import annotations

from pathlib import Path


def generate(brief_path: Path, out_dir: Path, *, aspect: str = "1:1") -> Path:
    raise NotImplementedError("ai.image.generate — not wired yet")
