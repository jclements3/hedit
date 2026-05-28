"""
fit_bottoms.py
==============

Fit a cubic-Bezier curve through the BOTTOM ends of the harp strings in an SVG,
using Schneider's algorithm (bezierfit.py). Writes a copy of the SVG with the
fitted curve added as a <path data-role="bottom-curve">, and prints the path 'd'.

Usage:  python3 fit_bottoms.py [in.svg] [out.svg] [max_nodes]
Default: strings.svg -> strings_bottomcurve.svg, max_nodes = 8

`max_nodes` is the max number of on-curve nodes (anchors); the curve uses at
most max_nodes-1 cubic segments and its first/last nodes are pinned to the
first/last string bottoms exactly.

Pure ASCII. No Unicode.
"""

import re
import sys
import numpy as np
from bezierfit import fit_curve_max_nodes, q

IN  = sys.argv[1] if len(sys.argv) > 1 else "strings.svg"
OUT = sys.argv[2] if len(sys.argv) > 2 else "strings_bottomcurve.svg"
MAX_NODES = int(sys.argv[3]) if len(sys.argv) > 3 else 8


def attr(tag, name):
    m = re.search(r'\b' + name + r'="([^"]+)"', tag)
    return float(m.group(1)) if m else None


def bottom_points(svg_text):
    """Bottom (larger-y) endpoint of every string <line> (skips the S axis)."""
    pts = []
    for m in re.finditer(r'<line\b[^>]*?/?>', svg_text):
        tag = m.group(0)
        if 'data-role="s-axis"' in tag:
            continue
        x1, y1, x2, y2 = (attr(tag, k) for k in ("x1", "y1", "x2", "y2"))
        if None in (x1, y1, x2, y2):
            continue
        bx, by = (x1, y1) if y1 >= y2 else (x2, y2)   # bottom = larger y (SVG y-down)
        pts.append((bx, by))
    pts.sort(key=lambda p: p[0])                       # left -> right along the spacing axis
    return np.array(pts, dtype=float)


def curves_to_d(curves):
    c0 = curves[0]
    d = "M %.3f %.3f" % (c0[0][0], c0[0][1])
    for c in curves:
        d += " C %.3f %.3f %.3f %.3f %.3f %.3f" % (
            c[1][0], c[1][1], c[2][0], c[2][1], c[3][0], c[3][1])
    return d


def max_residual(pts, curves):
    """Worst point-to-curve distance, sampling each segment densely."""
    samp = []
    for c in curves:
        for i in range(41):
            samp.append(q(c, i / 40.0))
    samp = np.array(samp)
    worst = 0.0
    for p in pts:
        d = np.min(np.hypot(samp[:, 0] - p[0], samp[:, 1] - p[1]))
        worst = max(worst, d)
    return worst


def main():
    svg = open(IN).read()
    pts = bottom_points(svg)
    if len(pts) < 2:
        print("Need at least 2 string bottoms; found %d" % len(pts))
        return
    curves = fit_curve_max_nodes(pts, MAX_NODES)
    d = curves_to_d(curves)
    resid = max_residual(pts, curves)
    start, end = curves[0][0], curves[-1][3]
    print("input bottoms : %d points  (x %.1f..%.1f, y %.1f..%.1f)"
          % (len(pts), pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()))
    print("max_nodes     : %d  ->  %d node(s), %d cubic segment(s), max residual %.4f"
          % (MAX_NODES, len(curves) + 1, len(curves), resid))
    print("end nodes     : start (%.3f, %.3f) == first bottom %s ; end (%.3f, %.3f) == last bottom %s"
          % (start[0], start[1], np.allclose(start, pts[0]),
             end[0], end[1], np.allclose(end, pts[-1])))
    print("path d        : %s" % d)

    path = ('<path data-role="bottom-curve" d="%s" fill="none" '
            'stroke="#cc2222" stroke-width="1.5"/>' % d)
    out = re.sub(r'</svg>\s*$', path + "\n</svg>\n", svg, count=1)
    open(OUT, "w").write(out)
    print("wrote         : %s (original + fitted bottom curve)" % OUT)


if __name__ == "__main__":
    main()
