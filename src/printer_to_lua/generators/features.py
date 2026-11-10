"""Generate ``features.lua`` content from feature metadata."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from printer_to_lua.models.features import FeatureGroups, default_values, lua_value
from printer_to_lua.models.printer import PrinterConfig


def _render_groups(
    lines: list[str],
    groups: FeatureGroups,
    values: dict[str, dict[str, Any]],
    config_commented_features: set[str],
) -> None:
    for category, features in groups.items():
        lines.extend(["", f"--{category}"])
        for name, definition in features.items():
            value = values.get(category, {}).get(name, definition[0])
            if definition[5] or name in config_commented_features:
                lines.append(f"--{name} = {lua_value(value)}")
            else:
                lines.append(f"{name} = {lua_value(value)}")


def generate_features(
    config: PrinterConfig,
    default_features: FeatureGroups,
    additional_features: FeatureGroups,
    created_on: Optional[date] = None,
) -> str:
    """Generate a deterministic features profile."""
    created_on = created_on or date.today()
    name = config.require_name()
    values = config.features or default_values(default_features)
    lines = [
        f"--Custom profile for {name}",
        f"--Created on {created_on.strftime('%x')}",
        "",
        "--Firmware: 0 = Marlin; 1 = RRF; 2 = Klipper;",
        f"firmware = {config.firmware}",
        "",
        "--Additional features: ",
        "add_checkbox_setting('auto_bed_leveling', 'Auto Bed Leveling','Use G29 Auto Leveling if the machine is equipped with one (BLTouch, Pinda, capacitive sensor, etc.)')",
        "add_checkbox_setting('reload_bed_mesh', 'Reload the last bed-mesh','Reload the last saved bed-mesh if available')",
        "add_checkbox_setting('use_per_path_accel', 'Uses Per-Path Acceleration', 'Manage Accelerations depending of the current path type')",
        "add_setting('volumetric_flow', 'Volumetric Flow', 0, 20, 'Product of printing speed, layer height and nozzle diameter', 4.8)",
        " ",
    ]
    config_commented_features = config.commented_features
    _render_groups(lines, default_features, values, config_commented_features)
    _render_groups(lines, additional_features, values, config_commented_features)
    return "\n".join(lines) + "\n"