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

## Conventions

- Vanilla JS, `"use strict"`, no frameworks or external libs — keep it that way; the single-file,
  zero-dependency form is the point.
- Create SVG nodes with `document.createElementNS(SVGNS, ...)`, never `createElement`.
- Numeric output goes through `fmt()` (rounds to 3 decimals) so serialized `d`/attributes stay clean.
- Style edits read the right-panel inputs via `defaultStyleAttrs()` / `applyStyleToSelection()`;
  `getStyle` checks inline style then attribute, and `toHex` normalizes any CSS color to `#rrggbb`.
