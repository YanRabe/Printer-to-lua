import asyncio

from textual.widgets import Button, Header, Input, Select, Switch

from printer_to_lua.ui.app import gui


async def _mount_app():
    app = gui()
    async with app.run_test() as pilot:
        assert app.query_one(Header)
        assert app.query_one("#name")
        assert app.query_one("#send").disabled
        assert app.query_one("#quality_tab").disabled
        await pilot.pause()


def test_textual_app_mounts_in_headless_mode():
    asyncio.run(_mount_app())


async def _enter_name_and_generate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = gui()
    async with app.run_test() as pilot:
        await pilot.click("#name")
        await pilot.press(*"Phase 5 Printer")
        await pilot.pause()

        assert not app.query_one("#send").disabled
        assert not app.query_one("#quality_tab").disabled
        assert not app.query_one("#materials_tab").disabled

        app.query_one("#send", Button).press()
        await pilot.pause()

        output = tmp_path / "Phase_5_Printer"
        assert (output / "features.lua").is_file()
        assert app.featurecode.startswith("--Custom profile for Phase 5 Printer")

        for button_id, relative_path in (
            ("send-pq", "profiles/low.lua"),
            ("send-pm", "materials/PLA.lua"),
            ("send-printer", "printer.lua"),
        ):
            app.query_one(f"#{button_id}", Button).press()
            await pilot.pause()
            assert (output / relative_path).is_file()


def test_textual_app_generates_features_from_active_button(tmp_path, monkeypatch):
    asyncio.run(_enter_name_and_generate(tmp_path, monkeypatch))


async def _exercise_dynamic_controls():
    app = gui()
    async with app.run_test() as pilot:
        firmware = app.query_one("#firmware", Select)
        firmware.value = 1
        await pilot.pause()
        assert app.query_one("#classic_jerk", Switch).value
        assert app.query_one("#classic_jerk", Switch).disabled

        material = app.query_one("#material", Select)
        material.value = "ABS"
        await pilot.pause()
        assert app.query_one("#nozzle_diameter_mm_0_pm", Input).value == "0.6"
        assert not app.query_one("#enable_fan_pm", Switch).value

        bed = app.query_one("#bed_circular", Select)
        bed.value = True
        await pilot.pause()
        assert not app.query_one("#bed_radius", Input).disabled
        assert app.query_one("#bed_size_x_mm", Input).disabled

        extruders = app.query_one("#extruder_count", Select)
        extruders.value = 3
        await pilot.pause()
        assert app.query_one("#horizontal_nozzle_1").display
        assert app.query_one("#horizontal_nozzle_2").display
        assert not app.query_one("#extruder_swap_zlift_mm").disabled

        advanced = app.query_one("#advanced_mode", Switch)
        advanced.value = True
        await pilot.pause()
        assert app.query_one("#horizontal_filament_linear_adv_factor").display


def test_textual_app_dynamic_controls_preserve_state_rules():
    asyncio.run(_exercise_dynamic_controls())
