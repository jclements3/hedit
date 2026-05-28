# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`hedit` is a browser-based SVG bezier/path editor. The entire application — markup, CSS, and
logic — lives in a single self-contained file: **`hedit.html`**. There is no build step, no
package manager, no dependencies, and no test suite.

## Running / developing

- **Run:** open `hedit.html` in a browser (`xdg-open hedit.html`), or serve the directory
  (`python3 -m http.server`) and load it. It boots with `loadSample()` content so it's immediately
  testable.
- **Edit:** change `hedit.html` directly and reload the browser. No compilation.
- **Verify:** there are no automated tests — verification is manual in the browser. Exercise each
  tool (V/N/P/R/E), then Save and re-Open the resulting SVG to confirm a round-trip.

## Architecture

The code is one `<script>` block organized into clearly-delimited sections (search for the
`====` banner comments). The key concepts that span multiple functions:

### Two SVG layers (`buildLayers`)
The `#stage` SVG holds exactly two groups:
- **`contentGroup` (`#content`)** — the actual document. This and only this is serialized on Save.
- **`overlayGroup` (`#overlay`)** — transient editing chrome (bounding boxes, node anchors, control
  handles, marquee, pen preview). Rebuilt from scratch every `renderOverlay()`; never saved.

Keep anything visual-only out of `contentGroup`, or it will end up in the saved file.

### Path node model (the core abstraction)
Paths are edited through an intermediate model, not by string-munging the `d` attribute:
1. `parsePathD(d)` — tokenizes and resolves a path `d` string into **absolute segments**. All curve
   commands (S/Q/T/relative forms) are normalized to absolute cubic `C`; `H`/`V` become `L`.
2. `segsToSubpaths(segs)` — builds the editable model: an array of subpaths, each `{closed, closeSeg,
   nodes[]}`, where every node is `{x, y, hasIn, inX, inY, hasOut, outX, outY, seg, arc?}`. In/out
   are the cubic control handles. A trailing point coincident with the start of a closed subpath is
   collapsed into the closing segment.
3. `subToD` / `subsToD` — serialize the model back to a `d` string (cubic-or-line per segment).

When node-editing, `pathModel = {el, subs}` holds the live model. Edits mutate `subs` then call
`commitPathModel()` to write `subsToD(subs)` back to the element's `d`. Geometry helpers
(`cubicAt`, `lerp`, `nearestSegment`, `insertNodeAt`) operate on this model. Arcs (`A`) are preserved
but not subdivided.

### Coordinate spaces
Three spaces, with explicit converters — using the wrong one is the most common bug source:
- **screen px** — raw `clientX/Y`; constants `HANDLE_PX`/`CTRL_PX`/`HIT_PX` and hit tolerances are here.
- **user/content coords** — the `viewBox` space; `contentGroup` is identity. `evtUser(e)` maps a
  mouse event here.
- **element-local coords** — inside a transformed element. `toLocal(el, u)` / `toUserFromLocal(el, l)`
  convert via `el.getCTM()`. Node positions in the model are element-local.

`view = {x,y,w,h}` drives the stage `viewBox` (`applyView`); pan/zoom mutate it. `screenScale()` is
used to keep overlay handles a constant pixel size regardless of zoom.

### Tools and interaction
`tool` is one of `select | node | pen | rect | ellipse` (`setTool` + the toolbar/keyboard). Pointer
handling is centralized: `onDown`/`onMove`/`onUp` branch on `tool` and on a `drag` descriptor object
(`{type: "pan"|"move"|"marquee"|"node"|"shape"|"pen", ...}`). The pen tool keeps separate `penState`
and routes its drag through extra `mousemove`/`mouseup` listeners near the pen section.

### Undo
`pushUndo()` snapshots `contentGroup.innerHTML` (a string) onto `undoStack` (capped at 100) and
clears `redoStack`. Undo/redo swap whole-tree HTML snapshots. Call `pushUndo()` **before** mutating,
and note the `onUp` pattern that pops an unused snapshot when a move drag didn't actually move.

