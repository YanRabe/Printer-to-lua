from printer_to_lua.generators.templates import write_profile


def test_write_profile_creates_nested_directories(tmp_path):
    destination = write_profile(
        tmp_path,
        "Test Printer",
        {
            "features.lua": "features\n",
            "profiles/low.lua": "quality\n",
            "materials/PLA.lua": "material\n",
        },
    )

    assert destination == tmp_path / "Test_Printer"
    assert (destination / "features.lua").read_text() == "features\n"
    assert (destination / "profiles" / "low.lua").read_text() == "quality\n"
    assert (destination / "materials" / "PLA.lua").read_text() == "material\n"
