# CC-01 Refinement Task List — Pre-Phase-2 Alignment and Part-Integrity Pass

Created: 2026-11-14
Basis: live inspection of `codex.blend` (Blender 5.3.0, 242 objects) over MCP, plus
`PROJECT_OVERVIEW.md`, `AGENTS.md`, `docs/phase_2_task_list.md`, `docs/TBD_register.md`,
`docs/CC01_HANDOFF.md` and the design brief in `ref/`.
Status: **analysis only. No scene data or source files were modified.**

All coordinates below are **world millimetres** (Z-up, front glass toward −Y).
`CHAOS_CHAMBER_ROOT` maps authored local coordinates to world as
`world_x = x`, `world_y = −local_z`, `world_z = local_y`.
Datum-table values stored as local `z` therefore read as world `y = −z`.

Priority key: **P0** = blocks Phase 2 (the mechanism cannot work or be validated),
**P1** = fix before detailing the affected assembly, **P2** = hygiene, may overlap Phase 2.

---

## 1. Summary

Phase 1 validation passes, but it checks envelope, lengths and the XZ-plane path only.
A solid-geometry pass (mesh-versus-mesh intersection, 3D ball sweep, datum comparison)
shows the model is a good blockout but not yet one coherent mechanism.
Eight root causes explain nearly all of the problems:

| ID | Root cause | Effect |
| --- | --- | --- |
| R1 | The ball plane is 9.75 mm too far back. The ball centre sits at y = −63.0, exactly in the track floor mid-plane. | 173 of 179 path samples interfere with the track; the ball is half buried in the floor. |
| R2 | There is no consistent mounting plane. Track standoffs end at y = +33, the track floor is at y = −63, and the backing is at y = +60. | The track is not attached to anything (95 mm gap). |
| R3 | Backing plates, servo, linkage, springs and harnesses are on the glass side of, or inside, the ball plane. | They block or intersect branches and the ball. |
| R4 | Input assembly parts are mis-placed and solid: hopper body 63 mm off axis; throat, tube and bridge are solid blocks; gates are undersized. | The ball cannot physically enter or be held. |
| R5 | Selector topology conflicts: the NO branch overlaps the exit guide, YES and NO branches overlap, and the "gate" is a flat diamond. | The selector cannot divert and cannot be rigged. |
| R6 | Output pockets are closed lids with no floor, a mis-oriented catch plate, legacy guides and harnesses passing through. | The ball cannot enter or rest. |
| R7 | Enclosure: the glass is unparented and hidden; there is no bottom, rear or top panel; vents, inlet and switch float; feet float; the hinge is embedded. | Presentation and clearance checks are unreliable. |
| R8 | Rig-readiness and validation blind spots: 128 objects have origin at world zero, and no check exists for solid intersection, hollow bores, support chains or the glass object. | Problems stay invisible to the existing validator. |

The track mesh itself is internally consistent: with the ball moved to y = −72.75 the sweep
is clear everywhere except the input drop. Most of the work is re-seating parts onto
correct datums, not rebuilding the track.

---

## 2. How this was measured

1. Dumped every object: parent, collection, world bounding box, material, metadata.
2. Built evaluated-mesh BVH trees for 222 mesh objects and ran exact mesh-versus-mesh overlap tests
   (fasteners, washers and screws excluded): **249 intersecting pairs**. Roughly a third are intended
   joins (frame corners, wall-on-floor embed of 0.7–0.8 mm, support-to-standoff, pin-in-bush); the rest cluster in
   the areas listed in section 4.
3. Extracted the 179 ring centres of `BALL_CENTRE_PATH` and measured the nearest-surface distance to every
   track floor and wall, at the current position and shifted −9.75 mm in Y.
4. Compared the declared `datum_table` on `CHAOS_CHAMBER_ROOT` with measured positions.
5. Cross-checked against the written brief in `ref/Chaos_Chamber_CC-01_Industrial_Design_Brief.txt`
   (authoritative per `AGENTS.md`).

**The model is procedural. Fix everything in `src/*.py` and rebuild; do not hand-edit the `.blend`.**
Re-measure after each rebuild.

