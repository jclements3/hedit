# hedit/convoy -- lamination lanes for the DP/BP band

Fills the band between the harp frame's inner rail (DP, "dimple") and outer rail
(BP, "bulge") with evenly-spaced, non-crossing lamination lanes -- the plies of a
laminated frame. Uses the DTW-correspondence loft from the clements49 convoy
algorithm, adapted for hedit's **closed** rails.

Everything here is **new and self-contained**. It reads
`../../paraguayan/paraguayan_overrides.json` **read-only** and writes only into
this directory. No existing hedit file is modified.

## Run

```
/home/james.clements/anaconda3/bin/python3 selftest.py      # premises (30 checks)
/home/james.clements/anaconda3/bin/python3 lanes_dp_bp.py   # build + verify + render
```

System python3 is anaconda 3.12.2 (numpy 2.2.6, scipy 1.17.0, shapely 2.1.2 --
all verified present). hedit has no venv and does not need one. Runs in ~0.4 s.

Then **open `lanes_dp_bp.html` and look at it.** That is not a formality; see
"Acceptance" below.

| file | what |
|---|---|
| `rails_json.py` | DP/BP/SP Bezier chains -> dense polylines. Mirrors `harp.js:29` |
| `seam.py` | closed loop -> open rail, cut at the mutual-nearest pinch |
| `convoy.py` | vendored from `clements49_convoy_handoff.zip`, 2 marked adaptations |
| `lanes_dp_bp.py` | the driver: build, measure, verify, emit |
| `selftest.py` | pins every premise the driver relies on |
| `lanes_dp_bp.html` | **the deliverable a human looks at** (pan/zoom, no CDN) |
| `lanes_dp_bp.json` | sidecar: lanes + full acceptance evidence + ladder |
| `ladder.txt` | the run log |

## What it measured (real numbers, this machine, 2026-07-16)

Rails, straight from the JSON:

```
DP: 577 samples  closure gap 0.000000  area -400737.2 (CW)   9 nodes
BP: 641 samples  closure gap 0.000000  area -878498.5 (CW)  10 nodes
SP: 577 samples  closure gap 0.000000  area -626649.0 (CW)   9 nodes
DP.within(BP): True        (and DP < SP < BP strictly)
seam: DP[256]=(654.84,119.41)  BP[320]=(661.62,148.58)  gap = 29.953 mm
```

The ladder (J8: measured, not assumed):

```
iter 1:  1 lanes  0 crossings  pinch   nan  turn 16.10  seam 1.24  HF 0.0592  nesting PASS
iter 2:  3 lanes  0 crossings  pinch  7.49  turn 22.16  seam 2.63  HF 0.0721  nesting PASS
iter 3:  7 lanes  0 crossings  pinch  3.74  turn 27.09  seam 3.99  HF 0.0791  nesting PASS
iter 4: 15 lanes  0 crossings  pinch  1.87  turn 29.50  seam 5.31  HF 0.0827  nesting PASS
iter 5: 31 lanes  0 crossings  pinch  0.94  turn 32.38  seam 6.41  HF 0.0847  nesting PASS
```

Shipped: **iteration 3, 7 lanes, 0 crossings** -- and the stronger checks below.

**0 crossings all the way to iteration 5 -- and that is a REAL difference from the
Clements frame, not a bug.** The handoff documents 0/0/0/3/19 crossings for
iterations 1-5 and calls the iter-4 breakdown a topological limit that "DTW does
not dissolve". It does not reproduce here, because that limit is a property of the
*Clements frame's green head/tail reunion at the base notch*. DP/BP have no such
reunion: they are two strictly-nested closed loops, i.e. a topological annulus.
Evenly-spaced nested loops in an annulus **cannot** cross. So the crossing count is
nearly uninformative here, which is exactly why acceptance does not rest on it.
J8 said "re-derive the ceiling, do not assume iteration 3" -- re-derived, and the
crossing ceiling is gone. **The real ceiling is the pinch**, below.

## Acceptance -- and why "0 crossings" is not it

`CONVOY_ALGORITHM.md` 5: *0 crossings is necessary, NOT sufficient.* Worse,
`count_crossings` uses shapely `.crosses()`, which is **False for touching /
collinear-overlapping lines** -- two *tangent* lanes score 0. And a lane that
escaped the band entirely still scores 0 against its siblings. Here the annulus
argument above makes 0 nearly free. So the shipped build is verified four ways:

1. **Strict nesting chain** (the real test -- subsumes crossings, tangency and
   containment): `BP > lane1 > ... > lane7 > DP`, every link `within=True`,
   `touches=False`. Min separations 3.631 / 3.739 / 3.738 / 3.738 / 3.737 /
   3.735 / 3.733 / 3.384 mm. **PASS.** No two lanes intersect at all.
