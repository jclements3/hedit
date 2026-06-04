# Harp frame sweep — model write-up

A single closed sweep builds the whole harp frame. You supply three things;
the script does the rest. The cross-section is a limaçon through the
soundchamber and a superellipse through the pillar, morphing between them at
two junctions, with the section's width governed independently in Y.

## Coordinate frame

- **XZ plane** holds the *path* — the harp's side elevation (the closed loop:
  soundboard → rear shoulder → neck → front shoulder → pillar → back to
  soundboard). This is built on another chat and handed in as input.
- **Y** is the harp's width (left/right). The cross-sections extend in ±Y.
- At each path point the section lives in the plane spanned by **Nout** (the
  outward path normal, lying in XZ) and **Y**. So `n` = depth out from the
  path (the dimple→bulge / superellipse-inner→outer direction), `y` = width.

The inner path *is* the dimple line for the limaçon runs and the inner side
for the superellipse runs — i.e. the soundboard face and the pillar's inner
face both ride directly on the supplied curve.

## The three inputs

1. **`INNER_PATH_XZ`** — the inner loop as `(x, z, region_tag)` control
   points, in loop order. A `region_tag` marks where each named region
   *starts*: `sound_chamber`, `rear_shoulder`, `neck`, `front_shoulder`,
   `pillar`. Replace the fake harp outline with the real one; nothing else
   needs to change. The script fits a **periodic** cubic spline through the
   points, so the loop closes smoothly, and reads the region boundary
   fractions straight off the tagged points' arc length.

2. **`W_KNOTS`** — the **Y half-width law** (your "minor-axis control curve"),
   as `(u, half_width)` knots with `u` ∈ [0,1) the fraction around the loop.
   Fitted as a periodic spline. This is the same editable breadth curve from
   the 2D work, now indexed by arc length instead of X. (Swap in the Bézier
   chain here if you want draggable control — the evaluation is identical.)

3. **Region transition points** — come for free from the tags in input 1.
   They drive two derived scalar fields:
   - `morph(u)` ∈ [0,1]: 0 = limaçon, 1 = superellipse. Zero through
     soundchamber/rear-shoulder/neck, ramps 0→1 across the **front shoulder**,
     1 through the **pillar**, ramps 1→0 across the **pillar foot** (`Tclose`)
     so the section is a limaçon again where the loop rejoins the soundchamber.
   - `yplus(u)` ∈ [0,1]: the +Y half-width multiplier. 1 in the soundchamber,
     ramps 1→0 across the **rear shoulder**, 0 through the **neck**
     (−Y only), ramps 0→1 across the **front shoulder**.

   Both ramps are smoothstep, so every junction is tangent-smooth.

## Section construction

Two unit rings are built once — a limaçon (a = 2b) scaled to half-breadth 1,
and a superellipse (n = 4) scaled to the same depth — and matched
point-for-point by central angle (so φ = +90° is the +Y breadth, −90° the
−Y breadth, 180° the inner/dimple point on the path, 0° the outer bulge).
At each station `u`:

```
ring  = (1−morph)·limUnit + morph·seUnit      # blend the matched rings
ring *= W(u)                                  # scale to the Y half-width
ring.y = where(ring.y > 0, ring.y · yplus(u), ring.y)   # clip +Y in the neck
world  = P(u) + ring.n · Nout(u)   (in XZ);  world.Y = ring.y
```

Because the scaling is uniform, the bulge depth tracks the width
(`depth = 1.816 · W` for the a = 2b limaçon); the superellipse uses the same
depth so the morph is seamless. Clipping +Y to zero collapses that half onto
the y = 0 plane, leaving the half-section the neck needs.

## Asymmetry, restated

- Soundchamber, shoulders, pillar: **symmetric about Y** (`yplus = 1`).
- Neck: **−Y only** (`yplus = 0`), faired in/out across the two shoulders.

## Outputs

- `harp_3d.html` — orbitable Three.js sweep; the orange line is the inner
  path (spine), a bright ring sweeps the section, drag to orbit / scroll to
  zoom.
- `harp_side.svg/.png` — XZ side elevation: inner path + outer bulge edge,
  coloured by region.
- `harp_width.svg/.png` — the Y-width development: −Y edge (full) and +Y edge
  (clipped through the neck), with region boundaries marked.

## Swapping in the real path

Replace `INNER_PATH_XZ` with the curve from the XZ chat — either as tagged
control points, or by editing `csx, csz` to evaluate the real spline/Bézier
directly. Keep the five region tags so the boundary fractions resolve, tune
`W_KNOTS` for the real width schedule, and adjust `Tclose` if the pillar-foot
morph should start earlier or later. The section logic is path-agnostic.

## Known simplification

The neck's clipped +Y half collapses to the y = 0 plane (degenerate triangles
on the cut face). For a watertight half-section, cap the y = 0 face explicitly
rather than collapsing — a small addition when you want a solid for meshing.