### Load / Save / sanitize
- `loadSVGText` parses uploaded SVG, runs `sanitizeSVG` (strips `<script>`, `on*` attributes, and
  `javascript:` hrefs — keep this when touching load), imports children into `contentGroup`, and
  derives `viewBox`/size.
- `saveSVG` builds a fresh `<svg>` from `contentGroup` children only and downloads it as a Blob.

## Domain feature: harp strings

hedit doubles as a harp string-layout tool. A "string" is a `<line>` in
`contentGroup` whose `stroke-width` equals its diameter; spec metadata lives in
`data-*` attributes (`data-num`, `data-note`, `data-len`, `data-ten`,
`data-core`, `data-wrap`, `data-cdia`, `data-wdia`, `data-dia`). The reference
document is `strings.svg`. The **Strings (harp)** panel section drives this:

- **Parallel air-gap** (`parallelAirGapStrings`) — makes every string vertical and
  re-spaces them so the *edge-to-edge* gap between adjacent strings is constant,
  accounting for each string's diameter (`effectiveStrokeWidth/2`). Writes clean
  `x1`/`x2`, baking any transform first (`bakeLineTransform`).
- **Edit specs…** (`openStringsTable` / `STRING_COLS`) — a modal table mapping each
  cell to a line attribute or derived value. Notable mappings: `dia` → `data-dia` +
  `stroke-width`; `len` → `data-len` + `y2` (`= y1 + len`); `x` → `x1` + `x2`.
  One undo entry per editing session (`markStringsDirty`).
- **Align** (`alignStrings` top/middle/bottom, `alignStringsToCurve` top/bottom) —
  **Invariant: alignment is vertical-only.** It never touches `x1`/`x2` and never
  changes a string's length, so the parallel air-gap is always preserved. Length is
  taken from `data-len` (fallback: `|y2-y1|`). Curve alignment samples a selected
  `<path>` and maps each string's chosen end to the path's y at that string's x
  (nearest-x sampling; assumes the curve is roughly monotonic in x).
- **Embedded spec** — the complete harp definition (per-string specs + measured
  layout: air gap, rotation, alignment) is serialized to a `<metadata id="hedit-harp">`
  JSON block on **Save** (`buildHarpModel`/`writeHarpMetadata`) and read on **Open**
  (`applyHarpModel`), so the SVG is fully self-contained — reloading a different harp
  is just opening a different SVG. The metadata lives *only* in saved files: it's kept
  out of `contentGroup` on load and rebuilt fresh on save (so it never duplicates and
  the content layer stays purely graphical). Layout values are *measured from geometry*
  at save time, so they survive undo/manual edits. Don't use `<script>` for this —
  `sanitizeSVG` strips it.
- **+X/+Z frame** (`orientXZ` / `transformContentCoords`) — toggles the harp into a
  right-handed CAD frame: **+X right, +Z up, Y into the page**, origin at the content
  bounding-box bottom-left, all coordinates ≥ 0. It rewrites content coordinates into
  X-Z (`X = x − minX`, `Z = maxY − y`) and puts a `matrix(1 0 0 -1 minX maxY)` flip on
  `contentGroup` so it still renders upright (appearance is preserved — verified to
  ~0.001). Persisted on save by wrapping content in `<g id="hedit-frame" data-frame=
  "RH-XZ" transform=…>` (+ `layout.frame` in the metadata) and detected/unwrapped on
  load. Because a content transform now exists, the editor's coordinate conversions are
  flip-aware: stage↔content via `toContent`/`screenVecToContent`, alignment top/bottom
  swap via `yIsFlipped`, and move/draw/pen/fit go through these. Read flip params back
  from the transform *attribute* (`frameParams`), not `getCTM` (which can fold in the
  viewport scale).
- **Fit bottoms → curve** (`fitBottomsCurve` / `fitCurveMaxNodes`) — Schneider's cubic
  Bézier fitter (ported from `bezierfit.py`) run over the string bottom ends. Capped at a
  "Fit max nodes" budget with the first/last anchors pinned to the first/last bottoms,
  drawn as a red `<path data-role="bottom-curve">` and auto-selected so **Bottoms on
  curve** can align to it immediately. The standalone `bezierfit.py` + `fit_bottoms.py`
  remain for offline/CLI use; the JS port mirrors them.
