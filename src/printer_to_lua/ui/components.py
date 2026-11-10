"""Reusable presentation components for the Textual application."""

from __future__ import annotations

from textual.widgets import Static


class GeneratedOutput(Static):
    """Display generated Lua content in a named output pane."""

    def set_content(self, content: str) -> None:
        """Replace the displayed generated content."""
        self.update(content)
