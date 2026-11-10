# Architecture

The application was migrated from the original root-level `main.py` in small,
behavior-preserving phases.

## Architecture boundaries

- `data/` owns feature metadata, tooltips, and shared Lua utility code.
- `firmware/` owns firmware-specific Lua templates.
- `firmware/registry.py` maps the numeric firmware values used by IceSL to
  named template sets and exposes the same typed template bundle to the UI
  editor, avoiding firmware-specific branching in the application shell.
- `models/` contains UI-independent configuration and profile naming rules.
- `generators/` contains pure content generation and filesystem orchestration.
- `app.py` is the application entry point and injects `GenerationService` into
  the legacy Textual screen.
- `ui/app.py` owns the Textual screen orchestration. `ui/components.py` owns
  reusable presentation widgets, including `FeaturesTab` for the main printer
  feature form, the parameterized `ProfileTab` for quality and material forms,
  and `PrinterEditorTab` for firmware Lua editors. `printer_to_lua/main.py`
  remains a compatibility launcher for code that imports the old module path.
- `ui/state.py` owns the conditional projection of printer settings into
  firmware editor sections.
- `ui/controller.py` owns deterministic UI coordination policies such as
  firmware editor selection and quality/material defaults; it does not depend
  on Textual widgets.
- `ui/adapter.py` snapshots Textual controls into `PrinterConfig`; generation
  actions do not directly assemble Lua or open files.

The screen's data-driven layout remains in `ui/app.py`, while generated output
is represented by the reusable `GeneratedOutput` component. Its imports
resolve through package-owned data and firmware modules; the removed root
`dicts` package is no longer part of the application.
The remaining app methods are deliberately limited to Textual widget
coordination and event dispatch; deterministic policy calculations live in
`ui/controller.py`.

## Generation flow

```text
PrinterConfig
    -> GenerationService.generate()
        -> feature/profile/printer generators
            -> GeneratedProfile
                -> GenerationService.write()
                    -> output/<profile>/
```

Generators do not launch Textual or change process working directories. This
keeps generated Lua behavior testable independently from terminal rendering.

## Phase 5 environment and typing

The workspace targets Textual 8.2.x and configures VS Code/Pylance to use the
project `.venv`. This keeps editor diagnostics aligned with the interpreter
used by the test suite. The duplicate legacy generation handler was removed,
leaving one service-backed button path. Select and input event values are
normalized at the UI boundary, and the complete screen is now clean under
Pylance's current diagnostics.
