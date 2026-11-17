# Chaos Chamber CC-01 Project Overview

Updated: 2026-11-14

## Project

Chaos Chamber CC-01 is a modular Blender model of a mechanically believable
ball-routing chamber. The repository contains the procedural builder,
validation scripts, materials, scene presentation, isolated assembly renders,
and design documentation.

The authored unit is millimetres. Blender uses Z-up world coordinates, with
the front glass toward negative Y. Major assemblies remain separated into
named objects and collections so the model stays editable and animation-ready.

## Current status

### Overall

- Phase 1 industrial blockout and P0/P1 validation: complete.
- Phase 2 foundation and mechanical-detail pass: started.
- Latest validation: passed.
- Connected Blender file: `L:\coding\YOUTUBE\blenderr\codex.blend`.
- Active Blender scene: `Scene` with 170 objects and 9 major collections at
  the time of the latest MCP inspection.

### Latest validated values

- Overall envelope: 420 W x 730 H x 250 D mm.
- Track channel width: 23 mm.
- Track wall height: 10 mm.
- U-turn centreline radius: 30 mm.
- Ball diameter: 18 mm.
- Nominal track side clearance: 5 mm.
- Minimum measured glass clearance: 3 mm.
- Track and ball paths: continuous and inside the chamber.
- Selector branches: separated into YES and NO routes.
- Input assembly: hopper, holding chamber, gates, interlock, sensor datum,
  and launch cradle present.
- Service access: rear cover, selector hatch, power inlet, switch, and rear
  fasteners present.

The detailed machine-readable report is
`outputs/validation/phase1_validation.json`.

## Completed work

### Repository and builder

- Modularized the builder under `src/`.
- Centralized dimensions and design constants in `src/config.py`.
- Added reusable geometry, sweep, fastener, bevel, and collection helpers.
- Added shared track paths and validated bend geometry.
- Added procedural materials and role-based assignments.
- Added camera, tabletop, backdrop, and lighting setup.
- Added full-scene and isolated-group render entrypoints.

### Product blockout and assemblies

- Enclosure, walnut side panels, frame, header, chassis, rear cover, and feet.
- Front glass, gasket, hinges, latch, and retainers.
- Upper-left hopper, holding chamber, launch cradle, and escapement.
- Three-run continuous S-track with three U-turns.
- Selector gate with YES/NO branch routes and output pockets.
- Internal backing, electronics tray, wiring blockout, camera, lighting, and
  materials.
- Named track runs, U-turns, exit guides, brackets, fasteners, and ball
  assembly collection.
- Production component identifiers, datums, metadata, service-access parts,
  and a dimension/tolerance table.

### Validation and review

- Coordinate convention and world envelope checks.
- Track width, wall height, bend radius, slope, continuity, and chamber-fit
  checks.
- Ball-path continuity and ball/track clearance checks.
- Selector branch separation and input assembly presence checks.
- Service-access and production-object/component-ID checks.
- Front, rear, left, right, and top orthographic review setup.
- Full and isolated render workflows.

## Work still open

The authoritative task lists are:

- Phase 1: `docs/phase_1_task_list.md`
- Phase 2: `docs/phase_2_task_list.md`
- Open decisions: `docs/TBD_register.md`
- Handoff notes: `docs/CC01_HANDOFF.md`

The main controlled carryovers are:

- Final production-detail geometry for track floors, walls, lips, brackets,
  joints, alignment pins, and service removal.
- Animation-ready ball rig or Follow Path test through both selector routes.
- Selector gate thickness, pivot, hub, bearings, hard stops, linkage, return
  spring, and sensor actuation.
- Final YES/NO pocket details, impact pads, sensors, indicators, wiring, and
  service inserts.
- Glass thickness, edge treatment, gasket compression, retainer hardware, and
  final mechanism-to-glass clearance.
- Rear service tool envelope and assembly/removal sequence.
- Routed electronics harnesses, connector clearances, strain relief, and I/O
  documentation.
- Production material refinement, labels, indicator lenses, roughness
  variation, and hidden diagnostic geometry rules.
- Extended Phase 2 validation for IDs, orphan objects, gates, selector states,
  cross-feed, service access, materials, and diagnostic visibility.
- Final Phase 2 orthographic, mechanism, glass-on, isolated, hero, and service
  renders.

## Future phases

### Phase 2: mechanical detail and behavior

Convert the validated blockout into a believable, serviceable, animation-ready
product model. Resolve all TBD items, detail moving mechanisms, test both
selector states, and regenerate `outputs/validation/phase2_validation.json`.

### Phase 3: presentation and production polish

Refine materials, labels, lighting, camera composition, glass readability,
surface variation, final hero renders, exploded/service views, and presentation
assets.

### Phase 4: delivery and maintenance

Freeze a reproducible build and validation workflow, document Blender-version
assumptions, archive approved renders, and maintain the component-ID and TBD
register as the model evolves.

## Useful commands

```powershell
python -m py_compile build_cc01.py validate_cc01.py src/*.py
blender --background --python build_cc01.py
blender --background --python validate_cc01.py
blender --background --python render_cc01.py
blender --background --python isolate_cc01.py -- --group all --render
```

## Source of truth

The written design brief in `ref/` is authoritative when reference images and
older notes disagree. Keep dimensions in millimetres, preserve the coordinate
convention, and update the phase checklist, TBD register, validation report,
and this overview whenever a major assembly or project state changes.
