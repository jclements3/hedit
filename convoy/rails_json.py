"""
rails_json.py -- read DP/BP/SP rails out of paraguayan_overrides.json.

The missing piece: convoy.py parses rails out of an SVG, but hedit's rails are not
authored in an SVG at all. They live in

    /home/james.clements/projects/paraguayan/paraguayan_overrides.json

as node+handle Bezier chains (DP=9 nodes, BP=10, SP=9, all closed:true), and
hedit/harp-maker/harp.js reads THAT to build harp.svg. HARP_PLAN.md is explicit
that DP/BP/SP are OUTPUTS of paraguayan/harp.py, so this module opens the file
READ-ONLY and nothing here ever writes it.

Handle semantics mirror harp.js:29-34 `chainToBeziers` exactly:

    hp = (node, h) => [node.x + node[h].dx, node.y + node[h].dy]
    seg(a, b)      =  [a, a+a.hout, b+b.hin, b]

i.e. handles are RELATIVE OFFSETS FROM THEIR OWN NODE (p1 = p0 + hout,
p2 = p3 + hin), NOT absolute control points. Getting this backwards yields a
plausible-looking but wrong rail. `closed:true` appends the wrap segment
last->first (harp.js:33).

Frame: the JSON is Y-up mm -- "exactly Maker.js's native frame, so the rails
import 1:1 with no flip" (harp.js:13-14). We keep Y-up throughout and flip only
for display in the HTML.
"""

import json
import numpy as np

OVERRIDES = "/home/james.clements/projects/paraguayan/paraguayan_overrides.json"


def load_overrides(path=OVERRIDES):
    with open(path) as f:
        return json.load(f)


def _hp(node, h):
    """Handle point: node + relative offset. Mirrors harp.js:30."""
    d = node.get(h)
    return np.array([node["x"] + (d["dx"] if d else 0.0),
                     node["y"] + (d["dy"] if d else 0.0)])


def chain_to_segments(ch):
    """-> list of [p0, p1, p2, p3] cubic control sets. Mirrors harp.js:29-34."""
    n = ch["nodes"]
    def seg(a, b):
        return [np.array([a["x"], a["y"]]), _hp(a, "hout"),
                _hp(b, "hin"), np.array([b["x"], b["y"]])]
    segs = [seg(n[k - 1], n[k]) for k in range(1, len(n))]
    if ch.get("closed") and len(n) > 1:
        segs.append(seg(n[-1], n[0]))
    return segs


def chain_to_polyline(ch, per_seg=64):
    """Dense polyline. For closed chains P[-1] == P[0] exactly (the wrap segment
    ends on node 0), so the closure gap is 0 by construction, not by luck."""
    pts = []
    for k, (p0, p1, p2, p3) in enumerate(chain_to_segments(ch)):
        u = np.linspace(0.0, 1.0, per_seg + 1)[:, None]
        if k:                      # drop the duplicated joint, keep the last point
            u = u[1:]
        pts.append((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1
                   + 3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3)
    return np.vstack(pts)


def assert_full_handles(ch, name):
    """Every DP/BP/SP node has BOTH handles (verified 9/9, 10/10, 9/9) so
    chain_to_polyline needs no missing-handle branch -- but assert it, don't
    trust it. _hp() would silently treat a missing handle as a zero offset."""
    bad = [i for i, nd in enumerate(ch["nodes"])
           if nd.get("hin") is None or nd.get("hout") is None]
    if bad:
        raise AssertionError("%s: nodes missing a handle: %s" % (name, bad))


def rail(name, path=OVERRIDES, per_seg=64):
    ch = load_overrides(path)[name]
    assert_full_handles(ch, name)
    return chain_to_polyline(ch, per_seg)


def signed_area(P):
    """Shoelace. NEGATIVE = clockwise in a Y-up frame."""
    x, y = P[:, 0], P[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def closure_gap(P):
    return float(np.linalg.norm(P[-1] - P[0]))
