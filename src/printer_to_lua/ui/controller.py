"""Pure coordination policies used by the Textual application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from printer_to_lua.firmware.registry import FirmwareUiTemplates, firmware_ui_templates


QUALITY_DEFAULTS: dict[str, dict[str, str]] = {
    "low": {
        "z_layer_height_mm_pq": "0.2",
        "priming_mm_per_sec_pq": "30",
        "print_speed_mm_per_sec_pq": "60",
        "cover_print_speed_mm_per_sec_pq": "35",
    },
    "medium": {
        "z_layer_height_mm_pq": "0.15",
        "priming_mm_per_sec_pq": "40",
        "print_speed_mm_per_sec_pq": "40",
        "cover_print_speed_mm_per_sec_pq": "25",
    },
    "high": {
        "z_layer_height_mm_pq": "0.1",
        "priming_mm_per_sec_pq": "50",
        "print_speed_mm_per_sec_pq": "50",
        "cover_print_speed_mm_per_sec_pq": "30",
    },
}

MATERIAL_DEFAULTS: dict[str, dict[str, str]] = {
    "PLA": {
        "nozzle_diameter_mm_0_pm": "0.4",
        "filament_diameter_mm_0_pm": "1.75",
        "filament_linear_adv_factor_pm": "0.06",
        "filament_priming_mm_pm": "45",
        "extruder_temp_degree_c_pm": "210",
        "bed_temp_degree_c_pm": "60",
        "fan_speed_percent_pm": "100",
        "fan_speed_percent_on_bridges_pm": "100",
        "print_speed_mm_per_sec_pm": "60",
        "perimeter_print_speed_mm_per_sec_pm": "45",
        "cover_print_speed_mm_per_sec_pm": "30",
        "first_layer_print_speed_mm_per_sec_pm": "20",
    },
    "ABS": {
        "nozzle_diameter_mm_0_pm": "0.6",
        "filament_diameter_mm_0_pm": "1.75",
        "filament_linear_adv_factor_pm": "0.04",
        "filament_priming_mm_pm": "45",
        "extruder_temp_degree_c_pm": "240",
        "bed_temp_degree_c_pm": "100",
        "enable_fan_pm": "false",
        "fan_speed_percent_pm": "100",
        "fan_speed_percent_on_bridges_pm": "100",
        "print_speed_mm_per_sec_pm": "50",
        "perimeter_print_speed_mm_per_sec_pm": "45",
        "cover_print_speed_mm_per_sec_pm": "45",
        "first_layer_print_speed_mm_per_sec_pm": "20",
    },
    "PETG": {
        "nozzle_diameter_mm_0_pm": "0.6",
        "filament_diameter_mm_0_pm": "1.75",
        "filament_linear_adv_factor_pm": "0.08",
        "extruder_temp_degree_c_pm": "230",
        "bed_temp_degree_c_pm": "75",
        "enable_fan_pm": "true",
        "fan_speed_percent_pm": "45",
        "fan_speed_percent_on_bridges_pm": "75",
        "print_speed_mm_per_sec": "120",
        "perimeter_print_speed_mm_per_sec_pm": "80",
        "cover_print_speed_mm_per_sec_pm": "80",
        "first_layer_print_speed_mm_per_sec_pm": "30",
    },
}


@dataclass(frozen=True)
class UiController:
    """Coordinate deterministic UI policy without importing Textual."""

    def firmware(self, index: int) -> FirmwareUiTemplates:
        return firmware_ui_templates(index)

    def quality_defaults(self, name: str) -> dict[str, str]:
        return dict(QUALITY_DEFAULTS.get(name, {}))

    def material_defaults(self, name: str) -> dict[str, str]:
        return dict(MATERIAL_DEFAULTS.get(name, {}))

    def speed_defaults(
        self, speed: float, nozzle_diameter: float, layer_height: float
    ) -> dict[str, str]:
        """Return dependent speed and volumetric-flow values."""
        return {
            "print_speed_mm_per_sec_min": f"{round(speed / 3, 2)}",
            "print_speed_mm_per_sec_max": f"{round(speed * 3.5, 2)}",
            "perimeter_print_speed_mm_per_sec": f"{round(speed * 0.75, 2)}",
            "perimeter_print_speed_mm_per_sec_min": f"{round(speed / 3, 2)}",
            "perimeter_print_speed_mm_per_sec_max": f"{round(speed * 2.8, 2)}",
            "cover_print_speed_mm_per_sec": f"{round(speed * 0.75, 2)}",
            "cover_print_speed_mm_per_sec_min": f"{round(speed / 3, 2)}",
            "cover_print_speed_mm_per_sec_max": f"{round(speed * 2.8, 2)}",
            "first_layer_print_speed_mm_per_sec": f"{round(speed / 3, 2)}",
            "first_layer_print_speed_mm_per_sec_max": f"{round(speed * 2.8, 2)}",
            "travel_speed_mm_per_sec": f"{round(speed * 3, 2)}",
            "volumetric_flow": f"{round(speed * nozzle_diameter * layer_height, 2)}",
        }

    def acceleration_defaults(self, acceleration: float) -> dict[str, str]:
        """Return dependent acceleration values."""
        return {
            "e_prime_max_acc": f"{round(acceleration / 2)}",
            "perimeter_acc": f"{round(acceleration / 2)}",
            "infill_acc": f"{round(acceleration)}",
            "x_max_acc": f"{round(acceleration)}",
            "y_max_acc": f"{round(acceleration)}",
            "z_max_acc": f"{round(acceleration / 40)}",
            "e_max_acc": f"{round(acceleration)}",
        }

    def junction_defaults(
        self,
        jerk: str | float,
        default_acceleration: float,
        perimeter_acceleration: float,
        infill_acceleration: float,
    ) -> dict[str, str]:
        """Return junction-deviation values derived from jerk and acceleration."""
        jerk_value = float(jerk)
        deviation = lambda acceleration: str(
            round(0.4 * (jerk_value**2 / acceleration), 4)
        )
        return {
            "infill_jerk": str(jerk),
            "default_junction_deviation": deviation(default_acceleration),
            "perimeter_junction_deviation": deviation(perimeter_acceleration),
            "infill_junction_deviation": deviation(infill_acceleration),
            "travel_junction_deviation": deviation(default_acceleration),
        }

    def advanced_visibility(self, enabled: bool) -> dict[str, bool]:
        """Return visibility for controls hidden outside advanced mode."""
        from printer_to_lua.data.features import features_dict

        return {
            "horizontal_enable_acceleration": enabled,
            "horizontal_filament_linear_adv_factor": enabled,
            **{
                f"horizontal_{feature}": enabled
                for category in features_dict.values()
                for feature, metadata in category.items()
                if metadata[4]
            },
        }

    @staticmethod
    def _feature_groups(
        category: str,
    ) -> tuple[tuple[str, tuple[Any, str, Any, Any, bool, bool]], ...]:
        from printer_to_lua.data.features import features_dict

        return tuple(features_dict[category].items())

    def acceleration_visibility(self, enabled: bool) -> dict[str, bool]:
        """Return disabled state for acceleration controls."""
        excluded = {
            "classic_jerk",
            "default_jerk",
            "infill_jerk",
            "default_junction_deviation",
            "perimeter_junction_deviation",
            "infill_junction_deviation",
            "travel_junction_deviation",
        }
        return {
            feature: enabled
            for feature, _ in self._feature_groups("acceleration_settings")
            if feature not in excluded
        }

    def extruder_visibility(self, count: int, maximum: int = 14) -> dict[str, bool]:
        """Return visibility for additional extruder controls."""
        return {
            f"horizontal_{prefix}_{index}": index < count
            for index in range(1, maximum)
            for prefix in ("nozzle", "fildiam")
        }

    def extruder_swap_disabled(self, count: int) -> dict[str, bool]:
        """Return disabled state for multi-extruder swap controls."""
        disabled = count <= 1
        return {
            "extruder_swap_zlift_mm": disabled,
            "extruder_swap_retract_length_mm": disabled,
            "extruder_swap_retract_speed_mm_per_sec": disabled,
        }
