# Chaos Chamber CC-01 Phase 2 Task List

Phase 2 converts the validated Phase 1 blockout into a mechanically believable,
editable, animation-ready product model. Keep authored dimensions in
millimetres and preserve the Z-up / front-negative-Y world convention.

## Phase 2 entry conditions

- [x] Phase 1 envelope validation passes at 420 × 730 × 250 mm.
- [x] Orthographic review cameras and renders exist.
- [x] Front glass and gasket clearance validation passes.
- [x] Continuous 18 mm ball path and 5 mm nominal track side clearance pass.
- [x] Track, ball, selector, service-access, and component-ID collections exist.
- [x] Review and accept the open items in `docs/TBD_register.md` as controlled Phase 2 carryovers.

## 2.1 Mechanical architecture and datum control

- [x] Establish named datums for enclosure, glass inner face, track floor,
  selector pivot, input centerline, and output pocket centers.
- [x] Add a reusable dimension/tolerance table to the configuration module.
- [x] Assign stable component IDs to every production-facing assembly and
  fastener family.
- [x] Confirm all detailed parts remain editable as separate named objects.
- [x] Add an assembly-level custom property describing revision and units.
- [x] Record every changed nominal dimension and tolerance in the TBD register.

## 2.2 Input hopper and escapement

- [x] Replace the hopper blockout with wall thickness, rim, throat, and
  mounting details.
- [x] Define the holding chamber capacity and ball queue spacing.
- [x] Resolve upper-retainer gate geometry, pivot/slide axis, travel, and
  closed/open hard stops.
- [x] Resolve lower-release gate geometry, travel, stop faces, and timing.
- [x] Add the mechanical interlock preventing simultaneous release and retain.
- [x] Add actuator brackets, return springs, pins, bushings, and fasteners.
- [x] Position the input sensor and define its sensing datum.
- [x] Verify the hopper-to-cradle transition has no ball-catching ledges.
- [x] Validate one-ball-at-a-time release through the escapement.

## 2.3 Track and ball system

- [ ] Convert named track pieces into production-detail assemblies with real
  floor, wall, lip, bracket, and fastener interfaces.
- [ ] Verify tangency and elevation continuity at all three U-turns.
- [ ] Add track joint strategy, alignment pins, and service removal features.
- [ ] Add local corner relief and anti-rattle details where required.
- [ ] Create a dedicated animation-ready ball rig or Follow Path setup.
- [ ] Add a path-driven ball test for input, all three turns, selector, YES, and NO.
- [ ] Test ball clearance at straight runs, bends, joins, gate positions, and
  output transitions.
- [ ] Test worst-case ball/track tolerance stack using the TBD dimensions.
- [ ] Add optional hidden diagnostic geometry for path and clearance review.

## 2.4 Selector and routing mechanism

- [ ] Model the selector gate thickness, pivot bore, hub, and bearing surfaces.
- [ ] Define explicit LEFT/YES and RIGHT/NO angular states.
- [ ] Replace placeholder stops with contact-capable hard-stop geometry.
- [ ] Verify the two states cannot overlap or cross-feed.
- [ ] Detail servo/motor mount, output arm, linkage pin joints, and return spring.
- [ ] Add limit-sensor brackets and confirm sensor actuation at both stops.
- [ ] Add a selector state test that drives each route independently.
- [ ] Confirm branch-to-pocket alignment and drop height in both states.

## 2.5 Output pockets and indication

- [ ] Detail YES and NO pocket sidewalls, back plates, catch plates, and exits.
- [ ] Confirm EPDM impact-pad thickness, retention, and replacement access.
- [ ] Position and dimension output sensors against the ball centerline.
- [ ] Detail indicator lenses, bezels, labels, and mounting features.
- [ ] Add wiring paths and strain relief for sensors and indicators.
- [ ] Test that each selector state delivers only to its assigned pocket.
- [ ] Add a removable service insert for each output pocket if required.

## 2.6 Enclosure, glass, and serviceability

- [ ] Detail front glass thickness, edge treatment, gasket section, and clamp
  or retainer hardware.
