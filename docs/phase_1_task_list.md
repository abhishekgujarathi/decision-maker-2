# Chaos Chamber CC-01 Phase 1 Task List

Phase 1 is complete only when the industrial blockout is dimensionally consistent, visually validated from all required views, and mechanically plausible enough to begin detailed Phase 2 construction.

## Baseline already present

- [x] 420 × 730 × 250 mm enclosure target defined.
- [x] Walnut side panels, frame, header, lower chassis, rear cover, and basic feet modeled.
- [x] Front glass, gasket, hinges, latch, and retainers modeled.
- [x] Upper-left hopper and input assembly blockout placed.
- [x] Three-run S-track and three-turn reference silhouette created.
- [x] Selector and YES/NO pocket locations established.
- [x] Internal backing, electronics tray, basic wiring, camera, lighting, and materials added.
- [x] Full and isolated render workflows created.

## P0 — Resolve before detailed modeling

- [x] Resolve the coordinate convention: Blender world is Z-up, front/glass is negative Y; local assembly authoring is Y-up with positive Z toward the front, mapped by the build root.
- [x] Correct the actual U-turn radius to 30 mm, inside the 26–32 mm specification range, using one shared centerline consumed by both builder and validator.
- [x] Verify the complete envelope in world space: the validator measures 420 W × 730 H × 250 D mm with a 2 mm tolerance.
- [x] Build `validate_cc01.py` / `validate_cc01.bat` and `src/validate.py`; the JSON report covers envelope, track width, wall height, bend radius, continuity, slopes, and glass clearance.

## P1 — Orthographic and clearance validation

- [x] Add front orthographic camera and render.
- [x] Add left/right side orthographic camera and render.
- [x] Add top orthographic camera and render.
- [x] Add rear orthographic camera and render.
- [x] Temporarily enable `SHOW_FRONT_GLASS = True` and inspect the glass, gasket, track, fastener, and ball clearances.
- [x] Confirm the track remains inside the chamber and does not enter the glass clearance envelope.

## P1 — Mechanical blockout validation

- [x] Define one continuous ball-centre path from input through all three turns to the selector.
- [x] Verify the 18 mm ball has clearance through the full track.
- [x] Replace the display-only ball with a path-test or animation-ready ball object.
- [ ] Resolve upper-retainer and lower-release gate geometry, travel, stops, and interlock logic.
- [x] Connect the input hopper physically to the holding chamber and launch cradle.
- [x] Define selector LEFT/YES and RIGHT/NO states with real hard-stop positions.
- [x] Connect both selector branches to their respective output pockets.
- [x] Verify that both branches cannot cross-feed.
- [x] Confirm output catch plates, EPDM pads, sensors, and indicators are physically positioned.

## P2 — Prepare for Phase 2

- [x] Split the track into named runs, U-turns, exit guide, brackets, and fastener groups.
- [x] Create a separate `BALL_ASSEMBLY` collection.
- [x] Add production-style component identifiers such as `CC-310`, `CC-420`, and `CC-530`.
- [x] Add service-access and rear-panel checks.
- [x] Record unresolved dimensions and tolerances in a TBD register.

## Phase 1 exit criteria

- [x] All four orthographic views agree.
- [x] Envelope and coordinate checks pass.
- [x] Glass can be shown without intersections.
- [x] Ball path is continuous and clearance-safe.
- [x] Selector has two distinct physical routes.
- [x] Input, selector, and output assemblies are ready for detailed Phase 2 construction.
