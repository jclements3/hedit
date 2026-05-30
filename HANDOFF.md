# HANDOFF — harp part tracing + hedit image/resize upgrade

Written 2026-05-30 by the work laptop's Claude. Read this first, then test in the
browser. Everything below is committed and pushed to `origin/main`
(`ssh://git@ssh.github.com:443/waveform-jc/hedit.git` — note the **port-443 SSH
endpoint**, set because plain port-22 SSH times out on the VPN; `git pull` just works).

## Goal
Trace the **gold** and **gray** part outlines out of the CAD frames in `images/`,
then use hedit to lay each part's photo in the **background** and tweak the
**outline shapes** (select / resize / node-edit) on top, saving clean part SVGs.

## What's DONE
1. **Repo synced** to the home-laptop version (was 4 commits behind; fast-forwarded).
2. **Tracer** `images/trace_parts.py` — pure Python (Pillow + numpy, no potrace).
   Color-keys gold or gray, cleans the mask, contour-traces, RDP-simplifies,
   writes `<stem>.traced.svg` + a debug mask PNG. Tunables: `--only gold|gray`,
   `--eps`, `--min-area`, `--close`, `--open`, color thresholds.
   Run: `python3 trace_parts.py harp_0011.png --only gold --min-area 80 --eps 1.2`
3. **17 part sprites traced** → `images/harp_XXXX.traced.svg`:
   - GOLD parts (gold-keyed, clean): 0007 0009 0011 0015 0021 0023 0027 0030
     0032 0043 1219 1373
   - SILVER/GRAY parts (re-traced with `--only gray`): 0057 0061 0063 0079
   - `harp_0080` is a *string-layout render*, not a part — its trace is just the
     brass pin fittings. Ignore/delete it.
4. **hedit.html upgraded** (+188 lines, all in one block appended after `loadSample`):
   - **Background reference image**: header **"Image…"** button → loads a photo as
     a dimmed `<image>` in a new `#bg` layer behind the content, fits the view to
     it. **opacity slider** + **"Clear img"** button. The `#bg` layer is OUTSIDE
     `contentGroup`, so **Save never includes it**. Persists across reload via its
     own localStorage keys (`hedit:bg:url` / `hedit:bg:wh`), never in the part file.
   - **Select + resize**: the Select tool (V) now draws **8 white resize handles**
     around the selection bbox. Drag to scale any shape (rect/ellipse/circle/line/
     path) about the opposite anchor; **Shift = proportional**. Move + node-edit (N)
     unchanged.
   - **"Import…"** button: loads an SVG and APPENDS its shapes on top of the current
     document (doesn't wipe content or bg; skips the tracer's dark backdrop rect and
     `<metadata>/<defs>`). Use it to drop a `*.traced.svg` outline onto its photo.
   - Open/Save of standard-shape SVGs already round-trips.

### New code (search hedit.html for these)
`bgGroup` (decl + created in `buildLayers`), `setBgFromDataURL`, `setBgOpacity`,
`clearBg`, `restoreBg` (called from `buildLayers`), `loadRefImage`,
`importSVGFile`/`importSVGText`, `selBBoxUser`, `rzHandles`, `drawResizeHandles`
(called in `renderOverlay`), `startResize` (called in `onDown`), `resizeMove`
(called in `onMove`), and the `addRefImageUI` IIFE that injects the toolbar
buttons next to `#btn-dxf`. Resize finalize is the existing `onUp` (drag=null).

## What I VERIFIED
- `node --check` on the extracted script → **SYNTAX_OK**.
- `./test-hedit.sh` (headless Chrome, real `loadSVGText`) → **TEST_OK**, boots clean.
- Saved-SVG path builds from `contentGroup` only (bg image cannot leak into a save).

## What I could NOT verify — DO THIS AT HOME
The work-laptop environment was unstable (dropped/corrupted tool output), so I did
**no interactive click-testing**. Please smoke-test the real workflow:
1. Open `hedit.html` (or `python3 -m http.server` then load it — localStorage is more
   reliable over http than file://).
2. **Image…** → pick `images/harp_0011.png`. Confirm it appears dimmed in the
   background and the view fits it. Try the opacity slider + **Clear img**.
3. **Import…** → `images/harp_0011.traced.svg`. The outline should drop on top.
4. **V** (Select) → click a shape → drag the white corner/edge handles to resize
   (Shift for proportional); drag the body to move. **N** → tweak bezier nodes.
5. **Ctrl+S** → save. Re-open the saved file and confirm the shapes round-trip and
   the background image is NOT in it.
6. Run `./test-hedit.sh` to confirm the headless smoke test still passes.

## Known gaps / next steps (optional)
- **Pin/axle holes**: tracer emits only the OUTER silhouette; bolt/axle circles are
  not cut as inner holes. Add an inner-contour pass to `trace_parts.py` if wanted.
- **DXF export** of corrected outlines: hedit has a DXF button; not verified on these
  parts.
- **Only the 17 clean sprites are traced.** The ~1440 full Fusion screenshots in
  `images/` are cluttered (UI chrome, multiple parts) — not worth tracing without
  cropping first.
- Debug masks (`*.gold.png` / `*.gray.png`) are git-ignored (see `.gitignore`); they
  regenerate on each tracer run.

## File map
- `hedit.html` — the editor (the upgrade).
- `images/trace_parts.py` — the tracer.
- `images/harp_*.traced.svg` — the 17 traced part outlines (the deliverable).
- `images/harp_*.png` — clean part sprites (good trace/background targets).
- `images/harp_*.jpg` — full source frames (~1440; reference only).
