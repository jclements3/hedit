# Clements 49 — sweep2 wishbone package

Read first: HANDOFF_SWEEP2.md, then GREEN_ORIENTATION.md.

## Interactive HTML (open in any browser, self-contained)
- morph_picker.html   — drag the 4 transition anchors on the green spine; "copy spec" -> paste to Claude
- lanes.html          — animated isometric, lanes only (base + arms + bores), ortho view buttons
- snapshot.html       — static side / rear / bottom panels of the current build
- floor_check.html    — bottom-view proof: mouths vs authored base.svg
- rgb.html            — the three control curves as core._flatten consumes them
- rgb_morph.html      — spine colored by section family + transition ticks
- harp.html           — earlier ring-stack viewer (superseded by lanes.html; kept for reference)

## Build scripts (python3; needs numpy, shapely, scipy)
- sweep2.py           — THE build. sweep2.wishbone("frame.svg","base.svg",anchors=SPEC)
                        -> (rings, bores, (base_outer, base_inner), meta).
                        assert_green_orientation() runs first and fails loudly if the frame is swapped.
- core.py             — section primitives + canonical _flatten parser (project copy)
- convoy.py           — DTW correspondence lane machinery (project copy)
- wishbone_ring0.py   — historical lobe splitter (superseded by boolean-join fits; reference only)

## Data
- frame.svg           — frame v14 (red/green/blue rails), from frame_v14_svg.txt
- base.svg            — authored floor footprint (red_outer + blue_outer)

## Templates (viewer regeneration)
- lanes_template.html / picker_template.html / harp_template.html
  Rebuild pattern: template.replace("__DATA__", json_from_sweep2)

## Current authored anchors
{"sh_in":{"x":965.2,"y":525.3},"sh_out":{"x":955.5,"y":520.8},
 "cr_in":{"x":348.1,"y":293.4},"cr_out":{"x":203.1,"y":395.2}}
