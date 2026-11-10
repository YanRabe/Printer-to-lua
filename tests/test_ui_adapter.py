from types import SimpleNamespace

from printer_to_lua.data.features import (
    default_features,
    features_dict,
    materials_features,
    quality_features,
)
from printer_to_lua.ui.adapter import config_from_widgets


def test_config_adapter_reads_feature_values_and_switches():
    widgets = {}
    for groups in (default_features, features_dict, quality_features, materials_features):
        for features in groups.values():
            for name, definition in features.items():
                widgets[name] = SimpleNamespace(value=str(definition[0]), disabled=False)
    for groups, suffix in ((quality_features, "_pq"), (materials_features, "_pm")):
        for features in groups.values():
            for name, definition in features.items():
                widgets[f"{name}{suffix}"] = SimpleNamespace(
                    value=str(definition[0]), disabled=False
                )
    widgets.update(
        {
            "header": SimpleNamespace(text="header"),
            "footer": SimpleNamespace(text="footer"),
            "select_extruder": SimpleNamespace(text="select"),
            "move_xyz": SimpleNamespace(text="xyz"),
            "move_xyze": SimpleNamespace(text="xyze"),
        }
    )

    def query_one(selector):
        return widgets[selector[1:]]

    config = config_from_widgets(
        query_one,
        name="Adapter Test",
        firmware=2,
        extruder_count=1,

        switches={"purge_line": False, "auto_bed_leveling": True},
        function_ids=(),
    )

    assert config.name == "Adapter Test"
    assert config.firmware == 2
    assert config.purge_line is False
    assert config.features["build_area_dimensions"]["bed_size_x_mm"] == "310"
    assert config.function_overrides["header"] == "header"