- [ ] Verify the minimum 3 mm mechanism-to-glass clearance after detailing.
- [ ] Detail hinge leaves, hinge pins, latch strike, and quarter-turn latch.
- [ ] Verify glass/door opening clearance around the selector and pockets.
- [ ] Detail rear service cover, fastener heads, vents, power inlet, switch,
  and selector service hatch.
- [ ] Confirm a realistic tool envelope for rear cover and hatch removal.
- [ ] Add assembly order notes for glass, track, electronics, and rear cover.
- [ ] Validate no hidden part becomes inaccessible after enclosure closure.

## 2.7 Electronics and wiring blockout

- [ ] Place controller, motor/servo driver, power supply, sensors, and
  connectors on serviceable mounting points.
- [ ] Replace placeholder harnesses with routed cable paths and clips.
- [ ] Add connector clearance and bend-radius checks.
- [ ] Separate signal, power, and moving-mechanism routing where practical.
- [ ] Add component IDs and service labels to electronics objects.
- [ ] Document the assumed control I/O for escapement, selector, and outputs.

## 2.8 Materials and visual refinement

- [ ] Refine walnut procedural material with scale and grain direction matched
  to each panel orientation.
- [ ] Create production roles for painted/charcoal parts, stainless steel,
  polished steel, EPDM rubber, glass, labels, and amber indicators.
- [ ] Add roughness variation and restrained edge wear where appropriate.
- [ ] Improve glass readability while preserving clearance inspection renders.
- [ ] Add material assignment validation so no production object is unassigned.
- [ ] Keep diagnostic/path geometry hidden from final product renders.

## 2.9 Animation and behavior tests

- [ ] Animate or procedurally test the upper retainer and lower release gate.
- [ ] Animate the ball from hopper through all three U-turns to the selector.
- [ ] Test selector LEFT/YES and RIGHT/NO states with hard-stop contact.
- [ ] Test output pocket capture and impact-pad contact.
- [ ] Add timing/state metadata for sensors, gates, and selector positions.
- [ ] Verify no animation state causes geometry intersection or cross-feed.
- [ ] Produce a short mechanism review animation or frame sequence.

## 2.10 Validation and automated checks

- [ ] Extend validation for component-ID completeness.
- [ ] Extend validation for named collection membership and orphan objects.
- [ ] Add gate travel, stop, and interlock checks.
- [ ] Add ball clearance checks for both selector states and both outputs.
- [ ] Add glass/gasket/fastener clearance checks after detail modeling.
- [ ] Add service-access and tool-envelope checks.
- [ ] Add material-role and hidden-diagnostic-object checks.
- [ ] Keep `py_compile`, Blender rebuild, validation, and render commands green.
- [ ] Regenerate `outputs/validation/phase2_validation.json`.

## 2.11 Review renders and deliverables

- [ ] Render updated front, rear, left, right, and top orthographic views.
- [ ] Render a glass-on clearance review.
- [ ] Render glass-off mechanism views for input, track, selector, and outputs.
- [ ] Render isolated views for each major production assembly.
- [ ] Render a final hero image with finished materials and lighting.
- [ ] Render an exploded/service view if assembly communication requires it.
- [ ] Update `outputs/README.md` with the Phase 2 render set and commands.
- [ ] Update the handoff document with final validation results and open items.

## Phase 2 exit criteria

- [ ] All TBD items are either resolved or explicitly approved as deferred.
- [ ] Input escapement, track, selector, and outputs form one mechanically
  plausible ball-handling system.
- [ ] Gate travel, selector stops, and interlocks are physically represented.
- [ ] Both selector routes pass independent ball-path and cross-feed tests.
- [ ] Glass, gasket, fasteners, and detailed mechanism pass clearance checks.
- [ ] Service cover, hatch, electronics, and moving parts are serviceable.
- [ ] Every production object has a stable collection and component ID.
- [ ] Materials, labels, indicators, and diagnostic visibility are review-ready.
- [ ] Phase 2 validation and review renders are reproducible from the entrypoints.
