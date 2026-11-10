from datetime import date

from printer_to_lua.generators.service import GenerationService
from printer_to_lua.models.printer import PrinterConfig


def test_service_generates_all_four_profile_files():
    generated = GenerationService().generate(
        PrinterConfig("Service Test", firmware=2),
        created_on=date(2024, 6, 14),
    )

    files = generated.files()
    assert set(files) == {
        "features.lua",
        "printer.lua",
        "profiles/low.lua",
        "materials/PLA.lua",
    }
    assert "function header()" in files["printer.lua"]
    assert "function footer()" in files["printer.lua"]
    assert "--################################################## COMMENT" in files["printer.lua"]


def test_service_supports_all_firmware_registrations():
    service = GenerationService()
    for firmware in (0, 1, 2):
        output = service.generate(
            PrinterConfig(f"Firmware {firmware}", firmware=firmware),
            created_on=date(2024, 6, 14),
        ).printer
        assert f"firmware = {firmware}" in output
        assert "function header()" in output


def test_service_writes_complete_profile_tree(tmp_path):
    destination = GenerationService().write(
        tmp_path,
        PrinterConfig("Service Test", firmware=1),
        quality_name="draft",
        material_name="PETG",
        created_on=date(2024, 6, 14),
    )

    assert (destination / "features.lua").is_file()
    assert (destination / "printer.lua").is_file()
    assert (destination / "profiles" / "draft.lua").is_file()
    assert (destination / "materials" / "PETG.lua").is_file()


def test_service_preserves_editor_overrides():
    config = PrinterConfig(
        "Override Test",
        function_overrides={
            "header": "custom header",
            "footer": "custom footer",
            "comment": "custom comment",
        },
    )
    output = GenerationService().generate(config).printer

    assert "custom header" in output
    assert "custom footer" in output
    assert "custom comment" in output
