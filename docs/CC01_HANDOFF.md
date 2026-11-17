# CC-01 Blender Project Handoff

## Current state

The Chaos Chamber CC-01 builder is modularized under `src/`. The production
world convention is enforced as Blender Z-up: X is width, Z is height, and
front/glass is negative Y. Assemblies are authored in a local Y-up,
positive-Z-front frame and mapped by `CHAOS_CHAMBER_ROOT`.

P0 validation is complete and passes in Blender 5.3.0:

- World envelope: 420 × 730 × 250 mm exactly.
- Track channel width: 23 mm.
- Track wall height: 10 mm.
- U-turn centreline radius: 30 mm.
- Track continuity: maximum sampled step 10.798 mm.
- Straight-run slopes: 5.906 degrees.
- Minimum measured glass clearance: 3 mm.

The latest report is `outputs/validation/phase1_validation.json`.

## Main entrypoints

```powershell
python -m py_compile build_cc01.py validate_cc01.py src/*.py
F:\soft\BLENDER\blender.exe --background --python validate_cc01.py
F:\soft\BLENDER\blender.exe --background --python render_cc01.py
F:\soft\BLENDER\blender.exe --background --python isolate_cc01.py -- --group track --render
```

`validate_cc01.py` rebuilds the scene before checking it. `render_cc01.py`
writes the next full review image to `outputs/full/`. Isolated renders go to
`outputs/isolate/<group>/`.

## Important implementation files

- `src/config.py` — dimensions and coordinate constants.
- `src/build.py` — product assembly and geometry placement.
- `src/paths.py` — shared track centerline and 30 mm bends.
- `src/validate.py` — read-only world-space validation.
- `docs/phase_1_task_list.md` — remaining Phase 1 work.

## Next recommended work

Begin the Phase 2 work tracked in `docs/phase_2_task_list.md`. The primary
carryover is `TBD-001`: upper-retainer and lower-release gate travel, stops,
interlock, and release timing. Continue with mechanical detailing, serviceable
electronics, animation tests, and PBR material refinement.

## Git note

The previous session could not commit because this environment could read
`.git` but could not create `.git/index.lock`. Once repository write access is
available, review and commit the P0 files; do not automatically add the
reference DOCX or generated `__pycache__` files.
