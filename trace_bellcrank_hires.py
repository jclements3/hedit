"""Trace the three hi-res bellcrank gold parts (files (8).zip) into clean SVGs.
Reuses trace_parts.py's contour/fit/SVG helpers; supplies a red-excluding gold mask
(the pivot bosses are circled in red, which must not leak into the gold silhouette)."""
import sys, os, cv2, numpy as np
sys.path.insert(0, "/home/james.clements/projects/hedit")
import trace_parts as tp

SRC = "parts/bellcrank_hires"
OUT = "/home/james.clements/projects/hedit/parts/bellcrank_svg"
JOBS = [("arm_topleft_boss.png",    "arm_top_left"),
        ("yoke_midleft_boss.png",   "yoke_mid_left"),
        ("arm_bottomleft_boss.png", "arm_bottom_left")]

def gold_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    r = bgr[:, :, 2].astype(int); g = bgr[:, :, 1].astype(int)
    m = ((S > 45) & (V > 110) & (H < 40) & (g > 0.62 * r)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))  # repair red-ring notches
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return m

for fname, name in JOBS:
    bgr = cv2.imread(os.path.join(SRC, fname))
    Himg, Wimg = bgr.shape[:2]
    m = gold_mask(bgr)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    li = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))   # largest non-bg gold blob
    comp = (lab == li).astype(np.uint8) * 255
    raw = tp.outer_contour(comp)
    sm = tp.smooth_closed(raw, sigma=2.5, step=2)
    segs = tp.fit_closed(sm, 2.0)
    d = tp.segs_to_path_d(segs)
    tp.write_svg(os.path.join(OUT, name + ".svg"), d, Wimg, Himg, "#e6b34d", name)
    # verification overlay
    vis = bgr.copy()
    poly = []
    import bezierfit
    for s in segs:
        for t in np.linspace(0, 1, 18):
            poly.append(bezierfit.q(s, t))
    cv2.polylines(vis, [np.array(poly, np.int32)], True, (40, 120, 220), 2, cv2.LINE_AA)
    cv2.imwrite("/tmp/hires_%s.png" % name, vis)
    print("%-16s %dx%d  area=%d  segs=%d  rawpts=%d" % (name, Wimg, Himg, stats[li, cv2.CC_STAT_AREA], len(segs), len(raw)))
print("wrote SVGs to", OUT)
