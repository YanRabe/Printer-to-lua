from printer_to_lua.firmware.marlin import (
    marlin_footer_dict,
    marlin_header_dict,
    marlin_move_xyz_dict,
    marlin_move_xyze_dict,
    marlin_select_extruder_dict,
)
from printer_to_lua.ui.state import PrinterUiState


def _marlin_templates():
    return {
        **marlin_header_dict,
        **marlin_footer_dict,
        **marlin_select_extruder_dict,
        **marlin_move_xyz_dict,
        **marlin_move_xyze_dict,
    }


def test_ui_state_renders_conditional_sections():
    state = PrinterUiState(
        enable_acceleration=True,
        classic_jerk=True,
        heated_chamber=True,
        purge_line=True,
        auto_bed_leveling=True,
        reload_bed_mesh=True,
        extruder_count=2,
        use_per_path_accel=True,
        craftware_debug=True,
    )

    sections = state.render_sections(_marlin_templates())

    assert "M205 X" in sections["header"]
    assert "M141 S" in sections["header"]
    assert "M420 L" in sections["header"] or "M420" in sections["header"]
    assert "function footer()" in sections["footer"]
    assert "extruder" in sections["select_extruder"]
    assert sections["move_xyz"]
    assert sections["move_xyze"]


def test_ui_state_omits_disabled_sections():
    state = PrinterUiState(
        enable_acceleration=False,
        heated_chamber=False,
        purge_line=False,
        auto_bed_leveling=False,
        use_per_path_accel=False,
    )

    sections = state.render_sections(_marlin_templates())

    assert "M201" not in sections["header"]
    assert "M141" not in sections["header"]
    assert "G29" not in sections["header"]
    assert "G0 F6000 X0.100" not in sections["header"]
