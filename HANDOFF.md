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

## What I did this session (unattended)
1. **Corrected the string lengths — for real this time.** The authoritative scale is the **erand47
   archive** array (`L = np.array([1514.93, 1448.69, …])`), confirmed by your `erand47_profile_v2.svg`.
   - My *previous* "fix" had used `strings.svg` lengths (1514.9, 1489.7, …) — that's the **Paraguayan**
     harp, a different instrument, off by ~82 mm mean / 279 mm max. **That wrong version was committed
     and pushed earlier; this commit corrects it.**
   - Fixed in `clements47_cf.md` §2 table + §7 generator and standalone `erand47_design.py`.
     Regenerated `clements47_cf_profile.svg` (verified per-string to 0.011 mm vs the archive).
   - **Do NOT** re-introduce either regression: not `np.linspace(...)` (a straight ramp), not
     `strings.svg` (the wrong harp).
2. **Reduced §4 (structural analysis, CF)** to the solver-independent core: material-independent loads
   (6655 N closing / 811 N shear), the E-ratio deflection re-size (193/135 = 1.43× → bar height ×1.127,
   ends 18.8 / peak 91.4 mm), trivial stress, ILSS/lacing notes, and an honest caveat that the full
   frame-FE solver isn't in the repo (§7 hardcodes the SS profile, scaled ×1.127). Dropped the
   overstated per-item FE table. BOM updated: bare ≈ 2.56 kg, rigged ≈ 5.0 kg.
3. **Landed your latest zip** (`files (6).zip`) as the stainless reference and fixed its bug:
   `erand47/clements47.md` (replaced the still-buggy repo copy) + `erand47/erand47_profile_v2.svg`.
   Note: the zip's §2 *table* still showed the linear ramp while its generator/profile used the
   archive — I synced that table to the archive so the doc is self-consistent.

## OPEN ITEM — needs your call (data check)
The archive's treble tail is **non-monotonic and likely a typo**: F7 = **15.59 mm**, then G7 = 60.61 mm.
A 15.6 mm vibrating string is unphysical. I preserved the archive **verbatim** (didn't silently
"fix" it). The corrected profile therefore comes to a sharp treble point. Tell me the right F7 value
(it should probably continue the taper, ~75 mm) and I'll patch the archive + regenerate.

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