2. **Every lane closed**: max seam gap `0.00e+00` mm. Max seam turn 3.99 deg.
3. **No spacing collapse** (the failure mode a harmonic field hides behind a
   0 count): lane spacing equals band-width/8 to **2.8e-13 mm**, and min
   distance-to-DP scales linearly with `1-f` -- 26.14, 22.39, 18.65, 14.90,
   11.14, 7.27, 3.38 mm. Even 3.74 mm steps. Nothing hugs a rail.
4. **Rendered and looked at**, headless via
   `google-chrome --headless=new --screenshot`. 7 lanes nest cleanly between the
   rails and converge only at the pinch. The lanes *appear* bunched at the crown;
   that is real (band width there is genuinely narrow -- band width ranges
   29.95 / p10 59.13 / median 129.54 / max 283.43 mm), not a correspondence fault.
   Per lesson 2 of the 3-D convoy work, apparent crowding was checked against the
   data before being "fixed" -- there was nothing to fix.

## The pinch is the real limit (structural, read this before raising the lane count)

The band pinches to **29.95 mm**. Lanes divide it evenly, so iteration `n` gives a
pinch gap of `29.95 / 2**n`: 7.49 / **3.74** / 1.87 / 0.94 mm at iters 2-5. The
shipped 7 lanes leave **3.74 mm** between plies at the pinch, which is **below
HARP_PLAN's `TOW_W = 6`**. So iteration 3 is already past the tow-width budget at
the pinch, even though it is geometrically clean. **This is a design decision for a
human, not a bug**: either accept sub-tow spacing locally at the pinch, allow
non-uniform spacing through it, or merge inner plies before it. Nothing here
decides that. Iteration 3 ships because it is the documented canonical figure and
it is geometrically sound; it is *not* endorsed as manufacturable at the pinch.

Lane count is dyadic (`2**n - 1` lanes at `f = k/2**n`) -- you cannot ask for 5.
For a non-dyadic count call `convoy.loft(Rs, Gp, f)` directly at chosen `f`.

## Judgement calls

**J1 -- New directory, not a change to `harp.js`.** `harp.svg`/`harp.dxf` are
terminal artifacts with no grep-findable consumer, so emitting lanes there would be
write-only, and it would collide with the parallel `svgHeight()` work on the same
file. Lanes are pure-new Python with their own render and their own sidecar.

**J2 -- The closed-loop problem is solved by a mutual-nearest-pair seam at the
pinch.** This is the central call. `convoy` wants **open** rails and anchors
`red[0]<->green[0]`, `red[-1]<->green[-1]` (`convoy.py` `dtw_map`). DP/BP are
closed. Cutting them anywhere arbitrary makes that anchoring actively *wrong* --
it force-pairs two points with no reason to correspond. So both rails are cut at
the **mutually-nearest DP/BP sample pair** (the 29.95 mm pinch), rolled so the cut
is index 0, with the cut sample duplicated at index -1. Two properties earn this:

* it is **derived from the geometry, not hand-frozen** -- HARP_PLAN.md warns DP/BP
  are *outputs* of `paraguayan/harp.py`, so a hardcoded index would rot on the next
  regen; a mutual-nearest search re-derives itself;
* nearest-point projection makes the two cuts **correspond by construction**, so
  the endpoint anchoring now pins the seam to the seam. It is **correct here, not
  vestigial**.

Consequence: every lane is itself a closed loop nesting between DP and BP -- which
is what a lamination in a closed frame physically *is*. `CONVOY_ALGORITHM.md`
8.3's "closed->open topology change at the cusp" worry is **defused, not worked
around**. It also handed us the nesting-chain acceptance test, which is far
stronger than anything available on the open Clements frame.

**J3 -- `co_orient()` is a CHECK, not the production path.** Both rails measure CW
(shoelace negative), so no reversal is needed and `co_orient`'s 2 extra DTW solves
are waste. But the claim is *verified, not asserted*: the driver runs `co_orient`
once and **asserts it returns green un-reversed** (it does), then bypasses it. If
that assert ever fires, the driver stops rather than shipping lanes built on a
premise the code denies.

**J4 -- vendored `convoy.py` adapted; `core.py` deliberately NOT pulled in.**
`CONVOY_ALGORITHM.md` 7 calls `core._flatten` the "canonical parser; handles
relative/V/H". **That is false, and it was verified false here, not taken on
faith:** `core.py:30`'s tokenizer regex is `[MmCcLlZz]` -- no H, no V -- so it eats
their operands as an `(x,y)` pair. Measured against
`/home/james.clements/Downloads/clements49_base_handoff/core.py`:

