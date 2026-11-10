from printer_to_lua.ui.controller import UiController


def test_controller_returns_firmware_editor_templates():
    templates = UiController().firmware(2)

    assert templates.functions
    assert templates.header


def test_controller_returns_profile_defaults_as_independent_mappings():
    controller = UiController()

    quality = controller.quality_defaults("medium")
    material = controller.material_defaults("PLA")

    assert quality["z_layer_height_mm_pq"] == "0.15"
    assert material["nozzle_diameter_mm_0_pm"] == "0.4"

    quality["z_layer_height_mm_pq"] = "changed"
    assert controller.quality_defaults("medium")["z_layer_height_mm_pq"] == "0.15"


def test_controller_ignores_unknown_profile_defaults():
    controller = UiController()

    assert controller.quality_defaults("unknown") == {}
    assert controller.material_defaults("unknown") == {}


def test_controller_calculates_dependent_speed_values():
    values = UiController().speed_defaults(60, 0.4, 0.2)

    assert values["print_speed_mm_per_sec_min"] == "20.0"
    assert values["travel_speed_mm_per_sec"] == "180"
    assert values["volumetric_flow"] == "4.8"


def test_controller_calculates_acceleration_and_junction_values():
    controller = UiController()

    assert controller.acceleration_defaults(1000)["z_max_acc"] == "25"
    assert controller.junction_defaults("5", 1000, 500, 1000)[
        "default_junction_deviation"
    ] == "0.01"


def test_controller_calculates_visibility_plans():
    controller = UiController()

    assert controller.advanced_visibility(False)[
        "horizontal_filament_linear_adv_factor"
    ] is False
    assert controller.advanced_visibility(True)[
        "horizontal_filament_linear_adv_factor"
    ] is True
    assert controller.acceleration_visibility(False)["default_acc"] is False
    assert controller.extruder_visibility(3)["horizontal_nozzle_2"] is True
    assert controller.extruder_visibility(3)["horizontal_nozzle_3"] is False
    assert controller.extruder_swap_disabled(1)["extruder_swap_zlift_mm"] is True
    assert controller.extruder_swap_disabled(2)["extruder_swap_zlift_mm"] is False
