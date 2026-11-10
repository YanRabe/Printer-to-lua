from datetime import date

from printer_to_lua.data.features import (
    default_features,
    features_dict,
    materials_features,
)
from printer_to_lua.generators.features import generate_features
from printer_to_lua.generators.materials import generate_profile
from printer_to_lua.models.printer import PrinterConfig


def test_features_generation_is_deterministic_and_uses_lua_booleans():
    output = generate_features(
        PrinterConfig("Baseline", firmware=2),
        default_features,
        features_dict,
        created_on=date(2024, 6, 14),
    )

    assert output.startswith("--Custom profile for Baseline\n--Created on 06/14/24")
    assert "firmware = 2" in output
    assert "bed_circular = false" in output
    assert "add_checkbox_setting('auto_bed_leveling'" in output


def test_material_generation_rejects_unknown_profile_kind():
    try:
        generate_profile(
            PrinterConfig("Baseline"),
            "unknown",
            materials_features,
            created_on=date(2024, 6, 14),
        )
    except ValueError as error:
        assert "quality" in str(error)
    else:
        raise AssertionError("unknown profile kinds must be rejected")


def test_disabled_features_are_emitted_as_lua_comments():
    config = PrinterConfig(
        "Baseline",
        commented_features={"bed_size_z_mm"},
    )
    output = generate_features(
        config,
        default_features,
        features_dict,
        created_on=date(2024, 6, 14),
    )

    assert "--bed_size_z_mm = 340" in output
