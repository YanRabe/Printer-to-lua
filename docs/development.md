# Development

The project is being migrated in phases. Phase 1 establishes the non-UI
generation boundary and preserves the existing Lua examples as fixtures.

Install the project and test dependencies with. The supported UI dependency is
Textual 8.2.x:

```bash
python -m pip install -e ".[test]"
```

VS Code is configured to use `.venv/bin/python` for Pylance and test
discovery. With fish, activate it using `source .venv/bin/activate.fish`;
from other shells, invoke `.venv/bin/python` directly.

Run the test suite with:

```bash
python -m pytest
```

The Textual UI is available through:

```bash
python -m printer_to_lua
```

The UI has headless mount and generation tests using Textual's
`App.run_test()` API. These keep widget IDs, initial disabled-state behavior,
and artifact generation stable.

Phase 4 routes the active Create buttons through `GenerationService`. The
obsolete duplicate generation handler has been removed; Textual dispatches
through the single service-backed handler.

Generated files should be written below an explicit output directory. The
phase-1 `write_profile` helper creates nested `profiles` and `materials`
directories safely.

The domain service exposes complete and selected-artifact generation:

```python
from pathlib import Path
from printer_to_lua.generators.service import GenerationService
from printer_to_lua.models.printer import PrinterConfig

GenerationService().write(Path("output"), PrinterConfig("My Printer"))
```

Build release artifacts with:

```bash
python -m pip install build
python -m build
```

The wheel includes the Textual stylesheet from `src/printer_to_lua/assets/`.

The quality and material forms share the `ProfileTab` component in
`src/printer_to_lua/ui/components.py`. Preserve the existing widget IDs when
extending these forms because the adapter and event handlers use those IDs as
their UI-to-domain contract.

The main printer feature form is provided by the `FeaturesTab` component in
the same module. It owns the data-driven feature controls and preserves the
existing IDs used by the adapter and application event handlers.

Deterministic event coordination is kept in `ui/controller.py`. Profile
defaults and firmware template selection belong there; Textual handlers apply
the returned values to widgets and remain responsible for rendering.
Derived speed, acceleration, and junction-deviation values use the same
controller boundary.

The firmware variable and Lua editor surface is provided by the
`PrinterEditorTab` component in the same module. Firmware switching remains
owned by the application event handler; the component receives the current
template values when it is composed.
