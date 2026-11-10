"""Printer configuration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PrinterConfig:
    """Inputs required to generate a printer profile."""

    name: str
    firmware: int = 0
    extruder_count: int = 1
    features: dict[str, dict[str, Any]] = field(default_factory=dict)
    quality: dict[str, dict[str, Any]] = field(default_factory=dict)
    material: dict[str, dict[str, Any]] = field(default_factory=dict)
    enable_acceleration: bool = False
    classic_jerk: bool = False
    heated_chamber: bool = False
    purge_line: bool = True
    auto_bed_leveling: bool = True
    reload_bed_mesh: bool = False
    use_per_path_accel: bool = True
    craftware_debug: bool = True
    function_overrides: dict[str, str] = field(default_factory=dict)
    commented_features: set[str] = field(default_factory=set)

    def require_name(self) -> str:
        """Return the profile name or raise a useful validation error."""
        name = self.name.strip()
        if not name:
            raise ValueError("A printer name is required.")
        return name