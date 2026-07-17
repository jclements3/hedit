#!/usr/bin/env python3
"""harp_lanes.py — LANE-FIRST soundbox build (the convoy doctrine in 3-D).

Sections stay the transverse truth (exact limaçon math); the SURFACE is built
longitudinally: every ring vertex index j defines a 3-D lane across all
stations, each lane is Schneider-fitted to a true cubic-bezier curve (G1, the
same fitter as hedit / frame1.svg, made dimension-agnostic), and the solid is
lofted through rings REBUILT from the faired lanes. Smoothing happens along
the flow direction — where the h-field jitter actually lives — instead of
being averaged across stacked rings after the fact.

    python3 harp_lanes.py [harp_spec.json] [frame.svg]
    -> out/soundbox_lanes.step
    -> prints raw-vs-faired lane smoothness

M = 96 vertices/ring (multiple of the 12 rose flutes, per JC).
"""
import ctypes, json, math, os, sys

try:
    ctypes.CDLL(os.path.expanduser("~/miniconda3/lib/libexpat.so.1"))
except OSError:
    pass

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../.."))          # bezierfit.py at repo root
import bezierfit  # noqa: E402
import harp as H  # noqa: E402  (the verified section pipeline in this dir)
from build123d import Wire, Solid, export_step  # noqa: E402

M = 96          # ring vertices (12 flutes x 8)
K = 120         # rebuilt stations sampled from the faired lanes
FIT_ERR = 0.5   # Schneider tolerance per lane, mm


def bez_eval(c, t):
    c = [np.asarray(p, float) for p in c]
    mt = 1 - t
    return (mt**3)*c[0] + 3*(mt**2)*t*c[1] + 3*mt*(t**2)*c[2] + (t**3)*c[3]


def lane_resample(curves, k):
    """k arclength-uniform samples along a fitted bezier chain."""
    dense = []
    for c in curves:
        for t in np.linspace(0, 1, 24, endpoint=False):
            dense.append(bez_eval(c, t))
    dense.append(np.asarray(curves[-1][3], float))
    dense = np.asarray(dense)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))]
    u = np.linspace(0, s[-1], k)
    return np.c_[[np.interp(u, s, dense[:, i]) for i in range(3)]].T


def max_turn(P):
    d = np.diff(np.asarray(P), axis=0)
    d = d[np.linalg.norm(d, axis=1) > 1e-9]
    dn = d / np.linalg.norm(d, axis=1)[:, None]
    dots = np.clip((dn[:-1] * dn[1:]).sum(1), -1, 1)
    return float(np.degrees(np.arccos(dots)).max()) if len(dots) else 0.0


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../sweep2/harp_spec.json")
    frame_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "../../sweep2/frame.svg")
    spec = json.load(open(spec_path))
    svg = open(frame_path).read()
    green = H.flatten(H.getd(svg, "green_curve"))
    red = H.flatten(H.getd(svg, "red_curve"))

    sb = spec.get("soundbox", {})
    c_out, b_div = sb.get("c_out", 2.0), sb.get("b_divisor", 4)
    S = spec.get("sampling", {}).get("S", 160)
    trim = spec.get("base", {}).get("trim_z", 130.0)
    sh_in = spec.get("windows", {}).get("sh_in", {"x": 965.2, "y": 525.3})

    a, b = 0, len(green) - 1
    while a < len(green)//2 and (H.FLOOR - green[a][1]) < trim: a += 1
    while b > len(green)//2 and (H.FLOOR - green[b][1]) < trim: b -= 1
    g = green[a:b+1]
    seg = H.cumseg(g)
    us = [seg[-1] * k / (S - 1) for k in range(S)]
    spine = [H.interp(u, seg, g) for u in us]

    N = []
    for i in range(S):
        a2, b2 = spine[max(i-1, 0)], spine[min(i+1, S-1)]
        dx, dy = b2[0]-a2[0], b2[1]-a2[1]
        n = math.hypot(dx, dy) or 1
        N.append((-dy/n, dx/n))
    cen = (400.0, 900.0); q = S // 4
    if (spine[q][0]-cen[0])*N[q][0] + (spine[q][1]-cen[1])*N[q][1] < 0:
        N = [(-nx, -ny) for nx, ny in N]
    for i in range(1, S):
        if N[i][0]*N[i-1][0] + N[i][1]*N[i-1][1] < 0:
            N[i] = (-N[i][0], -N[i][1])
    h = [H.ray_hit(spine[i], N[i], red) or 200.0 for i in range(S)]

    si = min(range(S), key=lambda i: math.hypot(spine[i][0]-sh_in["x"], spine[i][1]-sh_in["y"]))
    stations = [i for i in range(S) if us[i] < us[si]]
    print(f"stations: {len(stations)}  M={M}  c_out={c_out}")

    # exact section rings, ALL stations (stride 1 — the lanes do the fairing)
    rings = []
    for k in stations:
        bb = h[k] / b_div
        ring = []
        for j in range(M):
            th = 2*math.pi*j/M
            r = bb*(c_out + math.cos(th))
            ring.append((-r*math.sin(th), r*math.cos(th)))
        ymin = min(p[1] for p in ring)
        o = (spine[k][0], 0.0, H.FLOOR - spine[k][1])
        nx, ny = N[k]
        rings.append([(o[0]+(p[1]-ymin)*nx, p[0], o[2]+(p[1]-ymin)*(-ny)) for p in ring])
    rings = np.asarray(rings)                    # (n_st, M, 3)

    # LANES: vertex j across stations -> Schneider bezier -> arclength resample
    raw_worst, fair_worst, total_segs = 0.0, 0.0, 0
    faired = np.zeros((K, M, 3))
    for j in range(M):
        lane = rings[:, j, :]
        raw_worst = max(raw_worst, max_turn(lane))
        curves = bezierfit.fit_curve([np.array(p) for p in lane], max_error=FIT_ERR)
        total_segs += len(curves)
        smooth = lane_resample(curves, K)
        fair_worst = max(fair_worst, max_turn(smooth))
        faired[:, j, :] = smooth
    print(f"lanes: {M} fitted, avg {total_segs/M:.1f} bezier segs/lane")
    print(f"lane smoothness (max turning angle): raw rings {raw_worst:.2f}°  ->  faired {fair_worst:.2f}°")

    # loft the rebuilt rings
    sections = []
    for k in range(0, K, 3):
        sections.append(Wire.make_polygon([tuple(p) for p in faired[k]], close=True))
    sections.append(Wire.make_polygon([tuple(p) for p in faired[-1]], close=True))
    print(f"lofting {len(sections)} faired rings through OCC…")
    solid = Solid.make_loft(sections, ruled=False)   # wires may be slightly non-planar — ThruSections handles it
    print("solid volume:", round(solid.volume/1e6, 2), "L")

    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
    export_step(solid, os.path.join(out, "soundbox_lanes.step"))
    print("STEP →", os.path.join(out, "soundbox_lanes.step"))


if __name__ == "__main__":
    main()
