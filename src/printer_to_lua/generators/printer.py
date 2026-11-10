"""Generate ``printer.lua`` content from firmware templates."""

from __future__ import annotations

from datetime import date
from collections.abc import Mapping
from typing import Any, Optional

from printer_to_lua.models.printer import PrinterConfig


def _template(mapping: Mapping[str, Any], key: str, default: str = "") -> str:
    value = mapping.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"Firmware template {key!r} must be a string.")
    return value


def _append(mapping: Mapping[str, Any], key: str, parts: list[str]) -> None:
    if key not in mapping:
        raise ValueError(f"Firmware template is missing {key!r}.")
    parts.append(_template(mapping, key))


def generate_printer(
    config: PrinterConfig,
    main_variables: dict[str, Any],
    util_functions: str,
    firmware_templates: Mapping[str, Any],
    created_on: Optional[date] = None,
) -> str:
    """Generate a printer file using the same conditional template order."""
    created_on = created_on or date.today()
    name = config.require_name()
    firmware_name = {0: "marlin", 1: "reprap", 2: "klipper"}.get(config.firmware)
    if firmware_name is None:
        raise ValueError(f"Unsupported firmware index: {config.firmware}.")
    try:
        templates = firmware_templates[firmware_name]
    except KeyError as error:
        raise ValueError(f"Templates are missing for {firmware_name}.") from error

    parts = [
        f"--Printer functions for {name}",
        f"--Created on {created_on.strftime('%x')}",
        "",
        "--Firmware: 0 = Marlin; 1 = RRF; 2 = Klipper;",
        f"firmware = {config.firmware}",
        "",
        util_functions,
        "",
        "--//////////////////////////////////////////////////Defining main variables",
    ]
    for variable, value in main_variables.items():
        rendered = str(value).lower() if isinstance(value, bool) else str(value)
        parts.append(f"{variable} = {rendered}")
    parts.append("")
    if "header" in config.function_overrides:
        parts.append(config.function_overrides["header"])
    else:
        _append(templates, "start_header", parts)
    if "header" not in config.function_overrides and config.enable_acceleration:
        _append(templates, "enable_acceleration", parts)
        if config.firmware == 0:
            _append(templates, "jerk_true" if config.classic_jerk else "jerk_false", parts)
    if "header" not in config.function_overrides:
        _append(templates, "temp_setup", parts)
        if config.heated_chamber:
            _append(templates, "heated_chamber", parts)
        _append(templates, "home_all", parts)
        if config.auto_bed_leveling:
            _append(
                templates,
                "auto_bed_leveling_and_reload_bed_mesh"
                if config.reload_bed_mesh
                else "auto_bed_leveling",
                parts,
            )
        if config.purge_line and config.firmware != 2:
            _append(templates, "purge_extruder", parts)
        _append(templates, "end_header", parts)
    parts.extend(
        [
            "-----------------------",
            config.function_overrides.get(
                "footer", _template(templates, "start_footer")
            ),
        ]
    )
    if "footer" not in config.function_overrides and config.heated_chamber:
        parts.append(_template(templates, "heated_chamber"))
    if "footer" not in config.function_overrides:
        parts.append(_template(templates, "home_all"))
    if "footer" not in config.function_overrides and config.enable_acceleration:
        parts.append(_template(templates, "enable_acceleration"))
        if config.firmware == 0:
            parts.append(
                _template(
                    templates,
                    "jerk_true" if config.classic_jerk else "jerk_false", ""
                )
            )
    if "footer" not in config.function_overrides:
        parts.extend(["", _template(templates, "end_footer")])
    parts.extend(
        [
            "--//////////////////////////////////////////////////Main Functions - called by IceSL ",
            "--################################################## HEADER & FOOTER ",
        ]
    )
    functions = templates.get("functions", {})
    for category, category_functions in functions.items():
        parts.append(f"\n--################################################## {category}")
        for function_name in category_functions:
            parts.append(
                config.function_overrides.get(
                    function_name, _template(category_functions, function_name)
                )
            )
            parts.append("-----------------------")
    return "\n".join(parts) + "\n"