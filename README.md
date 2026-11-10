# Printer-to-lua

Printer-to-lua is a Python/Textual application for generating IceSL printer
profiles. It supports Marlin, RepRapFirmware, and Klipper templates and
generates:

- `features.lua`
- `printer.lua`
- quality profiles
- material profiles

## Requirements

- Python 3.9 or newer
- A terminal capable of running Textual

Create a virtual environment and install the project:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[test]"
```

With fish, activate the environment using:

```fish
source .venv/bin/activate.fish
```

## Run

Launch the installed command:

```bash
printer-to-lua
```

You can also use the module entry point:

```bash
python -m printer_to_lua
```

Generated files are written below the current working directory, inside a
sanitized directory derived from the printer name.

## Test and build

Run the test suite and compile check:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
```

Build source and wheel distributions:

```bash
.venv/bin/python -m pip install build
.venv/bin/python -m build
```

The resulting artifacts are created in `dist/`. The CI workflow runs the test
suite on Python 3.9, 3.12, and 3.14 and builds both distributions.

## Project layout

```text
src/printer_to_lua/
├── data/          Feature metadata and shared Lua utilities
├── firmware/      Marlin, RepRapFirmware, and Klipper templates
├── generators/    Pure Lua generation and filesystem orchestration
├── models/        UI-independent configuration models
└── ui/            Textual application, controller, adapters, state, and components
```

The UI controller owns deterministic defaults and derived values, while the
adapter converts widget state into `PrinterConfig`. Generators do not depend
on Textual, keeping profile generation testable without launching the terminal
application.

## Documentation

- [Architecture](docs/architecture.md)
- [Development](docs/development.md)
- [IceSL printer documentation](https://gitlab.inria.fr/mfx/icesl-documentation/-/wikis/Printer-profile)
- [Textual documentation](https://textual.textualize.io/)

## Acknowledgements

- [Textual](https://textual.textualize.io/)
- [IceSL printers](https://github.com/shapeforge/icesl-printers)
- [IceSL printer documentation](https://gitlab.inria.fr/mfx/icesl-documentation/-/wikis/Printer-profile)