---

## 3. Decisions needed before editing

- [ ] **D-01 Ball-plane datum.** Recommended: `Y_BALL = −(track floor front face + ball radius) = −72.75`.
  Move all ball-plane parts −9.75 mm in Y (ball, path, escapement, hopper, selector gate/hub/shaft).
  Evidence: the track floor (front face −63.75), the walls (−73…−63), the cradle floor and the cradle walls
  already agree with a ball at −72.75, and the pocket cavity centre (−75) is only 2.25 mm from it.
  Alternative: move the track, branches and pockets +9.75 instead; that disturbs far more parts and
  pulls the pocket back plates into the ball.
- [ ] **D-02 Mechanism mounting plane.** Recommended: move `INTERNAL_BACKING` forward to a "mechanism plate" at about
  y = −54…−50 with ~8 mm standoffs behind the track floor (floor back face −62.25). The electronics tray
  (y −46.5…−43.5) then sits directly behind it, actuators and harnesses live behind the plate, and the
  rear service hatch can actually reach the selector actuator. Alternative: keep the backing at y = +60
  and use ~100 mm standoffs (long, flexible, unrealistic for a 1.5 mm sheet track).
- [ ] **D-03 Selector junction topology.** Recommended: the exit guide drops the ball vertically onto the gate apex
  (ball leaves the guide end near x ≈ 20), and both branches start below that point.
  A fork where a leftward-moving ball must be deflected back to the right (current NO branch) is not
  gravity-feasible. Brief points to reconcile: P7 (+35, 350) → P8 (0, 325) → P9 (±75, 255) → P10 (±75, 190).
  Confirm with a rigid-body or path test for both states.
- [ ] **D-04 Gate size and angle.** Brief 9.3: ~25 mm wide, 2 mm plate, ~18–22° total travel.
  Current: ~76 × 56 mm diamond with ±34° metadata (TBD-004). Recommended: adopt the brief
  unless the simulation proves it needs more, and update TBD-004.
- [ ] **D-05 Door definition.** Brief 4.3: left-hinged glass panel, right quarter-turn latch.
  Confirm that the hinged door = glass + gasket + retainers (frame posts stay fixed).
- [ ] **D-06 Wall height.** Walls are effectively 9.25 mm above the floor face, only 0.25 mm above the ball centre line.
  Recommended: 12 mm (brief allows 8–12) or add the brief's raised lip on bends.

---

## 4. Refinement tasks

### A. Datums and global alignment

- [ ] **RF-A1 (P0) Re-seat the ball plane (R1).**
  Evidence (measured): ball path centre y = −63.0 for all 179 samples; `STEEL_BALL_PATH_TEST` at (−145, −63, 638);
  `STEEL_BALL_INPUT` at (−145, −64, 631); track floor y −63.75…−62.25; 173/179 samples interfere (min −9.0 mm).
  Shifting −9.75 mm leaves only samples 7–10 interfering (−1.8…−7.65 mm), all at the input drop.
  Action: add `Y_BALL` to `src/config.py`; derive every ball-plane part from it
  (ball, path, hopper throat/collar/rim/body, escapement tube/gates/guides/pins/bushes/springs/solenoid/sensors,
  selector gate/hub/pivot shaft/linkage/stops). Remove hard-coded y offsets.
  Done when: V-01 reports zero negative-clearance samples on both routes.
- [ ] **RF-A2 (P0) Rebuild the bracket chain to a real mounting plane (R2, per D-02).**
  Evidence (measured): standoffs y 33…53, support plates y 46…50, bracket fasteners y 34.5…39.5, backing y 58…62,
  track floor back face y −62.25. Gaps: standoff to track 95 mm, standoff to backing 5 mm, support plate to backing 8 mm.
  Action: place the plate per D-02; standoffs span exactly floor back face to plate front face; fasteners go through the plate.
  Done when: V-05 finds every track piece connected to the plate through a bracket with ≤0.5 mm gaps.
