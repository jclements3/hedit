# Harp hardware / linkage parts — extracted from the luthiery video

Source: `Video promotion Mediterranean harp luthiery [am7jsUQ1ytw].mp4`
(concertharps.com — Mediterranean harp luthiery). Frames sampled at 3 fps,
347 raw → 210 perceptual-hash-deduped → curated below.

Folders:
- `raw/`   — 347 frames @ 3 fps
- `dedup/` — 210 unique frames (near-duplicates removed)
- `parts/` — curated, sharpest representative(s) per part group
- `sheet_1..6.jpg` — contact sheets of all dedup frames
- `PARTS_overview.jpg` — contact sheet of the curated parts only

## Parts to model

| # | name | what it is | notes |
|---|------|------------|-------|
| 01 | sharpening-jig | rotating fixture grinding the lever blank | tooling/context, not a harp part |
| 02 | brass-hook-lever | small L-shaped sharping hook, 2 holes | core linkage element |
| 03 | threaded-coupling | brass coupling/ferrule joined to wire | |
| 04 | caliper-measure | the hook being measured | **reads 13.94 mm** |
| 05 | bracket-plate-drill | flat brass bracket, drilled holes | mounting bracket |
| 06 | sharping-lever-cam | cam-plate sharping lever on neck plate + string | **key semitone linkage** |
| 07 | tuning-pin-starwasher | tuning pin w/ knob + star washer | |
| 08 | ferrule-grommet | brass ferrule/bushing + red grommet set into neck | string bushing |
| 09 | lever-rail-curved | curved brass rail carrying the full row of levers | assembly context |
| 10 | lever-row-detail | detail of the mounted lever row | assembly context |

## Linkage sequence (1:10–1:24, the "how it works" segment)

`parts/linkage_seq/` — 84 frames @ 6 fps from t=70–84 s, cluster-deduped to 26
sharpest stills (named `lk_<timestamp>s.jpg`). Overview: `parts/LINKAGE_overview.jpg`.

What it shows (critical for modeling the mechanism):
- **70.0–72.0 s** — a single brass bell-crank lever positioned at its pivot hole
  next to the red string-bushing/grommet (close-up of one linkage joint).
- **72.7–77.3 s** — pull-back to the curved brass neck rail carrying the full row
  of cranks.
- **83.5–83.8 s** — clearest view: triangular brass **bell-crank levers** pinned to
  the neck plate, all joined by one continuous thin **steel actuating rod** along the
  curve; strings visible in the inset. The rod translates → every crank rotates
  together → ganged string engagement.

Parts to model from this: (a) the triangular bell-crank lever, (b) its pivot
pin/bushing, (c) the continuous actuating rod, (d) the rod-to-crank pin joints,
(e) the drilled neck plate they mount to.

## Finished-instrument reference (1:40–1:46 end-card)

t=100–106 s is the closing end-card, NOT a linkage close-up — it's the full finished
harp (right side, unobscured) beside the concertharps.com logo. Saved as overall
references for proportions / neck curve / string layout / lever-row placement:
- `parts/harp_reference_full.jpg` — full 640x360 end-card (sharpest frame)
- `parts/harp_reference_crop.jpg` — harp cropped out of the logo whitespace

## ★ Linkage detail — best reference (t≈79 s, user-flagged critical)

`parts/linkage_detail/` — clearest views of the full mechanism, sharpest frames at
78.4 / 79.1 / 80.4 s (a gloved hand works the rod, so the cranks sit at slightly
different angles between frames → shows the actuation/motion range).

Mechanism, fully legible here:
- triangular brass **bell-crank levers** on pivot pins through the neck plate
- one continuous thin **steel actuating rod** curving from crank to crank
- two parallel **gangs** (upper + lower rows) following the neck curve
- drilled **string-pin hole** grid in the plate
- pulling the rod (hand, lower-left) rotates every crank together → ganged engagement

Use `linkage_79.1s.jpg` / `linkage_80.4s.jpg` as the primary modeling reference;
they supersede the more distant `lk_083.7s.jpg`.
