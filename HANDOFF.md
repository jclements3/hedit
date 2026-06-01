# HANDOFF — clements47_cf harp, continue in hedit

Written 2026-06-01 (work machine). Pull this on the **home laptop**, then resume in hedit.
Remote is `origin` = `ssh://git@ssh.github.com:443/jclements3/hedit.git` (port-443 SSH endpoint,
set because plain port-22 times out on the VPN); `git pull` just works.

## Current focus
Continue the **clements47_cf** design = **erand47**, the 47-string (C1–G7) solid-body electric
**pedal harp**, **carbon-fiber frame** revision. Edit it in **hedit** (the single-file SVG editor).

> Keep two projects straight: **clements47_cf is the pedal harp** (twin curved-ladder CF frame).
> It is **NOT** the Paraguayan limaçon-body CF harp (harp.py / paraguayan_core / DP-BP-SP-WP rails).
> hedit's harp-curve JSON panel (DP/BP/SP/WP) was built for the Paraguayan one and does nothing
> useful on clements47_cf — here you edit the string `<line>`s and frame/disc geometry directly.

## Resume here
1. Serve + open hedit (localStorage/disk-save are reliable over http, flaky on file://):
   `cd ~/projects/hedit && python3 -m http.server 8000` → open `http://localhost:8000/hedit.html`.
2. **Open…** (use the picker, not drag-drop, so Ctrl+S saves back in place) → `clements47_cf_profile.svg`.
3. hedit drops the dark `#13110d` full-canvas backdrop on load (by design) — light strokes look
   low-contrast on hedit's canvas; that's display-only, not data loss.

## What's DONE this session
1. **Fixed the string lengths (the big one).** The generator had clobbered the real measured
   C1→G7 scale with `L = np.linspace(1514.93,60.61,47)` — a straight ramp wrong by up to **310 mm**,
   which rendered the soundboard as a straight-edged triangle. Restored the **real lengths from
   `strings.svg`** (the canonical harp reference: 47 `data-len` values, irregular taper) in BOTH
   the `clements47_cf.md` §2 table and the §7 generator, and regenerated `clements47_cf_profile.svg`.
   Verified per-string accurate to **0.02 mm**; still loads clean in hedit (190 objects, 47 lines).
   - **Do NOT re-linearize `L`.** If the strings ever look like a straight taper again, this bug is back.
   - `erand47_design.py` (repo root) is the standalone fixed generator, consistent with §7
     (`python3 erand47_design.py` → writes the profile SVG + prints the BOM; needs numpy).
2. **Ported the erand47 stainless session** into `erand47/` (design record `clements47.md`,
   generators, the pedal/bell-crank/linkage **bone skeleton** `erand47_bones.svg`, parts library).
3. **Traced the bellcrank reference parts** → `trace_parts.py` + `parts/bellcrank_svg/`
   (5 gold parts + 4 gray rods as fitted bezier outlines; see that folder's `_overview.svg`).

## Open / TODO
- **Tension schedule is still linear** (`TENSION_LBF = linspace(...)`) — looked intentional; only
  lengths were flagged wrong. Decide if tension should follow a real schedule too.
- **Mechanism is not yet in the CF design.** The pedal/column/bell-crank/linkage actuation lives
  in the *stainless* session (`erand47/erand47_bones.svg`, `erand47/parts.py`). Porting it onto the
  CF frame is the next big step (stainless handoff TODO #2/#3 in `erand47/HANDOFF.md`:
  re-add `build_class_bones`/`draw_bones` with per-string `PC`, then assemble the real relay).
- **Pin/axle holes** in the traced bellcrank parts are outer-silhouette only (no inner cutouts).

## File map (repo root)
- `hedit.html` — the editor.
- `clements47_cf.md` — CF design record (§2 string table, §7 runnable generator, §8 geometry).
- `clements47_cf_profile.svg` — **the working file** (open in hedit). `…_profile.png` — preview.
- `erand47_design.py` — standalone fixed CF generator.
- `strings.svg` — canonical harp string reference (the authoritative C1→G7 lengths/diameters).
- `erand47/` — ported stainless session + mechanism skeleton + `erand47/HANDOFF.md`.
- `trace_parts.py`, `parts/bellcrank*`, `parts/bellcrank_svg/` — bellcrank part tracing.
- Take-home tarball also lives at `~/Downloads/clements47_cf_hedit_session.tar.gz` (self-contained
  copy: hedit.html + the CF files + this kind of handoff), if you prefer that over `git pull`.
