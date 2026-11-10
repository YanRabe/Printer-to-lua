"""Filesystem output helpers for generated Lua files."""

from __future__ import annotations

from pathlib import Path

from printer_to_lua.models.profiles import profile_directory


def write_profile(output_dir: Path, profile_name: str, files: dict[str, str]) -> Path:
    """Write generated files below one explicit profile directory."""
    destination = profile_directory(output_dir, profile_name)
    destination.mkdir(parents=True, exist_ok=True)
    for relative_name, content in files.items():
        target = destination / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return destination


def write_files(output_dir: Path, profile_name: str, files: dict[str, str]) -> Path:
    """Write a selected set of generated files to a profile directory."""
    return write_profile(output_dir, profile_name, files)