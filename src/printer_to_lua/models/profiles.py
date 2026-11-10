"""Shared profile naming and output-path helpers."""

from __future__ import annotations

import re
from pathlib import Path


def profile_name(value: str) -> str:
    """Convert a display name to the folder naming convention of the app."""
    normalized = re.sub(r"\s+", "_", value.strip())
    normalized = re.sub(r"[^A-Za-z0-9_.-]", "_", normalized)
    normalized = normalized.strip("._")
    if not normalized:
        raise ValueError("A non-empty profile name is required.")
    return normalized


def profile_directory(output_dir: Path, name: str) -> Path:
    """Return the output directory for a profile without changing directories."""
    return output_dir / profile_name(name)