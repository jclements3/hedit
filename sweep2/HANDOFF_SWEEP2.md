# HANDOFF_SWEEP2.md — the wishbone sweep, settled (read with GREEN_ORIENTATION.md)

**For every future instance, desktop and web. This is the state after the session
that ended four months of the same bug. Do not re-derive any of it from scratch;
run the code, keep the invariants, extend from here.**

---

## 0. The two invariants that caused four months of failures

1. **GREEN**: START = SOUNDBOX foot (climbs the string diagonal, reaches the
   shoulder ~(968,545) at s≈1585 of 4215). END = PILLAR foot (vertical column
   x≈203). The floor tails CROSS — each endpoint lands beside the OTHER arm's
   red foot. **Never pair anything by floor proximity.** Enforced at build time
   by `sweep2.assert_green_orientation()` — it raises if violated.
2. **BLUE**: same disease — its tails cross at the floor too. Near the pillar
   bottom the nearest blue branch is the WRONG one. Blue-field ray hits are
   selected by Viterbi continuity (3 < t < 0.98·h, smoothest branch wins), never
   nearest-hit.

## 1. Object model (JC's four-object rule; objects OVERLAP)

| object | section | spans | source |
|---|---|---|---|
| **BASE** | hollow: outer = `red_outer`, inner = `blue_outer` of base.svg — the whole union outlines, unsplit, no green | z=0 → z=69.2 (the green self-intersection on v14, computed at build) | base.svg only |
| **SOUNDBOX arm** | full c=2 limaçon (fitted to the visible arc of red_outer), variable-bore inner | floor → shoulder | formula + base.svg mouth |
| **PILLAR arm** | full 12-flute rose + **cylinder bore Ø 60.9 constant** | floor → crown | formula + base.svg mouth |
| **NECK** | U-beam, blue-driven arch | shoulder ↔ crown | formula |

- The floor mouths are the **two SEPARATE complete shapes** (boolean join, NOT
  seam-cut lobes): full rose (center (54.48,60.05) R=47.07, all 12 flutes) and
  full limaçon (pole (138.45,60.08) b=23.95, dimple toward the reunion), fitted
  to red_outer's visible arcs (rms 0.5/1.2 mm). They overlap 1356 mm²; their
  union = red_outer to 0.8 mm mean. Inner: bore circle R=30.46 (concentric to
  0.09 mm) ∪ inner limaçon (pole (126.24,60.06) b=12.90), union = blue_outer to
  0.34 mm.
- Rose lobe is pinned EXACTLY under the pillar column axis (west, ring centroid
  x≈166); limaçon lands east under the soundbox body. Rigid transform only —
  the authored footprint is NEVER scaled, stretched, or seam-cut.
- Everything is FLAT ON THE FLOOR: base mouth, both arm mouths, all at z=0.00;
  global min z = 0.00. The base shell overlaps the arms below the crossing.

## 2. The sweep (sweep2.py — the working build; legacy `_frame_rings` is dead)

Pipeline, in order:
1. **Trim** green (and blue) tails below z=130 — the crossed tail-space is never
   swept.
2. **Fields**: h and c ray-cast on tilt-limited frames; validity-filtered
   (misses, grazing spikes) and rebuilt as smooth interpolants. Blue via Viterbi
   branch selection (§0.2).
3. **Frames**: gaussian-smoothed tangents; plane rotation capped at
   0.7·step/reach with a cap-field consistency loop → **zero plane collisions**
   anywhere (the old shoulder/neck/crown fans are gone by construction).
4. **g is blue-driven everywhere**: soundbox dimple, morph window, U arch+legs
   (g = clip(2c/h, …)) — the CODE_VERIFIED NEEDS-FIX, applied.
5. **Rose**: material-ordered vertices (helix phase-lock, aligned once at the
   crown, no per-station apex re-roll). Bore = constant cylinder (P["BORE_D"]
   = 2·R of the authored base circle).
