# Repository Guidelines

## Project Structure & Module Organization

This repository contains Python scripts for generating the Chaos Chamber CC-01 Blender model.

- `build_cc01.py` — compatibility entrypoint for the modular builder.
- `src/config.py` — centralized millimetre dimensions and design constants.
- `src/core.py` — reusable Blender mesh, sweep, fastener, bevel, and collection helpers.
- `src/build.py` — assembly orchestration and geometry construction.
- `src/materials.py` — procedural presentation materials and role-based assignment.
- `src/scene.py` — camera, tabletop, backdrop, and lighting setup.
- `src/paths.py` — shared continuous track centerline and validated bend geometry.
- `src/validate.py` — read-only world-space envelope, dimension, slope, continuity, and glass-clearance checks.
- `src/isolate.py` — argument-driven isolated assembly builds and review renders.
- `isolate_cc01.py` / `isolate_cc01.bat` — isolated-view entrypoints.
- `validate_cc01.py` / `validate_cc01.bat` — rebuild and run the P0 validation report.
- `outputs/full/` — complete-product review renders.
- `outputs/isolate/<group>/` — focused assembly renders and framing metadata.
- `docs/history/` — historical design transcript and thinking notes.
- `docs/phase_1_task_list.md` — current Phase 1 completion checklist and exit criteria.
- `ref/` — design brief and reference images; treat the written brief as authoritative when references differ.
- `claude_*.md` and the exported modeling transcript — historical design notes and implementation context.

Keep major product assemblies as separate named objects and collections so they remain editable and animation-ready.

## Build, Test, and Development Commands

Run syntax checks from the repository root:

```powershell
python -m py_compile cc01_config.py cc01_core.py build_cc01.py src/*.py
```

Run the generator from Blender’s Scripting workspace, or headlessly when Blender is available:

```powershell
blender --background --python build_cc01.py
```

Render a fresh complete-product review image to the next numbered file in `outputs/full/`:

```powershell
blender --background --python render_cc01.py
```

Run the P0 dimension and clearance validation, which writes
`outputs/validation/phase1_validation.json`:

```powershell
blender --background --python validate_cc01.py
```

Render isolated assembly groups into `outputs/isolate/<group>/`:

```powershell
blender --background --python isolate_cc01.py -- --group track --render
blender --background --python isolate_cc01.py -- --group selector,output --render
```

Use `--group all` for the complete scene. The isolated renderer automatically reframes the perspective camera and writes incrementing PNGs plus a small JSON framing record.

After running in Blender, inspect the generated scene and render a basic validation frame with `F12`.

## Coding Style & Naming Conventions

Use Python with four-space indentation, clear function boundaries, and millimetres for authored dimensions. Convert to Blender metres only at geometry creation. The production world is Z-up, with the glass/front toward negative Y. Use `snake_case` for functions and variables, `UPPER_SNAKE_CASE` for configuration constants, and descriptive uppercase object names such as `TRACK_CONTINUOUS` or `DIVERTER_GATE`.

Prefer reusable helpers in `cc01_core.py` over duplicated mesh-generation code. Avoid materials, lighting, or animation changes in geometry-only work unless explicitly requested.

## Testing Guidelines

No automated Blender test suite is currently configured. Every change should at minimum pass `py_compile`, then be tested by running the builder in Blender. Check overall dimensions, object separation, track continuity, clearances, and front/rear orientation.

## Post-Task Loop Hook

The repository contains a non-registered Codex `Stop` hook template in
`.codex/hooks/stop_task_hook.py`. Automatic project-local lifecycle hooks are
disabled here because this host's command runner cannot load the project hook
layer reliably. If a user-level Codex hook is configured and trusted, it may
call this template after a turn; otherwise use the normal task workflow.

The reusable task-level helper remains available for future automation:

```powershell
python tools/task_completion_hook.py --task RF-A3 --status complete --note "Validation passed"
```

Use `--status partial` when the task has progressed but its acceptance criteria
are not yet met, and `--status blocked` only when work cannot continue without
an external decision or state change.

## Commit & Pull Request Guidelines

Use concise imperative commit messages, for example `Add selector linkage geometry`. Pull requests should describe the affected assembly, include validation commands, note any Blender-version assumptions, and attach a viewport or render screenshot for visible geometry changes.

## Security & Configuration Tips

Do not commit proprietary reference assets, credentials, or machine-specific absolute paths. Keep external texture paths configurable and prefer procedural placeholders during development.
