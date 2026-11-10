"""UI state and firmware-template projection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass
class PrinterUiState:
    """Mutable values that control generated printer template sections."""

    firmware: int = 0
    extruder_count: int = 1
    enable_acceleration: bool = False
    classic_jerk: bool = False
    heated_chamber: bool = False
    purge_line: bool = True
    auto_bed_leveling: bool = True
    reload_bed_mesh: bool = False
    use_per_path_accel: bool = True
    craftware_debug: bool = True

    def render_sections(
        self, templates: Mapping[str, str]
    ) -> dict[str, str]:
        """Render all dynamic editor sections from one firmware template set."""
        header = templates["start_header"]
        if self.enable_acceleration:
            header += templates["enable_acceleration"]
            if self.firmware == 0:
                header += templates["jerk_true" if self.classic_jerk else "jerk_false"]
        header += templates["temp_setup"]
        if self.heated_chamber:
            header += templates["heated_chamber"]
        header += templates["home_all"]
        if self.auto_bed_leveling:
            header += templates[
                "auto_bed_leveling_and_reload_bed_mesh"
                if self.reload_bed_mesh
                else "auto_bed_leveling"
            ]
        if self.purge_line and self.firmware != 2:
            header += templates["purge_extruder"]
        header += templates["end_header"]

        footer = templates["start_footer"]
        if self.heated_chamber:
            footer += templates["heated_chamber"]
        footer += templates["home_all"]
        if self.enable_acceleration:
            footer += templates["enable_acceleration"]
            if self.firmware == 0:
                footer += templates["jerk_true" if self.classic_jerk else "jerk_false"]
        footer += templates["end_footer"]

        select_extruder = templates["start_select_extruder"]
        select_extruder += templates[
            "multi_extruders" if self.extruder_count > 1 else "solo_extruder"
        ]
        select_extruder += templates["end_select_extruder"]

        move_xyz = templates["start_move_xyz"]
        if self.use_per_path_accel:
            move_xyz += templates["use_per_path_accel"]
        move_xyz += templates["end_move_xyz"]

        move_xyze = templates["start_move_xyze"]
        move_xyze += templates[
            "craftware_debug_true" if self.craftware_debug else "craftware_debug_false"
        ]
        move_xyze += templates["path_type"]
        if self.use_per_path_accel:
            move_xyze += templates["use_per_path_accel"]
        move_xyze += templates["end_move_xyze"]

        return {
            "header": header,
            "footer": footer,
            "select_extruder": select_extruder,
            "move_xyz": move_xyz,
            "move_xyze": move_xyze,
        }