```
core._flatten("M 0,0 H 10 V 20 L 30,40")  -> 3 pts [[0,0],[10,20],[30,40]]   WRONG
_flatten_local(same)                      -> 4 pts [[0,0],[10,0],[10,20],[30,40]]
```

It loses both real points and *invents* (10,20). So the `from core import _flatten`
try/except is **deleted**; `_flatten_local` is the sole parser. The bare
`except Exception` that silently degraded to it is gone with it. (The SVG parser is
barely on our path -- we read Bezier chains from JSON -- but leaving a
known-broken import live in a fresh vendor is indefensible.) Both adaptations are
marked `VENDOR ADAPTATION` at their site; `dtw_map`, `loft`, `resample`,
`correspondence`, `build_convoy`, `count_crossings` are byte-faithful.

**J5 -- Smoothing measured, then NOT applied.** Lesson 1 from the 3-D convoy work
is that lofted lanes can carry Nyquist sawtooth (~7.3 mm there). **Measured here
first: lanes 0.079 mm HF residual vs the rails' own 0.049 mm** -- the lanes are as
clean as their sources, because they are lofts of analytic Beziers and nothing in
this path generates Nyquist content. So the trigger (3.0 mm) does not fire and
**no smoothing is applied**. `convoy.smooth_closed()` is implemented, unit-tested
(self-limiting: moves a clean circle 0.025 mm; kills sawtooth 5.00 -> 2.48 mm) and
wired to the measurement, ready if a future section generator needs it. The seam
turn (3.99 deg max) was the reason to keep it available -- `dtw_map`'s endpoint
taper disables smoothing exactly at the seam -- but 3.99 deg does not warrant it.

**J6 -- SP is drawn but unused.** The spine is reference geometry only; the lanes
are a DP/BP loft. SP is rendered dashed purple so a human can judge whether the
lanes sit sensibly relative to the medial axis.

**J7 -- Sidecar, never the source file.** `lanes_dp_bp.json` uses a top-level
`LANES` key *shape* (`hedit.html`'s `harpExtra` would round-trip such a key
untouched) but lives in a **separate file**: `paraguayan_server.py` rewrites the
overrides in place and its merge behaviour against a new top-level key is
**unverified**. Not risking someone else's authored geometry to save a file.

**Display flip.** The JSON is Y-up mm (`harp.js:13`); SVG is y-down. The render
negates y so it reads Y-up like `harp.svg` -- the harp stands on its foot. Note
`hedit.html:4378 importHarpJSON` writes JSON coords into `d` with **no** flip, so
anything eyeballed in that editor is vertically mirrored. Not copied.

## Not done / known gaps

* **Bezier refit not done.** The stretch goal (refit each lane to a node+handle
  chain via `hedit/bezierfit.py` for the overrides schema) is **not implemented**.
  The sidecar carries dense polylines (500 samples/lane), not 9-node chains. A
  consumer wanting editable chains must refit.
* **No consumer.** Nothing reads `lanes_dp_bp.json` yet. Wiring lanes into
  `harp.js` as a `harp.models.lanes` layer is a clean next step, but it must wait
  for the `svgHeight()` fix to land or the lanes would be judged against strings
  sitting 1735 mm out of position.
* **The pinch/tow-width conflict above is unresolved by design** -- it needs a
  human's call, not more code.
* **Manufacturability, ply thickness, fibre continuity, and whether a lamination
  should follow these curves at all are entirely out of scope.** This produces
  geometry that nests; it makes no engineering claim.

## Standing rules for this directory

* **0 crossings is necessary, not sufficient. Always render and look.** Here it is
  nearly free (nested closed loops in an annulus cannot cross) -- lean on the
  nesting chain, the spacing linearity, and your eyes.
* If the render *shows* a crossing the data denies, **suspect the render** (lesson
  2 of the 3-D work: unsorted 3-D polylines faked crossings that were not in the
  data). Verify apparent defects against the data before "fixing" the data.
* **Measure before smoothing.** Never smooth reflexively.
* `CONVOY_ALGORITHM.md` 8.3 is **unreliable on provenance** -- its claims that the
  3-D racetrack work "was never packaged" and "appears nowhere in the project
  files" are both false (`clements49_base_handoff.zip` packages it). 7's parser
  claim is false too (J4). Check its claims before trusting them.
* DP/BP/SP are **outputs** of `paraguayan/harp.py`. Never hardcode an index into
  them; re-derive. Run `selftest.py` after any rails regen.
