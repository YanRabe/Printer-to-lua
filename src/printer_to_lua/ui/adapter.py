"""Adapters between Textual widgets and the domain generation service."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from printer_to_lua.data.features import (
    default_features,
    features_dict,
    materials_features,
    quality_features,
)
from printer_to_lua.models.printer import PrinterConfig


class WidgetReader:
    """Small boundary around Textual's widget query API."""

    def __init__(self, query_one: Callable[..., Any]) -> None:
        self._query_one = query_one

    def value(self, widget_id: str) -> Any:
        widget = self._query_one(f"#{widget_id}")
        return getattr(widget, "value", getattr(widget, "text", ""))

    def disabled(self, widget_id: str) -> bool:
        return bool(self._query_one(f"#{widget_id}").disabled)


def _group_values(
    reader: WidgetReader,
    groups: Mapping[str, Mapping[str, tuple[Any, str, Any, Any, bool, bool]]],
    suffix: str = "",
) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for category, features in groups.items():
        values[category] = {}
        for feature in features:
            widget_id = f"{feature}{suffix}"
            values[category][feature] = reader.value(widget_id)
    return values


def _feature_overrides(
    reader: WidgetReader,
    groups: Mapping[str, Mapping[str, tuple[Any, str, Any, Any, bool, bool]]],
) -> dict[str, dict[str, Any]]:
    values = _group_values(reader, groups)
    for category, features in groups.items():
        for feature in features:
            value = values[category][feature]
            if isinstance(value, str) and value == "":
                raise ValueError(f"Missing value for {feature}.")
    return values


def _disabled_features(
    reader: WidgetReader,
    groups: Mapping[str, Mapping[str, tuple[Any, str, Any, Any, bool, bool]]],
    suffix: str = "",
) -> set[str]:
    return {
        feature
        for features in groups.values()
        for feature in features
        if reader.disabled(f"{feature}{suffix}")
    }


def config_from_widgets(
    query_one: Callable[..., Any],
    *,
    name: str,
    firmware: int,
    extruder_count: int,
    switches: Mapping[str, bool],
    function_ids: tuple[str, ...],
) -> PrinterConfig:
    """Build a validated domain configuration from the current UI snapshot."""
    reader = WidgetReader(query_one)
    values = _feature_overrides(reader, default_features)
    for category, category_values in _feature_overrides(reader, features_dict).items():
        values[category] = category_values

    for index in range(1, extruder_count):
        values.setdefault("extruder", {})[f"nozzle_diameter_mm_{index}"] = reader.value(
            f"nozzle_diameter_mm_{index}"
        )
        values["extruder"][f"filament_diameter_mm_{index}"] = reader.value(
            f"filament_diameter_mm_{index}"
        )

    overrides = {widget_id: str(reader.value(widget_id)) for widget_id in function_ids}
    overrides.update(
        {
            "header": str(reader.value("header")),
            "footer": str(reader.value("footer")),
            "select_extruder": str(reader.value("select_extruder")),
            "move_xyz": str(reader.value("move_xyz")),
            "move_xyze": str(reader.value("move_xyze")),
        }
    )
    commented_features = _disabled_features(reader, default_features)
    commented_features.update(_disabled_features(reader, features_dict))
    commented_features.update(_disabled_features(reader, quality_features, "_pq"))
    commented_features.update(_disabled_features(reader, materials_features, "_pm"))
    return PrinterConfig(
        name=name,
        firmware=firmware,
        extruder_count=extruder_count,
        features=values,
        quality=_group_values(reader, quality_features, "_pq"),
        material=_group_values(reader, materials_features, "_pm"),
        enable_acceleration=switches.get("enable_acceleration", False),
        classic_jerk=switches.get("classic_jerk", False),
        heated_chamber=switches.get("heated_chamber", False),
        purge_line=switches.get("purge_line", True),
        auto_bed_leveling=switches.get("auto_bed_leveling", True),
        reload_bed_mesh=switches.get("reload_bed_mesh", False),
        use_per_path_accel=switches.get("use_per_path_accel", True),
        craftware_debug=switches.get("craftware_debug", True),
        function_overrides=overrides,
        commented_features=commented_features,
    )
