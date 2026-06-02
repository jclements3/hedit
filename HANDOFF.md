# HANDOFF — clements47_cf (carbon-fiber pedal harp), continue in hedit

Written 2026-06-01 (work machine). Pull on the **home laptop**, read this, resume.
Remote `origin` = `ssh://git@ssh.github.com:443/jclements3/hedit.git` (port-443 SSH for the VPN);
`git pull` just works. Latest commit at handoff: see `git log -1`.

## What this is
**clements47_cf** = **erand47**, a 47-string (C1–G7) solid-body electric **pedal harp**, **carbon-fiber
frame**. Two tracks, both live here:
1. **hedit** (`hedit.html`) — the single-file SVG editor, now a harp *builder* (the interactive track).
2. **`erand47_design.py`** — the parametric *generator* (the canonical 2-D profile + load analysis).

> NOT the Paraguayan limaçon-body harp. hedit's DP/BP/SP/WP JSON panel is for that one; ignore it here.

## The build pipeline in hedit (run top-to-bottom)
Serve + open: `cd ~/projects/hedit && python3 -m http.server 8000` → `http://localhost:8000/hedit.html`.
Open `clements47cf.svg` via the **Open…** picker (so Ctrl+S saves in place).

1. **Step 1 → "Load erand47 strings"** — 47 strings, **real Érard scale** (C1=1514.9 … G7=60.6 mm),
   colorized **C=red / F=blue / others dark gray**, diameters mm, **tension in Newtons** (C1=234 N).
2. **Step 2 → "Apply parallel air-gap"** THEN **"Rake →pillar"** (default 7°). **Order matters:**
   air-gap makes strings vertical, so rake must come *after* (rake is a rigid rotation → air gap
   preserved exactly). Rake-then-air-gap *un-rakes* them.
3. **Step 5 → Fit curves** — fit **tops** then **bottoms** (Max nodes now defaults to **9**; keep
   9–12 — 5 under-fits the treble flick by ~22 mm and ruins the ladder). Optional **"Bottoms ↓
   curve"** rests string ends exactly on the curve (zero gap) if you want a perfect ladder match.
4. **Step 5b → Add pillar + Add shoulder** (Lamé side curves).
5. **Step 5c → Fit ladder frame** — builds the CF ladder: outer **NT-RO-EB-PO** / inner
   **NB-RI-ET-PI** as one smooth C2 spline each (centreline-offset, deloop'd; spread = bar height
   18.8→91.4 mm), neck/eyelet rungs + pillar (8) / shoulder (3) support rungs. Tune width via 5b bows.
6. **Step 4 → "Add guitar tuners (neck top)"** — Ø15.4 gear-posts ON TOP of the neck rail (outer
   edge), odd=front plate (orange) / even=back plate (blue), two-row parity offset (clears 13 mm pitch).

## Generator (`erand47_design.py`) — the lower-ladder split (clements47_cf.md §5b)
The lower CF ladder was converted from string **termination** to a load-bearing **anchor**, so a
**wooden sound chamber** can be fitted: CF carries the full tension, wood carries only a small
perpendicular down-bearing.
- **Wooden eyelet curve = old `sb`, unchanged** → speaking length / pitch / tension UNCHANGED (0.0000 mm).
- **CF anchor curve**: strings pass through the wooden eyelets and knot on the CF a `L_TAIL=30 mm`
  dead-tail down, kicked `|d|=6.24 mm` at `BREAK_ANGLE_DEG=12°` toward **−y (opposite the +y wooden
  chamber)** so the CF ladder **clears the chamber cavity**. Lower CF bar relocated ~29 mm back.
- **Loads:** CF frame **6655 N** axial; wood **1391 N** (~21%) down-bearing; F_db C1 49.0 … G7 10.2 N.
- Helpers `break_angle/down_bearing/anchor_offset/place_cf_anchors` (per-string → β taperable).
- Tapered wooden chamber (95→18 mm, soundhole) + CF backing rib. Render: PROFILE + DEPTH/ISO →
  `clements47_cf_anchor.svg`. Run: `python3 erand47_design.py` (numpy only).

## Rung sizing (CF rod + brass wear sleeve, sleeve = non-structural)
- **Neck rung 4 mm** CF (was 3 mm — marginal at a 90° wrap; 4 mm holds FoS≥3).
- **Soundboard/eyelet rung 8 mm** drilled to string Ø (brass eyelet bore), FoS 7–12.
- Pillar/shoulder support rungs 8 mm. Governing limit = the rung↔rail ILSS bond, not the rod.

## Data provenance (do not regress)
- **String lengths = the original Érard scale = `strings.svg`** (harpcanada.com/harpmaking/erard.htm,
  inches×25.4). **NEVER** the "erand47 archive" array (1448.69, 15.59…) or `np.linspace` — both corrupt.
- Tension: linear 52.69→10.98 lbf → ×4.4482 = N. Diameters: generator `DIA` set (NOT yet the Érard gauges).

## Open / TODO
- **Re-solve bar heights** for the relocated anchor load (currently hardcoded; FE solver not in repo).
- **Taper β at the bass** (e.g. 8–9° at C1–B1) to drop bass wood load below ~40 N.
- **Diameters**: switch string `DIA` to the real Érard inch gauges if you want the eyelet bores exact.
- Optional: fold the anchor/chamber into the hedit ladder; one-click "Build harp" macro.

## File map
- `hedit.html` — editor/builder. `clements47cf.svg` — your hedit working file (Open this).
- `erand47_design.py` — generator. `clements47_cf_anchor.svg` — its PROFILE+DEPTH render.
- `clements47_cf.md` — design record (§5b = the anchor/chamber split + load summary).
- `strings.svg` — the Érard string scale (authoritative lengths). `tuner/` — Thingiverse-6099101
  tuner reference (CC-BY-NC). `erand47/` — older stainless session reference.
