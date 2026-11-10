"""Compatibility module for launching the Textual application."""

from printer_to_lua.ui.app import gui, isNotSpaces

__all__ = ["gui", "isNotSpaces"]


if __name__ == "__main__":
    gui().run()
