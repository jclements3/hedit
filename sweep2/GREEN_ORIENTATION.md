# GREEN_ORIENTATION.md — the four-month invariant (read before touching any sweep)

## The rule
**Never determine arm identity, mating, or placement from the floor.**
The green floor tails CROSS. Each green endpoint lands beside the OTHER arm's
red foot. Any algorithm that pairs "green endpoint ↔ nearest red floor touch"
is wrong by construction and produces the swapped-arm / garbage-base failures
seen repeatedly since the start of the project.

## The authoritative orientation (verified from the curves, frame v14)
Green total arc: 4215 mm.

| side | evidence (follow the CURVE, not the floor) | identity |
|---|---|---|
| **START** (s=0, endpoint x=184) | climbs the string diagonal: (275,1743) at s=200 → (727,966) at s=1100 → reaches the shoulder anchor (968,545) at s=1585, within 0.5 mm of the authored sh_in | **SOUNDBOX foot** |
| **END** (s=4215, endpoint x=249) | the last ~1.4 m runs the vertical pillar column at x=203 (x deviation < 1 mm over 1200 mm of arc) | **PILLAR foot** |

The tails: the soundbox tail curls WEST to x=184 (landing beside the pillar's
red foot); the pillar tail curls EAST to x=249 (landing beside the soundbox).
Floor proximity therefore points at the WRONG mate on both sides, always.

## Floor mating (base.svg)
- Red floor touch clusters: x≈80 (pillar outer wall) and x≈520 (soundbox belly).
- base.svg lobes: rose lobe (low x, full 12-flute) = PILLAR foot; limaçon lobe
  (high x) = SOUNDBOX foot. Boolean join (two complete overlapping shapes),
  union = red_outer. blue_outer likewise: bore circle (pillar) ∪ inner limaçon.
- Correct world placement: rose lobe pinned under the pillar column axis
  (ring centroid x≈166, WEST); limaçon lobe under the soundbox body (x≈253,
  EAST). Note the body centroids sit on the OPPOSITE side of the crossed tail
  endpoints — that is the trap.

## Enforcement
`sweep2.assert_green_orientation()` runs at the top of every `wishbone()` build
and raises loudly if either invariant fails (start must reach the shoulder at
~38% arc; end must ride the x≈203 vertical). Any resample, re-author, or
reversal of green that swaps the arms now fails the build instead of silently
producing a swapped harp.

## Family order along green (JC-confirmed via picker anchors)
s=0 → soundbox limaçon → sh_in s≈1585 → shoulder morph → U-beam neck →
crown morph → rose column (helix) → s=4215 pillar foot. Tails below z=130 are
TRIMMED (never swept); each arm launches vertically from its own authored lobe.
