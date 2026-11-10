from pathlib import Path


ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples" / "printers"


def test_example_profiles_have_expected_output_tree():
    profiles = sorted(path for path in EXAMPLES.iterdir() if path.is_dir())
    assert profiles
    for profile in profiles:
        assert (profile / "features.lua").is_file()
        assert (profile / "printer.lua").is_file()
        assert (profile / "features.lua").read_text(encoding="utf-8").startswith("--")
        assert (profile / "printer.lua").read_text(encoding="utf-8").startswith("--")


def test_test_profile_fixture_preserves_nested_outputs():
    profile = EXAMPLES / "testProfile"
    assert (profile / "profiles" / "low.lua").is_file()
    assert (profile / "materials" / "PLA.lua").is_file()