6. **Launches** (NL=8 per arm, from each authored mouth):
   - angle-locked correspondence (vertex angles morph uniform → F's own) —
     **0.0° swirl**, exact landing on the sweep's first ring;
   - underside schedule: min-z ramps 0 → F's floor monotonically — **no hump**,
     soundbox underside is 0.00 for the whole launch;
   - rose mouth phase-rotated (12-fold, shape-preserving) to the column's flute
     phase — flutes stay crisp through the rise.
7. **Soundbox ease**: 30-station lateral drift absorbs the footprint offset;
   the pillar gets ZERO easing (column straight to 0.4 mm).
8. **Transitions**: bore continuity pass (cyclic alignment outside the rose, one
   constant roll for the rose block); shoulder blue = smoothed SHAPES with the
   PATH pulled onto a straight chord (sin-weighted, shape-preserving — never
   lerp whole rings, that shears); wall clamp ≥4.4 mm (plane-projected onto
   outer.buffer(−w)); crown bore blends buffer→cylinder with the outer's
   smoothstep; zone fairing on both surfaces + one gentle global pass. Mouths
   and rose flutes are excluded from all smoothing.

## 3. Authored anchors (JC's current spec — coordinates, not station numbers)

```json
{"sh_in":{"x":965.2,"y":525.3},"sh_out":{"x":955.5,"y":520.8},
 "cr_in":{"x":348.1,"y":293.4},"cr_out":{"x":203.1,"y":395.2}}
```
→ shoulder morph st67–68 (tight, past the L-corner apex), crown smoothstep
st102–110, rose from st111 (S=176: 8 launch + 160 trimmed + 8 launch). New
anchors come from **morph_picker.html** (drag the four dots, copy spec).

## 4. Verified numbers (this build)

- 176 stations × 90 pts; bores 176/176; 0 plane collisions; 0 lane index-snaps
  outside the rose helix; launch swirl 0.0°.
- Flat floor: min z 0.00 everywhere; underside monotone both arms.
- Pillar: straight to 0.4 mm; bore cylinder Ø60.9 mouth→crown.
- Shoulder blue: chord max dev 23 mm / 223 mm run; wall 4.4–12.7 mm, EXCEPT
  **st68 = 3.1 mm** (geometric ceiling: PLATE_OUT 35.3 minus bore; see §6).
- Crown bore worst step 58 mm (was 223); outer worst 80 (was 285).
- Lane kinks: outer 121°→69°, bore 148°→57° (medians 52°/35°).
- Union(arm mouths) vs base mouth: 3.7% XOR = JC's authored petal↔limaçon
  smoothing on the union (the raw formula shapes correctly lack it).

## 5. Files (outputs / project store)

- `sweep2.py` — THE build. `wishbone(svg, base_svg, anchors=…)` →
  (rings, bores, (base_o, base_i), meta). Guard runs first.
- `lanes.html` — animated isometric, lanes-only (NO ring hoops ever — JC
  rejected ring-stack displays explicitly). Ortho buttons top/side/rear/bottom,
  bore + base objects, convoy palette, white apex lane, plies.
- `morph_picker.html` — drag the four transition anchors on the spine.
- `floor_check.html` — bottom-view proof of the mouths vs base.svg.
- `snapshot.html` — static side/rear/bottom panels.
- `GREEN_ORIENTATION.md` — invariant §0.1 in full.

## 6. Open items (decide, don't re-litigate)

1. **st68 wall 3.1 mm**: the only sub-4.4 station, bounded by PLATE_OUT=35.3
   mid-morph. Options: local PLATE_OUT bump over st66–70, or shrink the bore
   there, or accept. JC to rule.
2. **Frame v14 pillar Ø68 vs base.svg rose Ø94**: the column outer tapers per
   the frame while the floor is authored wider; the launch bridges it. If the
   column should carry base proportions up, red near the pillar needs
   re-authoring (the red at x=135 mid-column vs x≈80 at the floor).
3. **The DTW lane-first sweep** (convoy doctrine in 3D — red↔green
   correspondence driving the surface directly, no section stacking) remains
   the deeper unbuilt alternative if section-sweep artifacts ever resurface.
4. Wall minimum 4.4 mm is a placeholder pending the layup schedule.

## 7. Rules for future sessions (the ones that were repeatedly broken)

- Run `assert_green_orientation()` before believing anything about the arms.
- Never floor-proximity pairing; never seam-cut the base lobes; never scale the
  authored footprint; never draw ring hoops in the lane viewers; never smooth
  the mouths or the rose flutes; never re-derive the merge height — compute the
  green crossing from the frame at build time.
- Anchors are coordinates from the picker, not station numbers.
- Render to /tmp and verify (Playwright headless + numeric checks) before
  presenting — and if the image viewer fails, SAY SO and verify numerically;
  do not claim visual confirmation that didn't happen.