- [x] **RF-A3 (P0) Correct the datum table.** _Implemented 2026-11-17: added the production-world ball-plane datum, gate pivot, glass outer face, and ball-plane pocket centres; Blender named-datum validation passes._
  `track_floor_z = 63` is the floor mid-plane, not the ball plane. Add `ball_plane_z`, `plate_front_z`,
  `gate_pivot` and a `glass_outer_face`. Update `selector_pivot` and `input_centerline` to `Y_BALL`.
- [ ] **RF-A4 (P1) Intentional-contact whitelist.**
  Wall-on-floor embed (≤0.8 mm), frame corner joints, support/standoff pairs, pin/bush pairs.
  V-02 reports only non-whitelisted intersections.

### B. Enclosure and housing

- [x] **RF-B1 (P0) Put the front glass in the model (R7).** _Done 2026-11-14: stale unparented glass removed, `FRONT_GLASS` parented to root, unhidden, materials merged, `SHOW_FRONT_GLASS=True`._
  Evidence (measured): `FRONT_GLASS` has no parent, `hide_viewport` and `hide_render` are both true, and its mesh is in
  root-local coordinates, so its world box is x ±185, y 127…676, z 98…102 (a flat sheet behind the cabinet).
  Correct pose after parenting: y −102…−98, z 127…676 (matches the declared glass inner face y = −98).
  Action: parent to `CHAOS_CHAMBER_ROOT` with identity inverse, unhide, merge duplicate `MAT_LOW_IRON_GLASS(.001)`.
  Done when: the glass renders in front, and V-06 measures clearance against the real object (≥ 3 mm).
- [ ] **RF-B2 (P1) Glass seating and retention.**
  Evidence: frame back face −105, glass front −102 (3 mm gap); gaskets span y −100…−94, overlapping the glass by 2 mm and
  sitting behind it; no retainers or screws; glass 370 mm wide over a 356 mm opening (7 mm lap each side).
  Action: model the gasket between frame and glass, add retainer strips and M3 screws (brief 4.3),
  then close TBD-003 with the fastener-head clearance.
- [ ] **RF-B3 (P1) Missing closure panels.**
  Evidence: no bottom plate, no fixed rear panel (`REAR_SERVICE_COVER` covers only z 140…640), no top panel.
  Vents (z 52.5…55.5), `POWER_INLET` (z 59…81) and `MAIN_SWITCH` (z 109…121) have nothing behind them.
  Brief 12 lists `REAR_PANEL` and `BASE_CHASSIS`.
  Action: add bottom plate, lower and upper rear panels with cut-outs for inlet, switch and vents, and a top cap behind the header.
- [ ] **RF-B4 (P1) Door and hinge.**
  Evidence: `HINGE_LEAF_0/1` (x −202…−186) overlap both `WALNUT_LEFT` and `FRAME_POST_L`; barrels (x −206…−198) are embedded in the
  panel (x −210…−192); `QUARTER_TURN_LATCH` overlaps `WALNUT_RIGHT` and `FRAME_POST_R`.
  Action (per D-05): `GLASS_DOOR` assembly parented to the hinge axis; split leaves into door-side and cabinet-side;
  barrel origin and axis on the pin; latch and strike aligned.
- [ ] **RF-B5 (P2) Duplicate base sides.** `BASE_SIDE_LEFT/RIGHT` are coincident inside `WALNUT_LEFT/RIGHT` (18 × 250 × 115 overlap, z-fighting).
  Brief 4.5 says the chassis sides are black powder-coat: split the walnut panel at z = 125 or drop the duplicates.
- [ ] **RF-B6 (P2) Feet.** Only two `RUBBER_FOOT` objects exist (x ±170, y 74…96, both toward the rear), inside the footprint with no plate above them.
  Action: four feet under the bottom plate, named FL/FR/RL/RR.

### C. Input assembly (Zone 01)

