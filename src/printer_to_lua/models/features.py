"""Feature value models used by the non-UI generation layer."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


FeatureGroups = Mapping[str, Mapping[str, tuple[Any, str, Any, Any, bool, bool]]]


def default_values(groups: FeatureGroups) -> dict[str, dict[str, Any]]:
    """Return a mutable copy of the default values from feature metadata."""
    return {
        category: {name: definition[0] for name, definition in features.items()}
        for category, features in groups.items()
    }


def lua_value(value: Any) -> str:
    """Render a Python value using the Lua literals used by the legacy app."""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)