- **Select all strings** (`selectAllStrings`) — selects every `<line>` as a group.
- **S axis** (`setSAxis` / `sAxisLines`) — a faint dashed `<line data-role="s-axis">`
  drawn through the string centers along the spacing direction (perpendicular to the
  strings). It is a reference, not a string: `stringLines()` filters it out (so air-gap,
  alignment, the spec table, and the harp model all ignore it), but `rotateStrings`
  rotates it together with the strings, so it stays visible and correctly oriented after
  a rotation. It round-trips as an ordinary tagged content line.
- **Rotate group** (`rotateStrings`) — rigid rotation of all string endpoints (and the
  S axis, if present) about
  the group's bounding-box center. Because a rigid rotation preserves all distances
  and angles, the strings stay parallel and the *perpendicular* edge-to-edge air gap
  is unchanged — it turns the whole S-axis (spacing) / length-axis frame as one body.
  This is the one string op that produces non-vertical strings, so run it *after*
  air-gap/alignment (those assume upright strings).

Headless verification of all of the above is in `test-hedit.sh` (and the ad-hoc
harnesses it inspired); run it after any change to the strings logic.

## Save / Open

`serializeDoc()` builds the SVG text (embedded harp metadata, S axis, +X/+Z frame, all
included). **Open…** (`openFile`) uses `showOpenFilePicker` and keeps the returned
`fileHandle`. **Save** (`saveSVG`, Ctrl+S) writes back *in place* to that handle
(`ensureWritable` requests `readwrite` permission, needs a user gesture); with no handle
it falls back to **Save As** (`saveAs`, Ctrl+Shift+S → `showSaveFilePicker`), and on
browsers without the API (or `file://`) to a plain download (`downloadSVG`, lands in the
browser's download folder). `<input>`/drag-drop opens give no writable handle, so they
reset `fileHandle = null` (Save then behaves as Save As). `newDoc` clears it too.

## Paraguayan harp curves (DP/BP/SP/WP)

hedit's real purpose: author the four curves that drive the Paraguayan harp body —
**DP** (dimple) and **BP** (bulge) closed Bézier rails, **SP** (spine, derived), and
**WP** (waterfall profile, a 1-D `{f→r}`). It imports/exports the **exact
`paraguayan_overrides.json` schema** (`{closed, nodes:[{x,y,hin:{dx,dy},hout:{dx,dy}}]}`
per rail; `WP={nodes:[{f,r}]}`; plus `column_width`, `_comment`), so it's a drop-in
front-end for the existing Python `paraguayan_core` (spine/WP/limaçon-sweep/winding/3-D).

- `chainToPathD` / `pathToChain` convert between the rail's relative `hin/hout` handle
  deltas and hedit's absolute `pathModel` handles. DP/BP/SP become `<path data-role>`
  chains (colors: DP `#0a4fc4`, BP `#e60000`, SP `#7a1fa2`). WP + extras pass through
  unchanged (`harpWP`, `harpExtra`) so round-trip is value-exact (verified maxNodeDiff 0).
- Import/Export JSON buttons are in the left **Harp curves** panel.
- Note: Paraguayan coords are **Y-up mm**; hedit renders y-down, so an imported body looks
  vertically mirrored (editing + round-trip are unaffected). A non-destructive display
  flip is a TODO. The "lemicon" cross-section is a convex **limaçon** `r=b(2+cosθ), b=a/4`.
- Output goal: SVG (drawing) + DXF (2-D fab) + JSON (parametric truth driving the 3-D body
  and CF-strand braiding). DXF export and a WP editor are still to come.

## Views, consoles, annotations (added later)

- **3D view** (`enter3d`/`project3d`/`render3d`, `#stage3d`): orthographic 3D→2D
  projection of the content (X right, Z up, Y depth; flat elements at Y=0), rotatable —
  left-drag orbit, right/middle-drag pan, wheel zoom, Shift+left roll, double-click set
  rotation center; Front/Side/Top/Iso presets (`set3dPreset`). Two SVG gotchas it works
  around: size from the `.canvas-wrap` div (SVG `clientWidth` is flaky) and toggle via
  `removeAttribute/setAttribute("hidden")` (SVG has no `.hidden` IDL prop).
- **WP editor** (`openWpEditor`/`renderWpPlot`, `#wp-modal`): draggable f→r waterfall
  plot (cubic smoothstep `s=t²(3−2t)`); double-click adds/removes nodes. WP lives in
  `harpWP`, round-trips via Import/Export JSON, and is embedded in the autosave metadata.
- **JS console (vim)** (`openJsEditor`/`runJsConsole`): a js-vim editor whose Run
  direct-`eval`s code in hedit's scope (call `stringLines()`, `addPins()`, etc.); Ctrl+Z
  reverts.
- **Pins / sensor dots** (`addPins`/`addSensorDots`): `<circle data-role="pin">` per
  string (30° up-left, 3 air-gaps from the top); natural/sharp/midi RGB dots at the
  Paraguayan fractions (0.0561L/0.1091L/0.125L below the tip). Excluded from string ops.
- **Fit both ends + shift** (`fitEndsCurve`, `shiftCurves`): fit bottoms OR tops; shift
  the selected path/curve by an amount or by the air gap.

## Export & embedded editor

- **DXF export** (`buildDXF`/`exportDXF`, header "DXF" button): samples content
  (paths via `cubicAt`, lines/rect/ellipse/circle) into DXF LINE+CIRCLE entities,
  `$INSUNITS=4` (mm), Y-up for CAD (stored coords when in the +X/+Z frame, else flip
  y-down→y-up). Skips the s-axis guide. Verified with `ezdxf`.
- **Vim JSON editor** (`VIM_SRCDOC`/`openVimSource`, "Edit JSON (vim)" button): the
  vendored `vendor/js-vim.min.js` (MIT, itsjoesullivan/js-vim) hosted in an **iframe**
  so its document-wide key capture stays isolated from hedit's shortcuts. Loads the harp
  JSON via `vim.curDoc.text(...)`, **Apply** reads it back and `importHarpJSON`s it.

## Persistence

The working document is auto-saved to `localStorage` (`hedit:autosave:svg`/`:name`) so a
browser reload restores it instead of dropping back to the sample. `serializeDoc()` is the
shared serializer (used by both **Save** and autosave). A `MutationObserver` on
`contentGroup` (re-attached in `buildLayers`) debounce-calls `persist()` on any change;
boot does `if(!restoreAutosave()) loadSample()`; **New** calls `clearAutosave()`. All
localStorage access is wrapped in try/catch, so an opaque/blocked origin just no-ops
(falls back to the sample + manual Save/Open). Note: `file://` localStorage works in
Chrome but can be flaky — serve over `http://localhost` for reliable autosave.

## UI layout

The panels are **collapsible `<details class="sec">` cards** (CSS `.sec`/`.sec-body`, primary
action = `.btn-primary`). The **left column (`.props-left`) is the harp workflow** in pipeline
order — numbered cards: JSON file (DP/BP/SP/WP import/export) → 1 Strings → 2 Spacing → 3 Align
ends → 4 Fit curve → 5 Transform → Arrange (generic, the only non-harp card). The **right column
(`.props`) is the Inspector** for the selected object: Style / Node / View / Help. Header is
grouped (File · Undo/Redo · Fit/Delete). The far-left strip is the tool palette (V/N/P/R/E).
All control IDs are unchanged across the redesign — JS wiring keys off ids, not structure, so
moving a control between cards is safe. The harp pipeline + Maker.js capability map is in
`HARP_PLAN.md`.

## Conventions

- Vanilla JS, `"use strict"`, no frameworks or external libs — keep it that way; the single-file,
  zero-dependency form is the point.
- Create SVG nodes with `document.createElementNS(SVGNS, ...)`, never `createElement`.
- Numeric output goes through `fmt()` (rounds to 3 decimals) so serialized `d`/attributes stay clean.
- Style edits read the right-panel inputs via `defaultStyleAttrs()` / `applyStyleToSelection()`;
  `getStyle` checks inline style then attribute, and `toHex` normalizes any CSS color to `#rrggbb`.
