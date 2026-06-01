"""
trace_parts.py
==============

Separate the gold (bell-crank/lever) parts and the gray linkage rods in
parts/bellcrank.png by color, extract each part's outer outline, fit it with
Schneider's cubic-Bezier fitter (bezierfit.fit_curve), and write one SVG per
part (plus a combined overview SVG and a verification overlay PNG).

Pure ASCII. Coordinates are image pixels (y-down), which is SVG-native, so
the viewBox is "0 0 W H".
"""

import os
import cv2
import numpy as np
import bezierfit

SRC = "parts/bellcrank.png"
OUT = "parts/bellcrank_svg"

# ---- color thresholds (from sampling) -------------------------------------
# gold: hue<40, saturation high, bright;  gray rod: very low saturation, bright
def gold_mask(hsv):
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    m = ((S > 40) & (V > 90) & (H < 40)).astype(np.uint8) * 255
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

def gray_mask(hsv):
    S, V = hsv[:, :, 1], hsv[:, :, 2]
    m = ((S < 28) & (V > 95)).astype(np.uint8) * 255
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))


# ---- contour helpers -------------------------------------------------------
def outer_contour(comp_mask):
    """Largest external contour of a single-component mask, as an (N,2) array."""
    cnts, _ = cv2.findContours(comp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cnts, key=cv2.contourArea)
    return cnt.reshape(-1, 2).astype(float)


def smooth_closed(pts, sigma=2.0, step=2):
    """Periodic Gaussian smoothing of a closed contour, then subsample."""
    n = len(pts)
    rad = max(1, int(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2)
    k /= k.sum()
    idx = (np.arange(n)[:, None] + np.arange(-rad, rad + 1)[None, :]) % n
    sm = (pts[idx] * k[None, :, None]).sum(axis=1)
    sm = sm[::step]
    # roll seam to the topmost point (usually low-curvature) for a clean join
    seam = int(np.argmin(sm[:, 1]))
    sm = np.roll(sm, -seam, axis=0)
    return sm


def fit_closed(pts, max_error):
    """Fit a closed cubic-Bezier loop; returns list of 4x2 control-point segs."""
    loop = np.vstack([pts, pts[0]])           # close: start == end
    return bezierfit.fit_curve(loop, max_error)


def segs_to_path_d(segs):
    f = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
    p0 = segs[0][0]
    d = ["M %s,%s" % (f(p0[0]), f(p0[1]))]
    for s in segs:
        d.append("C %s,%s %s,%s %s,%s" % (
            f(s[1][0]), f(s[1][1]), f(s[2][0]), f(s[2][1]), f(s[3][0]), f(s[3][1])))
    d.append("Z")
    return " ".join(d)


def write_svg(path, d, W, H, fill, name):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
        '  <path data-part="%s" d="%s" fill="%s" stroke="#333" stroke-width="0.5"/>\n'
        '</svg>\n' % (W, H, W, H, name, d, fill))
    with open(path, "w") as fh:
        fh.write(svg)


# ---- main ------------------------------------------------------------------
def components(mask, area_min, area_max=10 ** 9):
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask, 8)
    out = []
    for i in range(1, n):
        a = stats[i, cv2.CC_STAT_AREA]
        if area_min <= a <= area_max:
            out.append((i, a, tuple(cent[i])))
    return lab, out


def name_for(prefix, cx, cy, W, H):
    vert = "top" if cy < H / 3 else ("bottom" if cy > 2 * H / 3 else "mid")
    horiz = "left" if cx < W / 3 else ("right" if cx > 2 * W / 3 else "center")
    return "%s_%s_%s" % (prefix, vert, horiz)


def main():
    os.makedirs(OUT, exist_ok=True)
    bgr = cv2.imread(SRC)
    H, W = bgr.shape[:2]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    jobs = [("gold", gold_mask(hsv), 300, "#e6b34d", 2.0),
            ("rod",  gray_mask(hsv), 250, "#b3b3b3", 1.6)]

    overlay = np.full((H, W, 3), 255, np.uint8)
    overview_paths = []
    manifest = []

    for prefix, mask, amin, fill, err in jobs:
        lab, comps = components(mask, amin)
        comps.sort(key=lambda t: (t[2][1], t[2][0]))  # top-to-bottom
        for li, area, (cx, cy) in comps:
            comp = (lab == li).astype(np.uint8) * 255
            raw = outer_contour(comp)
            sm = smooth_closed(raw, sigma=2.0, step=2)
            segs = fit_closed(sm, err)
            d = segs_to_path_d(segs)
            name = name_for(prefix, cx, cy, W, H)
            write_svg(os.path.join(OUT, name + ".svg"), d, W, H, fill, name)
            overview_paths.append('  <path d="%s" fill="%s" fill-opacity="0.55" stroke="#333" stroke-width="0.5"/>' % (d, fill))
            manifest.append((name, prefix, area, len(segs), len(raw)))

            # draw fitted curve into overlay for verification
            poly = []
            for s in segs:
                for t in np.linspace(0, 1, 12):
                    poly.append(bezierfit.q(s, t))
            poly = np.array(poly, np.int32)
            cv2.polylines(overlay, [poly], True,
                          (60, 60, 60) if prefix == "rod" else (40, 120, 220), 1, cv2.LINE_AA)

    # combined overview svg
    with open(os.path.join(OUT, "_overview.svg"), "w") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n</svg>\n'
                 % (W, H, W * 3, H * 3, "\n".join(overview_paths)))
    cv2.imwrite(os.path.join(OUT, "_verify_overlay.png"), overlay)

    print("part                     kind  area  segs  rawpts")
    for name, prefix, area, segs, raw in manifest:
        print("%-24s %-4s %5d %5d %6d" % (name, prefix, area, segs, raw))
    print("\nwrote %d SVGs to %s/" % (len(manifest), OUT))


if __name__ == "__main__":
    main()
