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
