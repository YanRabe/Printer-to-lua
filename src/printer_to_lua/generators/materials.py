"""Generate quality and material Lua profile content."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from printer_to_lua.models.features import FeatureGroups, lua_value
from printer_to_lua.models.printer import PrinterConfig


def generate_profile(
    config: PrinterConfig,
    kind: str,
    values: FeatureGroups,
    created_on: Optional[date] = None,
) -> str:
    """Generate a quality or material profile using the legacy format."""
    created_on = created_on or date.today()
    name = config.require_name()
    if kind not in {"quality", "material"}:
        raise ValueError("Profile kind must be 'quality' or 'material'.")
    selected = config.quality if kind == "quality" else config.material
    profile = "low" if kind == "quality" else "PLA"
    header = (
        f"--Custom quality profile: {profile} for {name}"
        if kind == "quality"
        else f"--Custom material profile: {profile} for {name} "
    )
    lines = [header, f"--Created on {created_on.strftime('%x')}", " "]
    for category, features in values.items():
        lines.extend(["", f"--{category}"])
        for feature, definition in features.items():
            value: Any = selected.get(category, {}).get(feature, definition[0])
            prefix = "--" if feature in config.commented_features else ""
            lines.append(f"{prefix}{feature} = {lua_value(value)}")
    return "\n".join(lines) + "\n"