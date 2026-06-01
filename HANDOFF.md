# HANDOFF — clements47_cf (carbon-fiber) harp, continue in hedit

Written 2026-06-01 (work machine, unattended session). Pull on the **home laptop**, then resume in
hedit. Remote `origin` = `ssh://git@ssh.github.com:443/jclements3/hedit.git` (port-443 SSH endpoint
for the VPN); `git pull` just works.

## Current focus — CF version
**clements47_cf** = **erand47**, the 47-string (C1–G7) solid-body electric **pedal harp**, with a
**carbon-fiber frame** (UD-dominant CF/epoxy, E≈135 GPa). You want the **CF version, not stainless.**
Edit it in **hedit**.

> Two projects, don't conflate: clements47_cf is the **pedal harp**, NOT the Paraguayan limaçon-body
> CF harp (harp.py / DP-BP-SP-WP rails). hedit's harp-curve JSON panel is for the Paraguayan one.

## Resume here
1. `cd ~/projects/hedit && python3 -m http.server 8000` → open `http://localhost:8000/hedit.html`.
2. **Open…** (picker, not drag-drop, so Ctrl+S saves in place) → `clements47_cf_profile.svg`.
3. hedit drops the dark backdrop on load (by design) — light strokes look low-contrast; display-only.

## String lengths — SETTLED (read this; it went back and forth)
**Authoritative source = the ORIGINAL Érard scale = `strings.svg`.** "erand47" is named after Érard.
The real 47-string scale is at **harpcanada.com/harpmaking/erard.htm** (lengths in inches; ×25.4 → mm)
and is **identical to `strings.svg`** (verified to 0.0 mm): monotonic **C1 = 1514.9 … G7 = 60.6 mm**,
shortest two **F7 = 70.7, G7 = 60.6**.

**Three corrupt sources — never use for lengths:**
1. `np.linspace(1514.93, 60.61, 47)` — a straight ramp (the original bug).
2. the **"erand47 archive"** array `[1514.93, 1448.69, …, 15.59, 60.61]` from `files (6).zip` — its
   treble is garbage (15–45 mm stub strings; F7/G7 scrambled), off by up to **279 mm**.
3. `erand47_profile_v2.svg` — generated from that bad archive, so equally wrong (it has a 7.8 mm string).

History (so it isn't repeated): I first fixed it with strings.svg (correct), then wrongly switched to
the archive when `files (6).zip` was called "latest", briefly set F7=75 — then the Érard page proved
strings.svg right. **Now fixed back to the Érard/strings.svg scale** in `clements47_cf.md` §2 + §7,
`erand47_design.py`, and the hedit loader. Profile regenerated (clean monotonic taper, no treble hook).

## Other work this session
- **hedit #1 Strings card → "Load erand47 strings"** (`loadErand47Strings`): lays down the 47 Érard
  strings (C1..G7, monotonic), vertical and air-gap spaced on the x=0 axis, tagged with the harp
  data-* schema. Replaces existing strings, preserves other content. *Pose note:* these are the bare
  step-1 strings (flat-topped, vertical) — rake (7°) and the neck-curve top come from the later
  pipeline steps (align / curves / transform), not from this button.
- **§4 structural analysis (CF) reduced** to the solver-independent core (loads 6655 N / 811 N shear;
  E-ratio re-size 193/135 → bar height ×1.127, ends 18.8 / peak 91.4 mm; trivial stress; honest
  "FE solver not in repo" caveat). BOM ≈ 2.5 kg bare / 4.9 kg rigged.
- **Hi-res bellcrank parts** (`files (8).zip`) traced → `parts/bellcrank_svg/arm_top_left.svg`,
  `yoke_mid_left.svg`, `arm_bottom_left.svg` (sources in `parts/bellcrank_hires/`).

## OPEN ITEMS
- **Diameters** differ across sources: the generator `DIA` (C1≈1.676 mm) ≠ `strings.svg` data-dia
  (C1≈0.508) ≠ the Érard page gauges (c1 = 0.091″ = 2.31 mm). Lengths are now settled; **diameters are
  not** — tell me which gauge set is real and I'll align them (they affect spacing + stroke width).
- `erand47/clements47.md` and `erand47/erand47_profile_v2.svg` are still the **corrupt-archive**
  stainless versions — left as-is (reference only); regenerate from the Érard scale if you want them.

## Other open / TODO
- **Tension** is still a linear schedule (`TENSION_LBF = linspace(...)`) — looked intentional; confirm.
- **Mechanism not yet in the CF design** — the pedal/bell-crank/linkage actuation lives in the
  stainless session (`erand47/erand47_bones.svg`, `erand47/parts.py`); porting it onto the CF frame
  is the next big step (see `erand47/HANDOFF.md` TODO #2/#3).

## File map (repo root)
- `hedit.html` — editor.  `clements47_cf_profile.svg` — **the CF working file** (open in hedit).
- `clements47_cf.md` — CF design record (§2 archive table, §4 reduced structural, §7 generator).
- `erand47_design.py` — standalone CF generator (numpy; `python3 erand47_design.py` → SVG + BOM).
- `strings.svg` — the *Paraguayan* harp reference. **NOT the source for clements47 lengths** (that was the bug).
- `erand47/` — stainless reference + mechanism skeleton (`clements47.md`, `erand47_profile_v2.svg`, bones, parts).
- Take-home tarball `~/Downloads/clements47_cf_hedit_session.tar.gz` (may be stale — `git pull` is canonical).
