"""Firmware template registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from printer_to_lua.firmware.klipper import (
    klipper_footer_dict,
    klipper_function_dict,
    klipper_header_dict,
    klipper_move_xyz_dict,
    klipper_move_xyze_dict,
    klipper_select_extruder_dict,
)
from printer_to_lua.firmware.marlin import (
    marlin_footer_dict,
    marlin_function_dict,
    marlin_header_dict,
    marlin_move_xyz_dict,
    marlin_move_xyze_dict,
    marlin_select_extruder_dict,
)
from printer_to_lua.firmware.reprap import (
    rrf_footer_dict,
    rrf_function_dict,
    rrf_header_dict,
    rrf_move_xyz_dict,
    rrf_move_xyze_dict,
    rrf_select_extruder_dict,
)

FirmwareTemplates = dict[str, Any]


@dataclass(frozen=True)
class FirmwareUiTemplates:
    """Firmware snippets used by the printer editor UI."""

    header: dict[str, str]
    footer: dict[str, str]
    select_extruder: dict[str, str]
    move_xyz: dict[str, str]
    move_xyze: dict[str, str]
    functions: dict[str, dict[str, str]]


FIRMWARE_UI_TEMPLATES: dict[int, FirmwareUiTemplates] = {
    0: FirmwareUiTemplates(
        marlin_header_dict,
        marlin_footer_dict,
        marlin_select_extruder_dict,
        marlin_move_xyz_dict,
        marlin_move_xyze_dict,
        marlin_function_dict,
    ),
    1: FirmwareUiTemplates(
        rrf_header_dict,
        rrf_footer_dict,
        rrf_select_extruder_dict,
        rrf_move_xyz_dict,
        rrf_move_xyze_dict,
        rrf_function_dict,
    ),
    2: FirmwareUiTemplates(
        klipper_header_dict,
        klipper_footer_dict,
        klipper_select_extruder_dict,
        klipper_move_xyz_dict,
        klipper_move_xyze_dict,
        klipper_function_dict,
    ),
}


def firmware_ui_templates(firmware: int) -> FirmwareUiTemplates:
    """Return the editor templates for a supported firmware index."""
    try:
        return FIRMWARE_UI_TEMPLATES[firmware]
    except KeyError as error:
        raise ValueError(f"Unsupported firmware index: {firmware}.") from error


def _templates(
    header: dict[str, str],
    footer: dict[str, str],
    select_extruder: dict[str, str],
    move_xyz: dict[str, str],
    move_xyze: dict[str, str],
    functions: dict[str, dict[str, str]],
) -> FirmwareTemplates:
    return {
        **header,
        **footer,
        **select_extruder,
        **move_xyz,
        **move_xyze,
        "functions": functions,
    }


FIRMWARE_TEMPLATES: dict[int, FirmwareTemplates] = {
    0: _templates(
        marlin_header_dict,
        marlin_footer_dict,
        marlin_select_extruder_dict,
        marlin_move_xyz_dict,
        marlin_move_xyze_dict,
        marlin_function_dict,
    ),
    1: _templates(
        rrf_header_dict,
        rrf_footer_dict,
        rrf_select_extruder_dict,
        rrf_move_xyz_dict,
        rrf_move_xyze_dict,
        rrf_function_dict,
    ),
    2: _templates(
        klipper_header_dict,
        klipper_footer_dict,
        klipper_select_extruder_dict,
        klipper_move_xyz_dict,
        klipper_move_xyze_dict,
        klipper_function_dict,
    ),
}

FIRMWARE_NAMES = {0: "marlin", 1: "reprap", 2: "klipper"}


def firmware_templates(firmware: int) -> FirmwareTemplates:
    """Return templates for a supported firmware index."""
    try:
        return FIRMWARE_TEMPLATES[firmware]
    except KeyError as error:
        raise ValueError(f"Unsupported firmware index: {firmware}.") from error
