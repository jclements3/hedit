# hedit — Harp design plan (curves → SVG/DXF/JSON → 3-D body + CF braiding)

hedit authors the curves; downstream (`paraguayan_core` today, optionally Maker.js/JS later)
turns the exported JSON into the 3-D body and the carbon-fiber strand braiding. This doc
organizes the **paraguayan pipeline steps** and the **Maker.js capabilities**, then maps
them to hedit features and the UI.

## 1. The harp pipeline (from `../paraguayan/harp.py`)

Side-view convention: x = toward player, z = up, mm. The instrument reduces to three control
curves + one section shape: **DP** (inner/dimple rail), **BP** (outer/bulge rail), **WP**
(width-scale path), and a convex-limaçon ("lemicon") cross-section. DP/BP/SP are *outputs* of
steps 1–12 (they recompute from the string table + a few frozen hand-edits), then become the
editable curves.

| Step | Purpose | Consumes | Produces | Key knobs (defaults) |
|---|---|---|---|---|
| 1 Strings | frozen 49-row string spec (master input) | — | `STRINGS` (47+2) | the table |
| 2 Spacing | x of each string by constant air gap (surface-to-surface) | STRINGS, AIR_GAP | `centers` | `AIR_GAP`=13 |
| 3 Neck+dots | neck arc, flat tips, eyelets, sensor dots | centers, lengths | arc_z, flats, eyelets, naturals/sharps/midis | `NECK_DEG`=7, `HANG`=13, `MIDI_F`=.125, `NAT_F`=.9439, `SHARP_F`=.8909, `NECK_TOP_MODE`=smooth |
| 4 Soundboard | eyelet/seat curve the strings sit on | centers, eyelets, OPT_EYELET_BEZIER | `segs` (4 cubics) | frozen `OPT_EYELET_BEZIER` |
| 5 Belly | front underside curve | eyelets, midis | `belly_q` | `MIDI_CLEAR`=13, `N1_LEFT`, `N1_FRAC`, `N3_DROP`, `BELLY_HANDLE_OFFSETS` |
| 7 Rear shoulder | treble cap arcs SB↔belly, SA↔front | segs, belly_q, apex | rear-shoulder cubics | `REAR_SHOULDER_SAG`=26, `_HANDLE`=20 |
| 8 / 8s Column | front edge + structurally-sized CF column | belly_q, tension | column_edges, `column_section()` | `FRONT_SHOULDER_HANDLE`=140, `CF_E`, `CF_SIGMA_ALLOW`, `COLUMN_*` |
| 9 Sound chamber | SA back-bulge depth law + apex (B locus) | eyelets, segs, tension/freq | sc_depths, sc_apex_fitted | `SC_A_BASS`=330, `SC_FREQ_EXP`=1/3, `SA_B0A_SHIFT`=40 |
| 9/10 Holes | graduated round sound holes on SA | SA curve, depths | hole centers + lens profiles | `SC_N_HOLES`=6, `SC_HOLE_FRAC`=.42, `SC_HOLE_MIN/MAX`, `SC_HOLE_FORESHORTEN` |
| 11 Base arc | foot arc at b0a | eyelets, segs | base-arc params | `BASE_END_DEG`=173 |
| 12 Rails | assemble DP (dimple) + BP (bulge) point paths | the above landmarks | dimple_path, bulge_path | `DP_BP_SAMPLES`=24 |
| 12c Rails→Bézier | extract each rail as a cubic-Bézier chain | step-12 pieces | `DP_ch`, `BP_ch` | `RAIL_FIT_MAXERR`=1 |
| 12d Handles | converged foot/neck hand-edits + handle tuning | DP_ch, BP_ch | edited DP/BP | `B6_HANDLE_DEG`=20 |
| 13 Sections | swept limaçon sections D-on-DP / B-on-SA, morph to neck ellipse | rails, neck_ellipse | lemicon stations | `SWEEP_N_SECTIONS`=11, `SWEEP_MORPH_START`=.78, `LEMICON_WR`≈1.101 |
| 13c iso-sweep | 3-curve model: DP master, BP induced, WP scales width | DP, BP, WP, m, n | iso_sweep stations, `WP(f)` | m=24, n=10, `LEMICON_WR` |
| 13 Spine | medial axis of DP/BP channel → editable Bézier `SP` | DP, BP | `SP` (~9 segs) | `SPINE_STEP`=8, `SPINE_FIT_ME`=25 |
| 14 Surface | m×n tube surface framed off spine + winding numbers | SP, DP, BP, WP | grid, ribs, depths, `winding_report` | `SURF_M`=100, `SURF_N`=10, `TOW_W`=6 |
| 15 Winding | on-surface CF strands (helix), 1 wrap per pitch | surface grid | strands (iso + ortho views) | `WIND_PITCH`=300 |