- [x] **RF-C1 (P0) Hopper body off axis.** _Done 2026-11-14: `HOPPER_UPPER` is now a hollow funnel (`loft_rect_shell`, 2 mm walls, bore 35x25 top / 27x25 bottom) centred on `BALL_Z`; rim depth 36 mm (front y -90.75, 7.25 mm from glass); rim embeds 0.5 mm into hopper; bottom 1 mm into throat._
  Evidence: `HOPPER_UPPER` y −21…21 (centre 0); rim, throat, collar and tube are centred at y ≈ −63; gap to the rim back (y −41.5) is 20.5 mm,
  so the body floats 63 mm off axis.
  Action: centre on `Y_BALL`, join to the rim, set real wall thickness. After D-01 the rim front would sit at y ≈ −94.25
  (3.75 mm from glass); reduce rim depth from 43 mm to ≤ 36 mm to keep margin.
- [x] **RF-C2 (P0) Solid blocks where bores are needed.** _Done 2026-11-14 (geometry): throat and collar are hollow rings (bore 22 mm, 2 mm wall); `ESCAPEMENT_TUBE` is a front U-channel (bore 26.5 x 22); bridge is a rear U-clamp. Ball clears each by >= 1.0 mm at y 596-678. Gate slots deferred to RF-C3._
  Evidence (mesh-intersection): `HOPPER_THROAT` is a solid Ø26 × 12 disc, `HOPPER_THROAT_COLLAR` a solid Ø30 × 3 disc,
  `ESCAPEMENT_TUBE` a solid 24 × 24 × 52 box (8 vertices), `HOLDING_TO_CRADLE_BRIDGE` a solid 28 × 10 × 48 box.
  The ball intersects all of them (ball vs throat 104 faces, vs collar 168, vs tube 48, vs bridge 100).
  Action: hollow bores ≥ 22 mm (18 + 2 × 2 mm), wall ≥ 1.5 mm; throat as a funnel ring; tube as a U-channel or hollow section.
  Done when: V-03 confirms bore diameter and the ball clears every part at each queue position.
- [ ] **RF-C3 (P0) Escapement gates cannot hold or release a ball.**
  Evidence: both gates are 24 × 4 × 4 mm at y −55…−51, the rear 4 mm strip of a 24 mm-deep tube (y −75…−51).
  Travel is 10 mm against a 24 mm bore, so the OPEN gate still covers 14 mm and leaves about 10 mm clear for an 18 mm ball.
  Gate centre spacing is 18 mm (z 625 / 607) against the declared queue spacing of 22.5 mm; queue datums (z 629 / 606) are not at
  gate top + 9 mm (636 / 618).
  Action: gate as a pin or blade crossing the lower hemisphere of the ball in the `Y_BALL` plane; travel ≥ bore + 2 mm
  (or a narrower pin); spacing ≥ 22.5 mm; derive datums from gate geometry; update TBD-001. Verify with V-08.
- [ ] **RF-C4 (P0) Cradle-to-Run-01 handoff.**
  Evidence: cradle (x −158…−132, z 590…638) and the escapement tube overlap the first ≈ 13 mm of Run 01; the vertical ball drop at
  x = −145 passes through Run 01 floor and walls (samples 7–10, up to −7.65 mm).
  Action: end the cradle above Run 01 with a defined entry (curved ramp or lip), or start Run 01 at x ≈ −130; tangent, no overlap.
- [ ] **RF-C5 (P1) Actuators in the ball zone.**
  `ESCAPEMENT_SOLENOID` (x −138…−104, y −84…−66) intersects the tube, bridge, cradle wall and backing; the sensor bracket intersects the throat,
  cradle wall and bridge. Move behind the mechanism plate with shafts through slots. Check pin/bush engagement.
- [ ] **RF-C6 (P1) Duplicate balls.** `STEEL_BALL_INPUT` (−145, −64, 631) and `STEEL_BALL_PATH_TEST` (−145, −63, 638) overlap each other (102 faces).
  Brief: a single `STEEL_BALL_01`. Keep one ball, origin at centre, start on the queue position.
- [ ] **RF-C7 (P1) Escapement backing on the wrong side.** `ESCAPEMENT_BACKING` y −77…−73 is in front of the tube and cradle walls and touches the ball.
  It belongs behind the mechanism (see D-02).

### D. Track (Zone 02)

