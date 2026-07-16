# DATUM_NOTE.md -- the svgHeight fix, and the questions it did NOT answer

Written alongside the `svgHeight()` fix in `harp.js`. Read this before trusting
`harp.svg`.

## 1. What was fixed

`harp.js` `svgHeight()` returned `vb[3]` (the viewBox *height*) and used it as the
constant `C` in the y-flip `y -> C - y` at `harp.js:58, :76, :103`.

`return vb[3]` is only correct when `min-y == 0`. Commit `f408936`
("Harp pipeline: ... c1-origin canvas, ...") re-datumed `strings.svg` from

    viewBox="0 0 667.7 1554.9"      ->   viewBox="-120 -1734.9 807.7 1864.9"

i.e. gave it a **negative origin**. From that commit on, every flipped y was off
by exactly `-minY` = **1734.9 mm**.

The fix is one line: **`return vb[1] + vb[3]`** -- reflect about the viewBox's own
frame. This is the correct generalization of the existing contract ("reflect the
SVG about its own viewBox") and is right regardless of the open questions below.

Measured effect on the 47 strings, in Maker.js Y-up mm:

| constant | strings y-range |
|---|---|
| `vb[3]` = 1864.9 (old, buggy) | y[1864.9, 3379.8] |
| `vb[1]+vb[3]` = 130.0 (fixed) | y[130.0, 1644.9] |

BP (outer rail) spans y[-71.9, 1703.3], so the old output put the **entire** string
set above the frame.

### Correction to the record

Earlier notes claimed the bug dropped the strings "~300 mm BELOW the frame."
That is **wrong in direction**. The magnitude (1734.9) is right, but in Maker.js
Y-up the strings landed **161.6 mm ABOVE** the frame top (3379.8 vs BP's 1703.3).
Anyone eyeballing a pre-fix render should look **up**, not down.

## 2. Why min-x gets NO correction

Traced, not assumed:

* `vb[0]` is read **nowhere** in `harp.js`. Grep for `vb[` returns exactly one
  hit: line 65.
* x is a **pass-through** at every site -- `loadStrings:76` pushes `x1` raw,
  `cubicPathToBeziers:58` uses `cx,x1,x2,x3` raw, `loadCircles:103` uses `cx` raw.

That asymmetry is **correct, not an oversight**: a *reflection* needs an axis
constant; a *translation-free pass-through* does not. y is reflected, x is not.

The counterfactual settles it. Applying `x - minX` (i.e. `x + 120`) would move the
strings from x[0.0, 627.7] to x[120.0, **747.7**] -- **38.6 mm past BP's outer
edge (709.1)**, i.e. outside the frame. Raw x already sits inside BP x[-99.2,
709.1] with 99.2 / 81.4 mm of margin.

**`-120` is canvas padding, not a datum error.** Do not "fix" it.

## 3. The extents figure proves nothing

`node harp.js` prints `extents: 808.4 x 1775.2 mm`. That is **BP's bounding box
alone** -- BP saturates the model bbox, so C=0, C=20 and C=130 all print exactly
this. It is not evidence for any datum. **Report the string y-range instead.**

## 4. UNRESOLVED, and bigger than a datum: strings.svg is a DIFFERENT INSTRUMENT

The fix places the strings inside the frame's *bounding box* -- all four bbox
checks pass:

    strings  x[   0.0,  627.7]  y[  130.0, 1644.9]
    BP       x[ -99.2,  709.1]  y[  -71.9, 1703.3]   margins 99.2 / 81.4 / 201.9 / 58.4 mm

But **bbox containment is not shape containment.** A point-in-polygon test of all
94 string endpoints against a densely-sampled BP gives:

| datum | endpoints outside BP |
|---|---|
| `C=1864.9, dx=0` (old bug) | **94 / 94** |
| `C=130, dx=0` (**shipped fix**) | **47 / 94** |
| `C=20, dx=+20` (reproduces pre-`f408936` placement) | 46 / 94 |
| `C=20, dx=0` | 43 / 94 |

**No candidate datum fits.** The three plausible datums land within noise of each
other (43-47), which means containment **does not discriminate the datum** -- and
that a ~110 mm datum shim would not have fixed anything. This is why the fix
deliberately stops at the reflection and adds **no `dx/dy` shim**.

The actual cause is not a datum at all:

`strings.svg` is a **schematic length chart, not a laid-out harp.** All 47
strings share a single `y1 = -1514.9` -- every tuning-pin end on one *flat*
line. A real harp's pins follow the neck curve: `style25.csv`'s own `Z_necktop`
spans **1694.0 .. 2000.0 mm (a 306 mm rise)**. A flat pin line fits no curved
neck, of any instrument. That is the whole cause and it is sufficient alone.

An earlier draft of this note claimed `strings.svg` **is** the Style 25 string
band and that the mismatch was therefore "two different harps". **That claim is
false and is retracted.** Only the note range and the count match Style 25; the
geometry does not:

|           | strings.svg | style25.csv | delta   |
|-----------|-------------|-------------|---------|
| g7 x      | 627.7       | 643.0       | 15.3 mm |
| c1 length | 1514.9      | 1570.0      | 55.1 mm |
| g7 length | 60.6        | 105.0       | 44.4 mm |

It is not the Style 25 band, and it is not the Paraguayan band either. The
distinction matters practically: on the "two different harps" story you would
expect the *right* instrument's strings to drop straight in. They would not --
a flat pin line mismatches a curved neck whichever harp you pick.

`strings.svg` was added by `93e90b1` as a **"test fixture"** and its commit
message says so. Treat `harp.svg`'s string layer as a *fixture render*, not as
the Paraguayan instrument. Fixing this is a `strings.svg`/paraguayan question,
**not a `harp.js` question** -- `harp.js` correctly reflects whatever it is given.

### STILL OPEN: the y datum remains canvas-padding-dependent

The fix is correct and is a strict improvement, but it does **not** close the
datum question -- it restores the original semantics ("the viewBox's bottom edge
is rail y=0") while leaving the same *class* of fragility. Measured, by adding
100 mm of pure padding to `strings.svg` and changing **zero** string data:

* 100 mm of **bottom** padding (`h` 1864.9 -> 1964.9) shifts every string
  **+100.0 mm**, to `y_up[230, 1744.9]` -- poking 41.6 mm above BP.
* 100 mm of **left** padding shifts them **0.000 mm**.

So the two axes now use different datum conventions: x is anchored to the SVG's
own origin, y to whatever the canvas padding happens to be. `f408936` *was* a
canvas re-datum -- which means the next canvas edit silently re-breaks this in
exactly the same way. The reflection fix is right for today's canvas; a durable
answer needs `strings.svg` to carry an explicit datum, and that is a
`strings.svg`/paraguayan decision.

## 5. The committed harp.svg was stale; the regenerated one legitimately differs

Regenerating against the **old** `strings.svg` from `93e90b1` reproduces the
previously-committed `harp.svg` **byte-identically**. So it was built before the
`f408936` c1-origin change and committed at `7bd10ce` ("commit regenerated
harp.svg + harp.dxf") **without a real regen**.

**There is therefore no valid before/after baseline. Do not diff against the old
`harp.svg`.** Verify against the numbers in section 1 instead.

## 6. Zero-count warnings are NOT a regression

`node harp.js` now warns:

    WARN: no <path data-role="bottom-curve"> ...
    WARN: no <path data-role="top-curve"> ...
    WARN: no <circle data-role="pin"> ...

These are **additive diagnostics**, added because silent `[]` returns ("0 segs",
"pins: 0") are how the 1734.9 mm error hid for two commits. Nothing went missing:
`strings.svg` has 47 `<line>`s and has **always** had zero `data-role` attributes
(`git show 93e90b1:strings.svg | grep -c data-role` = 0, same in the current file).

The viewBox fallback `"0 0 800 600"` now also warns -- it silently flips every y
about 600 for any SVG with width/height but no viewBox.

## 7. The next victim

`clements47cf.svg` has viewBox `-20.838 -20 321.961 1554.9` -- **negative origin**
-- *and* carries exactly the `data-role` set `harp.js` wants (`bottom-curve`,
`top-curve`, `frame-inner`, `frame-outer`, `rung-*`). It is the file most likely
to be fed to `harp.js` next. Pre-fix it would have produced a silent **20 mm**
error -- small enough to pass a visual check. The fix covers it; this records why.

## 8. A counter-example worth knowing

`vb[1]+vb[3]` reflects content into `[0, H]`. `minarea_bezier.py:472,481-482`
reflects about `ymin+ymax` instead, which keeps content in place within the
viewBox. **Both are defensible; they are different frames.** The constant is a
*datum choice*, not a viewBox fact -- which is exactly why section 4's question
cannot be closed from inside `harp.js`.
