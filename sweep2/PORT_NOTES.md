# sweep2 → hedit port notes

This directory is the **Clements-49 sweep2 wishbone package** (the authoritative
Python: `sweep2.py` + `core.py`, plus the `spec_studio.html` knob editor and the
`frame.svg`/`base.svg` data). hedit folds the **soundbox-arm cross-section** half
of it into the browser as an interactive acoustic tuner (left card **3c Soundbox**
+ the **Soundbox cross-section** modal). The Python remains the source of truth for
the full 3-D build; hedit authors the section and exports the exact `harp_spec.json`
that drives it.

## What was ported (vanilla JS, in `hedit.html`, section "SOUNDBOX SWEEP")
The essential soundbox path, verified numerically against `core.py`:
- `core._flatten` (M/L/C/V/H/Z, 48 uniform steps/cubic) → `sbFlatten`
- trim z<130, arc-length resample to S, `_gauss_smooth` tangents, sign-propagated
  normals, `fh` ray-cast → `h`, `sweep2._field` (spike/validity filter) → `sbBuild`
- limaçon `_curve`, the dimple→y=0 shift, and `core._variable_bore` (the angle-graded
  "spine-and-wings" chamber wall) → `sbOuter` / `sbVariableBore`
- `assert_green_orientation` (the four-month invariant) → `sbAssertGreen`

## Verification
`ref_dump.py` emits `golden.json` from the real `core.py`; the JS port matches it to
**< 0.004 mm²** on chamber/outer/wall areas and to **2e-5 mm** on frame arc-lengths.
Regenerate after any change to the section math:

    python3 ref_dump.py > golden.json     # needs numpy, shapely, scipy

## The headline finding (why the knobs exist)
In the **as-built sweep2**, the soundbox OUTER section is a fixed `c=2` limaçon scaled
only by `b=h/4` — it does **not** depend on `g`, `c`, the fillet, or the blue curve.
The chamber's only real degrees of freedom are `h` (from the frame) and the
`_variable_bore` wall schedule, whose constants (`1.5/2.5/2.5/1.0`, angles `20/70/90`,
`fr=0.3`) are **hardcoded** in the Python. hedit promotes those hardcoded constants —
plus the outer `c` and the `b` divisor — to sliders so the section can actually be
tuned for acoustic quality, and reports chamber cross-section area, wall area, and
swept volume as the acoustic proxies. The exported `harp_spec.json` carries a new
`soundbox` block with these values.

## Structural analysis (added)
`hedit.html` section `// STRUCTURAL ANALYSIS` ports the other section families —
`core.opened` (U-beam, via `_arc`/`_opened`), `core.plate_u` (neck U-channel), the rose
(`_rext` outer + circular bore), and `base.svg`'s footprint — plus a composite polygon
section-property routine (`stSecProps`: area, first/second moments, principal I, centroid).
Verified against `golden.json` (rose/soundbox/plate_u/opened section props match `sec_props`
in `ref_dump.py` to <1e-3 rel). It computes, per piece + morph, section modulus, radius of
gyration, min wall, Euler buckling (pillar), bending stiffness EI (neck/soundbox), and bearing
FoS (base), under the string load (`data-ten` or the default Erard ΣT≈6655 N) with CF allowables.
The h-field is reliable in the soundbox; beyond it the pillar is evaluated from the **authored
Ø94 foot** and the frame-Ø68-vs-bore-Ø60.9 conflict (HANDOFF §6.2) is reported, not hidden.

`ref_dump.py`'s `sec_props` is the golden for the JS `stSecProps`.

## Not ported (3-D-only or irrelevant to the section)
Tilt-limited plane propagation, the Viterbi blue-branch selection (`c`/`g` don't move
the soundbox section), the rose/pillar/neck families, launches, base shell, and the
global fairing pass. See `HANDOFF_SWEEP2.md` and the in-code comments.