- [ ] **RF-D1 (P0) Re-run the ball sweep after RF-A1/RF-C4.** All 179 samples must be ≥ 0 (resting floor contact) with lateral clearance ≥ 2 mm; add both selector routes.
- [ ] **RF-D2 (P1) Wall retention.** Per D-06, raise walls or add the bend lip; update TBD-002 with the tolerance stack.
- [ ] **RF-D3 (P1) Bracket layout.** After RF-A2, re-space supports so none sit in the ball path or the view, and U-turn supports clear the outer wall.
- [ ] **RF-D4 (P1) Exit guide end.** Define the exact release point and drop height onto the gate apex (see RF-E1).

### E. Selector (Zone 03)

- [ ] **RF-E1 (P0) Junction layout (per D-03).**
  Evidence: exit guide floor x 19…145, z 308…341; `NO_BRANCH_FLOOR` x 10.5…87.5, z 238.5…336.5 overlaps it (68 × 28 mm);
  `YES_BRANCH_FLOOR` and `NO_BRANCH_FLOOR` overlap each other (17 mm in X, 13 intersecting faces); YES walls intersect the NO floor and walls.
  Branch tops (z ≈ 336–339) are above the hub (z 315) and the guide end.
  Action: re-derive branches from the junction apex; start below the arrival point; mutual clearance ≥ 5 mm.
- [x] **RF-E2 (P0) Diverter gate is a flat diamond.** _Implemented 2026-11-18: replaced with a pivot-centered 26 × 18 × 2 mm upright blade and explicit ±11° hard-stop metadata; P0 validation passes._
  Evidence: vertices (±38, 315), (0, 343), (0, 287), 2 mm thick along Y at y −60…−58, parallel to the track floor and behind the ball plane.
  A flat diamond cannot divert a ball.
  Action (per D-04): upright blade, in-plane length ~25–30 mm, 2 mm thick, height along Y ≥ 14 mm centred on `Y_BALL`;
  pivot on the Y axis; origin at the pivot; LEFT and RIGHT as rotation states.
- [ ] **RF-E3 (P1) Pivot assembly.** `PIVOT_SHAFT` (y −81…−35) intersects `YES_BRANCH_FLOOR` (48 faces), the backplate and the linkage;
  hub (y −61…−53) is behind the ball plane. Axis along Y through the plate with a bearing boss; hub and gate at `Y_BALL`; relieve branch floors around the hub.
- [x] **RF-E4 (P1) Stops.** _Implemented 2026-11-18: removed the duplicate YES/NO branch stops and retained one compact, contact-capable DIVERTER_STOP per side at the declared ±11° blade limits; P0 validation passes._
  Keep one stop per side with contact faces at the gate end positions; settle angles per D-04; update TBD-004.
- [x] **RF-E5 (P0) Servo, linkage, spring and limit sensors in the wrong place.** _Implemented 2026-11-18: actuator hardware is now behind the mechanism plate and within the 62 mm service-hatch width; the output shaft deliberately passes through the plate while the servo body, linkage, spring, and sensors clear it. P0 validation passes._
  Evidence: `SELECTOR_SERVO` (x 42…78, y −90…−64, z 284…314) intersects `NO_BRANCH_WALL_L` (36 × 9 × 30 mm), `NO_HARD_STOP` and the exit guide wall;
  `SERVO_OUTPUT_SHAFT` and `SELECTOR_LINKAGE` intersect branch floors and walls; `SELECTOR_RETURN_SPRING` intersects `YES_BRANCH_WALL_L`;
  limit sensors sit in front of the plate. The servo (x 42…78) is also outside the rear service hatch window (x ±31), so it cannot be serviced through it.
  Action: relocate everything behind the mechanism plate and inside the hatch window; shaft passes through the plate.
- [ ] **RF-E6 (P1) Cross-feed protection.** Add a geometric divider below the apex so YES and NO routes cannot share space; test with V-08.
- [ ] **RF-E7 (P1) Backplate on the wrong side.** `SELECTOR_BACKPLATE` y −77.5…−72.5 is in front of the branch walls, hiding them from the glass. Merge into the mechanism plate (D-02).

### F. Output assembly (Zone 04)

