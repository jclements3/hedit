# cad/ — kernel-exact downstream (OpenCascade)

hedit is the integrated studio (builder → morph → sections → analysis → ISO sheet);
its **Drawing** mode generates a native ISO 128 A3 sheet from silhouettes — fast and
live, but approximate. This directory is the *kernel* path: true B-rep solids lofted
through **OpenCascade** from the exact same spec, giving mathematically exact 2-D
vector profiles with real hidden-line removal, plus STEP for any CAD.

Input for both: the `harp_spec.json` that hedit's **Export spec** button writes
(defaults to `sweep2/harp_spec.json`). Both rebuild the sections from the spec +
`frame.svg` with the same math hedit uses (golden-tested against `sweep2/core.py`).

## replicad (JavaScript, OpenCascade WASM)

    cd cad/replicad
    npm install            # once (replicad + replicad-opencascadejs)
    node build.js [harp_spec.json] [frame.svg]

Outputs in `cad/replicad/out/`:
- `soundbox_front|left|top.svg` — kernel projections (visible solid + dashed hidden)
- `soundbox.step` — exact B-rep

Notes: node's `require(esm)` needs the CJS-global shim at the top of `build.js` for
the emscripten loader. The projections include all loft face-boundary edges; raise
`STATION_STRIDE` for fewer seams, or take the STEP into FreeCAD for silhouette-only.
`lib/` is a copy of the verified section pipeline (see `sweep2/PORT_NOTES.md`).

## build123d (Python, OCP)

    cd cad/build123d
    python3 -m pip install --user build123d     # once
    python3 harp.py [harp_spec.json] [frame.svg]

Outputs in `cad/build123d/out/`: `soundbox.step` + `soundbox_front.svg` (projected
profile with `LineType.HIDDEN` hidden lines). On miniconda, the script preloads
conda's `libexpat` to dodge an OCP symbol clash — already handled in `harp.py`.

**Certified ISO drawings**: open `out/soundbox.step` in FreeCAD → **TechDraw** →
new page from an ISO 7200 template → insert a projection group. TechDraw produces
standards-compliant hidden lines, dimensioning, and title blocks from this STEP.

## Scope / honesty

Both scripts currently loft the **soundbox arm** (the acoustically tuned piece).
The full wishbone union (base + pillar + neck + the three morphs) is blocked on the
unresolved HANDOFF §6.2 pillar taper conflict — the frame's Ø68 mid-column cannot
contain the authored Ø60.9 bore, and a loft through self-intersecting sections is
exactly what the kernel will (correctly) refuse. Rule on §6.2, then extend the loft.
