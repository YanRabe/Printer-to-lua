import pytest

from printer_to_lua.models.printer import PrinterConfig
from printer_to_lua.models.profiles import profile_directory, profile_name


def test_profile_name_matches_legacy_space_conversion():
    assert profile_name("My Test Printer") == "My_Test_Printer"


def test_profile_name_rejects_empty_names():
    with pytest.raises(ValueError):
        profile_name("  ")


def test_profile_directory_does_not_depend_on_current_directory(tmp_path):
    assert profile_directory(tmp_path, "Printer") == tmp_path / "Printer"


def test_printer_config_requires_a_name():
    with pytest.raises(ValueError, match="printer name"):
        PrinterConfig(" ").require_name()