Frozen hand-edits (not pure params): `OPT_EYELET_BEZIER` (step 4) and the belly shape — these
are exactly what hedit's node+handle editor should make *easy* to author next time.

## 2. Maker.js 0.19.2 — capabilities we can use

- **Curves/primitives:** `models.BezierCurve(points[])` (points→Bézier fit; the rail/neck primitive),
  `ConnectTheDots`, `Ellipse`/`EllipticArc`, `Oval`, `Ring`, `Slot`, `Holes`, `Circle`, `Arc`, `Line`.
- **Build the body from a rail:** `model.expandPaths(centerline, dist)` (sweep to finite width),
  `model.outline(model, dist, joints, inside?)` (offset/inset, kerf comp), `model.mirror` (symmetric halves).
- **Sound holes (boolean punch):** `models.Holes`/`Circle` + `model.combineSubtraction(body, holes)`;
  verify with `measure.isPointInsideModel`.
- **Distribute along a curve:** `layout.childrenOnChain/Path` (tuning pins / anchors on a rail),
  `layout.cloneToRadial/Grid` (decorative motifs, hole rows).
- **Fillet/clean:** `chain.fillet`, `model.simplify` (after `model.originate`), `removeDeadEnds`.
- **Measure:** `measure.modelExtents` (size/center), `measure.pathLength`.
- **Export:** `exporter.toSVG`, `exporter.toDXF` (layers, `usePOLYLINE`), `exporter.toPDF`,
  `exporter.toJscadCSG`→`toJscadSTL` (extruded 3-D body), `toSVGPathData`.
- **Units:** `unitType.Millimeter`, `model.convertUnits`. Coordinate frame is Y-up (matches +X/+Z).
- **Import:** `importer.fromSVGPathData` (ingest a traced profile).
- **No built-in curve-fit/spline** — hedit ships its own Schneider fitter (kept).
- **Parametric UI hook:** `IKit.metaParameters` (range params → auto sliders) — fits a knob panel.

## 3. Mapping → hedit (have / next)

| Pipeline need | hedit today | next |
|---|---|---|
| 1 Strings | spec-table modal, import strings.svg | — |
| 2 Spacing | parallel air-gap (diameter-aware) | — |
| 3 align ends / neck | Top/Middle/Bottom, on-curve, S-axis | neck-arc knobs (NECK_DEG/HANG) |
| 4 soundboard / fit | Fit bottoms→curve (Schneider, node cap, pinned ends) | fit tops; assign as DP seed |
| 12 DP/BP rails | import/export DP/BP/SP/WP JSON (drop-in), node+handle editor | "assign path → DP/BP", derive SP (`spine_chain` port) |
| 13c WP | pass-through | WP waterfall editor (1-D f→r smoothstep) |
| 13 lemicon | — | limaçon section preview at DP nodes |
| frame | Orient +X/+Z (RH) | non-destructive Y-up display |
| export | SVG (embedded), JSON (drop-in) | **DXF** (Maker.js or small JS writer), PDF |
| 14/15 surface+winding | (downstream `paraguayan_core`) | optional JS port later |

**Division of labor (confirmed):** hedit = 2-D curve front-end → SVG/DXF/JSON; Python
`paraguayan_core` consumes JSON for spine/WP/limaçon-sweep/winding/3-D + CF braiding.

## 4. UI direction (this session)

Critique: one crowded left column mixing harp-workflow + generic editing; controls scattered
across header/left-strip/right-panel; redundant Fit; cryptic tooltip-only labels.

Redesign: **left column = the harp WORKFLOW as ordered, collapsible stages** (Strings → Spacing →
Align → Fit → Transform → Rails/Export → Arrange); **right column = Inspector** (Style, Node, View,
Help) for the selected object; header grouped (File · History · Fit/Delete) with dividers; one
clear **primary** action button per stage; clearer labels. IDs unchanged so all logic keeps working.