- [x] **RF-F1 (P0) Pocket lids are closed.** _Implemented 2026-11-18: both pocket tops now have 26 mm entry slots aligned to the branch entry; P0 validation passes._
  Add an entry slot or funnel ≥ 22 mm wide aligned to the branch end, or open the top.
- [x] **RF-F2 (P0) Pocket interior.** _Implemented 2026-11-18: replaced the mis-oriented catch geometry with 18° inclined solids, rubber-faced at the intended contact surface; both pockets now declare a BALL_Z-aligned rest datum and opposed optical sensor beam datum. P0 validation passes._
  Evidence: no pocket floor or exit; `*_CATCH_PLATE` is a vertical plate parallel to the glass (44 × 3 × 60 at y −78.5…−75.5, z 133…193)
  extending 12 mm below the pocket sides (z 145); the rubber pad strip (y −78…−72, z 148…158) sits inside the ball volume.
  Brief 9.4: inclined guide plus rubber-backed stop plate.
  Action: inclined catch plate with the pad on its surface; defined ball rest position; sensor beam through the rest position.
- [x] **RF-F3 (P1) Legacy guides.** _Implemented 2026-11-18: removed the obsolete YES/NO solid guide blocks; the production branch channels now provide the inclined routing guide. P0 validation passes._
- [x] **RF-F4 (P1) Alignment.** _Implemented 2026-11-18: both branch floor endpoints align with their 26 mm entry slots; floor + 0.75 mm sheet + 9 mm ball radius resolves to BALL_Z, and the pocket sensor beams use that same datum. P0 validation passes._ Check branch end x/z against the entry slot; pocket centre y (−75) versus `Y_BALL` (−72.75);
  sensors (y −90…−82), indicators (y −92.5…−87.5) and inspection windows (y −91.5…−88.5) relative to the ball after the shift; sensor beam height versus ball centre (TBD-005).
- [x] **RF-F5 (P1) Harness through pockets.** _Implemented 2026-11-18: both harnesses now route behind the mechanism plate and are retained by explicit clips; detailed intersection checking reports zero harness collisions outside those intended clips. P0 validation passes._ `WIRING_HARNESS` (x −110…2, y −68…−60, z 87…285) intersects `OUTPUT_DIVIDER` and passes through the YES pocket zone;
  `SENSOR_HARNESS` (x 50…61, y −63.5…−60.5, z 88…290) intersects the NO branch, guide, pocket top and back. Reroute behind the plate with clips.

### G. Electronics and rear

- [x] **RF-G1 (P1) Electronics mounting.** _Implemented 2026-11-18: control board, driver, and power supply now sit inside the tray footprint on four dedicated standoffs each; detailed checking finds no unintended electronics intersections. P0 validation passes._ `POWER_SUPPLY` (z 42…74) hangs 10 mm below the tray bottom (z 52.5) and intersects the tray plane;
  `CONTROL_BOARD` (y −58…−50) and `MOTOR_DRIVER` (y −60…−48) float 3.5 mm and 1.5 mm in front of the tray with no standoffs. Mount on standoffs inside the tray extents.
- [ ] **RF-G2 (P1) Service hatch.** `SELECTOR_SERVICE_HATCH` is a solid overlapping `REAR_SERVICE_COVER`; cut an opening in the cover and make the hatch a plate with fasteners.
  Window must match the actuator position (RF-E5).
- [ ] **RF-G3 (P2) Rear tool envelope** and removal sequence: carry over from Phase 2 item 2.6.

### H. Rig-readiness and hygiene

- [ ] **RF-H1 (P1) Pivot origins.** 128 mesh objects have origin at world (0, 0, 0) with baked vertices. Moving parts affected: both escapement gates,
  `ESCAPEMENT_INTERLOCK_LINK`, `SELECTOR_LINKAGE`, `SELECTOR_SERVO`, both balls, hinge leaves.
  Brief 13 forbids pivots at arbitrary origins. Set origins at pivot or centre; add a `core.py` helper that authors in local space.
