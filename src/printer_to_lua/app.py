"""Application entry point."""

from __future__ import annotations

from printer_to_lua.generators.service import GenerationService


def create_generation_service() -> GenerationService:
    """Create the domain service used by the Textual application."""
    return GenerationService()


def main() -> None:
    """Launch the Textual application."""
    from printer_to_lua.ui.app import gui

    app = gui()
    app.generation_service = create_generation_service()
    app.run()