- [ ] **RF-H2 (P2) Naming and duplicates.** Eight `.001` objects (`RUBBER_FOOT.001`, `SELECTOR_LIMIT_SENSOR.001`, pocket and sensor fastener pairs); unused `MAT_LOW_IRON_GLASS`;
  component IDs are per assembly, not per part (needed by Phase 2.10).
- [ ] **RF-H3 (P1) Missing brief components.** `START_BUTTON`, angular output gate, selector cam or gearmotor (servo acceptable if documented),
  amber status indicator on the chassis, glass retainers and screws, `REAR_PANEL`, `BASE_CHASSIS` plate. Decide build or defer and log in the TBD register.
- [ ] **RF-H4 (P2) File hygiene.** About 12 text datablocks including `build_cc01.py.010` reload copies; `PROJECT_OVERVIEW.md` still says 170 objects and 9 collections (now 242 objects, 10 top-level collections plus track sub-collections).
- [ ] **RF-H5 (P2) Maintainability.** `src/build.py` is about 30 KB; split per assembly (input, track, selector, output, housing) while editing.

---

## 5. Validation upgrades (add before fixing, so each step is verifiable)

- [ ] **V-01** 3D ball sweep on both routes: distance to floor, walls and gate at ≤ 2 mm sample spacing; fail on any value < 0 beyond resting contact.
- [ ] **V-02** Solid-intersection report using BVH with the RF-A4 whitelist; fail on anything else.
- [ ] **V-03** Bore check: ray-cast the throat, tube, cradle and pocket entries; bore ≥ 22 mm.
- [ ] **V-04** Datum conformance: declared datums versus measured positions (ball plane, pivot, glass face).
- [ ] **V-05** Support-chain connectivity: every part must touch a host within 0.5 mm; flags floating parts (hopper body, vents, feet).
- [ ] **V-06** Glass object check: exists, parented to root, visible, matches datum; clearance measured against the real object.
- [ ] **V-07** Origin check: objects tagged `moving` must have origin at pivot or centre.
- [ ] **V-08** Gate state sweep: pose LEFT and RIGHT (and escapement open and closed); no intersection and no cross-feed.
- [ ] **V-09** Hidden-object whitelist: only diagnostic objects may be hidden.

---

## 6. Phase 2 items to re-open

| Phase 2 item | Status now | Why |
| --- | --- | --- |
| 2.1 Establish named datums | `[x]` → re-open | Datums disagree with the ball plane and the glass pose (RF-A1, RF-A3, RF-B1). |
| 2.2 Replace hopper blockout (rim, throat, mounting) | `[x]` → re-open | Throat and collar are solid; body floats (RF-C1, RF-C2). |
| 2.2 Upper retainer / lower release geometry, travel, stops | `[x]` → re-open | Gate size, travel and spacing are wrong (RF-C3). |
| 2.2 No ball-catching ledges at hopper-to-cradle | `[x]` → re-open | Cradle, tube and bridge overlap Run 01 and each other (RF-C2, RF-C4). |
| 2.2 Validate one-ball-at-a-time release | `[x]` → re-open | Never simulated; geometry cannot hold a ball. |
| 2.2 Position input sensor and datum | `[x]` → verify | Sensor bracket intersects throat and cradle wall (RF-C5). |

Items 2.3 to 2.5 should not start until the P0 tasks in A, C, D, E and F are closed.

---

## 7. New TBD register entries

| ID | Item | Needed decision |
| --- | --- | --- |
| TBD-007 | Ball-plane Y datum | D-01: confirm `Y_BALL = −72.75` and pocket centre alignment. |
| TBD-008 | Mechanism plate position and standoff length | D-02. |
| TBD-009 | Gate size and travel angle | D-04: brief 18–22° versus current ±34°. |
| TBD-010 | Wall retention height and bend lip | D-06. |
| TBD-011 | Glass door and gasket seat | D-05 and RF-B2. |
| TBD-012 | Pocket entry geometry and ball rest position | RF-F1, RF-F2. |

---

## 8. Execution order and resume gate

1. Commit or back up the current state (the handoff notes an `.git/index.lock` problem) and save a copy of `codex.blend`.
2. Resolve D-01 to D-06.
3. Add V-01, V-02, V-05, V-06 first so every later step is measurable.
4. RF-A1 and RF-A3 (datums in `src/config.py`), then RF-B1 (glass), so all renders and clearance checks include the glass.
5. RF-A2 (mechanism plate and bracket chain).
6. Input assembly and handoff: RF-C1 to RF-C7, RF-D1.
7. Selector and outputs together, since they interlock: RF-E1 to RF-E7, RF-F1 to RF-F5.
8. Electronics and rear: RF-G1, RF-G2, RF-B3, RF-B4, RF-B5, RF-B6.
9. Rig-readiness before Phase 2.9: RF-H1, RF-H3.
10. Update `docs/phase_2_task_list.md`, `docs/TBD_register.md`, `docs/CC01_HANDOFF.md`, `PROJECT_OVERVIEW.md`, then regenerate validation output.

**Phase 2 may resume when all of these hold:**

- [ ] Zero non-whitelisted solid intersections (V-02).
- [ ] Ball sweep clear on both routes with lateral clearance ≥ 2 mm (V-01).
- [ ] All tubes, throats, cradles and pocket entries hollow with bore ≥ 22 mm (V-03).
- [ ] Datum table matches measured geometry (V-04).
- [ ] No floating parts; every part has a host (V-05).
- [ ] Glass present, parented, visible, and clearance ≥ 3 mm measured against it (V-06).
- [ ] Moving parts have correct pivots (V-07); gate states are intersection-free (V-08).
- [ ] D-01 to D-06 recorded in the TBD register.

---

## 9. What is already sound (leave alone)

- Overall envelope 420 × 730 × 250 mm and the Z-up, front −Y convention.
- Track channel width, bend radius, slope and bend continuity: the mesh is consistent once the ball plane is corrected.
- Hierarchy and collection naming, component IDs on every object, materials assigned to all production objects.
- Left/right symmetry of the output pockets and the camera and lighting setup.
- Environment placement (table and back wall).

---

## Appendix A. Key measured data

**Ball plane versus track (world y, mm)**

| Item | Value |
| --- | --- |
| Track floor y range (1.5 mm sheet) | −63.75 … −62.25 |
| Track wall y range | −73.0 … −63.0 |
| Ball path centre | −63.0 (179 of 179 samples) |
| Required ball centre (floor front face − 9) | −72.75 |
| Pocket cavity centre | −75.0 |
| Glass inner face (datum) | −98.0 |

**Ball sweep (179 ring centres)**

| Case | Interfering samples | Minimum clearance |
| --- | --- | --- |
| Current (y = −63.0) | 173 | −9.0 mm |
| Shifted −9.75 mm (y = −72.75) | 10 flagged, 4 real (samples 7–10) | −7.65 mm at sample 8 (x −145, z 603) |

**Declared datums versus actual**

| Datum | Declared | Actual |
| --- | --- | --- |
| `glass_inner_face_world_y` | −98 | Glass hidden, unparented, lying flat at z 98…102 |
| `track_floor_z` | local 63 (y −63) | Floor mid-plane; ball also at −63 (wrong) |
| `selector_pivot` | (0, 315, local z 63) | Hub y −57, shaft y −58, gate y −59 |
| `input_centerline` | (−145, 638, local z 63) | Balls at y −63 and −64 |
| `yes/no_pocket_center` | local z 75 | Pocket cavity centre y −75 (OK) |

**Intersection clusters (non-fastener pairs)**

| Cluster | Notable pairs |
| --- | --- |
| Input | ball with throat, collar, tube, bridge, cradle floor; tube with cradle walls; solenoid with tube, bridge, wall; sensor bracket with throat |
| Track handoff | Run 01 with cradle, tube, bridge |
| Selector | servo, shaft, linkage, spring with branch floors and walls; branches with each other; exit guide with branches |
| Output | branch floors and walls with pocket tops; guides with pockets; harnesses with pockets and divider |
| Housing | walnut with base sides (coincident); hinge leaves with panel and post; latch with panel and post; gaskets with each other |
| Rear and electronics | service hatch with cover; power supply with tray |
