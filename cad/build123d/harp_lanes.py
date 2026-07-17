#!/usr/bin/env python3
"""harp_lanes.py — LANE-FIRST full-spine build (the convoy doctrine in 3-D).

Lanes run CONTINUOUSLY through the whole wishbone:

    soundbox (limaçon) → SHOULDER MORPH → U-beam neck → CROWN MORPH → rose pillar

Sections stay the transverse truth (core.py math); the morphs are smoothstep
vertex blends of apex-rolled, arclength-resampled profiles (exactly sweep2's
crown-morph recipe, applied to both transitions); the rose helix advances by
INTEGER vertex steps (M=96 = 12 flutes x 8, so flutes stay on lane vertices).
Every ring-vertex lane is then Schneider-fitted to a true 3-D bezier chain and
the solid is lofted through rings REBUILT from the faired lanes.

    python3 harp_lanes.py [harp_spec.json] [frame.svg]
    -> out/harp_lanes.step
    -> prints raw-vs-faired smoothness, overall and inside each morph window
"""
import ctypes, json, math, os, sys

try:
    ctypes.CDLL(os.path.expanduser("~/miniconda3/lib/libexpat.so.1"))
except OSError:
    pass

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../.."))            # bezierfit.py
sys.path.insert(0, os.path.join(HERE, "../../sweep2"))     # core.py (authoritative sections)
import bezierfit  # noqa: E402
import core       # noqa: E402
import harp as H  # noqa: E402
from build123d import Wire, Solid, Compound, export_step  # noqa: E402

M = 96
K = 240          # rebuilt stations from the faired lanes
FIT_ERR = 0.5    # Schneider tolerance per lane, mm
ROSE_TURNS = 0.5


def smoothstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def prep(ext):
    """apex-roll + arclength-resample to M — the shared lane-correspondence frame.
    Winding is normalized (signed area < 0) so every family lofts the same way."""
    e = np.asarray(ext)
    x, y = e[:, 0], e[:, 1]
    if 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) > 0:
        e = e[::-1]
    return core._resample(core._roll(e), M)


def rose_prof(h):
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    fl = (3 + 0.4 * np.sin(12 * th)) / 3.4
    e = np.c_[(h / 2) * fl * np.cos(th), h / 2 + (h / 2) * fl * np.sin(th)]
    e[:, 1] -= e[:, 1].min()
    return e


def limacon_prof(c_out, b):
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    r = b * (c_out + np.cos(th))
    e = np.c_[-r * np.sin(th), r * np.cos(th)]
    e[:, 1] -= e[:, 1].min()
    return e


def ubeam_prof(b, plate_out):
    e = core.opened(1.0, b)
    nat = np.ptp(e[:, 0])
    if nat > 1e-6:
        e[:, 0] *= plate_out / nat
    return e


def max_turn_stats(P):
    d = np.diff(np.asarray(P), axis=0)
    d = d[np.linalg.norm(d, axis=1) > 1e-9]
    if len(d) < 2:
        return np.zeros(1)
    dn = d / np.linalg.norm(d, axis=1)[:, None]
    return np.degrees(np.arccos(np.clip((dn[:-1] * dn[1:]).sum(1), -1, 1)))


def bez_dense(curves, per=24):
    out = []
    for c in curves:
        c = [np.asarray(p, float) for p in c]
        for t in np.linspace(0, 1, per, endpoint=False):
            mt = 1 - t
            out.append((mt**3)*c[0] + 3*(mt**2)*t*c[1] + 3*mt*(t**2)*c[2] + (t**3)*c[3])
    out.append(np.asarray(curves[-1][3], float))
    return np.asarray(out)


def lane_resample(curves, k):
    dense = bez_dense(curves)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))]
    u = np.linspace(0, s[-1], k)
    return np.c_[[np.interp(u, s, dense[:, i]) for i in range(3)]].T


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../sweep2/harp_spec.json")
    frame_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "../../sweep2/frame.svg")
    spec = json.load(open(spec_path))
    svg = open(frame_path).read()
    green = H.flatten(H.getd(svg, "green_curve"))
    red = H.flatten(H.getd(svg, "red_curve"))

    sb = spec.get("soundbox", {})
    c_out, b_div = sb.get("c_out", 2.0), sb.get("b_divisor", 4)
    plate_out = spec.get("neck", {}).get("plate_out", 35.3)
    S = spec.get("sampling", {}).get("S", 160)
    trim = spec.get("base", {}).get("trim_z", 130.0)
    W = spec.get("windows", {})
    sh_in, sh_out = W.get("sh_in", {"x": 965.2, "y": 525.3}), W.get("sh_out", {"x": 955.5, "y": 520.8})
    cr_in, cr_out = W.get("cr_in", {"x": 348.1, "y": 293.4}), W.get("cr_out", {"x": 203.1, "y": 395.2})

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

    def snap(A):
        return min(range(S), key=lambda i: math.hypot(spine[i][0]-A["x"], spine[i][1]-A["y"]))
    i_sh0, i_sh1 = snap(sh_in), snap(sh_out)
    i_cr1 = snap(cr_out); cwin = max(i_cr1 - snap(cr_in), 1)
    i_cr0 = i_cr1 - cwin
    if i_sh1 <= i_sh0: i_sh1 = i_sh0 + 1
    fam = lambda i: ("soundbox" if i < i_sh0 else "shoulder" if i <= i_sh1
                     else "neck" if i < i_cr0 else "crown" if i < i_cr1 else "pillar")
    print(f"stations: {S}  shoulder morph {i_sh0}..{i_sh1} ({i_sh1-i_sh0} st)  "
          f"crown morph {i_cr0}..{i_cr1} ({cwin} st)  M={M}")

    # ---- per-station profiles in the shared lane frame ----
    rings = np.zeros((S, M, 3))
    for i in range(S):
        bb = h[i] / b_div
        f = fam(i)
        if f == "soundbox":
            prof = prep(limacon_prof(c_out, bb))
        elif f == "shoulder":
            t = smoothstep((i - i_sh0) / max(i_sh1 - i_sh0, 1))
            prof = (1-t) * prep(limacon_prof(c_out, bb)) + t * prep(ubeam_prof(bb, plate_out))
        elif f == "neck":
            prof = prep(ubeam_prof(bb, plate_out))
        elif f == "crown":
            t = smoothstep((i - i_cr0) / cwin)
            prof = (1-t) * prep(ubeam_prof(bb, plate_out)) + t * prep(rose_prof(h[i]))
        else:
            prof = prep(rose_prof(h[i]))
            spin = int(round(ROSE_TURNS * M * (i - i_cr1) / max(S - 1 - i_cr1, 1)))
            prof = np.roll(prof, -spin, axis=0)          # helix by whole vertices — flutes stay on lanes
        o = np.array([spine[i][0], 0.0, H.FLOOR - spine[i][1]])
        nx, ny = N[i]
        v = np.array([nx, 0.0, -ny]); u2 = np.array([0.0, 1.0, 0.0])
        R = o + np.outer(prof[:, 1], v) + np.outer(prof[:, 0], u2)
        R[:, 2] = np.maximum(R[:, 2], 0.0)          # sweep2 flat-floor invariant (min z 0.00)
        rings[i] = R

    # ---- lanes across ALL stations: fit -> fair ----
    def window_stats(turn_by_lane, lo, hi):
        """turning angles whose vertex index falls inside [lo,hi)"""
        vals = [t[max(lo-1, 0):hi-1] for t in turn_by_lane]
        vals = np.concatenate([v for v in vals if len(v)]) if vals else np.zeros(1)
        return vals

    raw_turns, fair_turns, total_segs = [], [], 0
    faired = np.zeros((K, M, 3))
    for j in range(M):
        lane = rings[:, j, :]
        raw_turns.append(max_turn_stats(lane))
        curves = bezierfit.fit_curve([np.array(p) for p in lane], max_error=FIT_ERR)
        total_segs += len(curves)
        faired[:, j, :] = lane_resample(curves, K)
    fair_turns = [max_turn_stats(faired[:, j, :]) for j in range(M)]
    raw_all, fair_all = np.concatenate(raw_turns), np.concatenate(fair_turns)
    print(f"lanes: {M} fitted, avg {total_segs/M:.1f} bezier segs/lane")
    print(f"overall  turn: raw mean {raw_all.mean():.2f}° p95 {np.percentile(raw_all,95):.2f}°  ->  "
          f"faired mean {fair_all.mean():.2f}° p95 {np.percentile(fair_all,95):.2f}°")
    for name, lo, hi in (("shoulder morph", i_sh0-2, i_sh1+3), ("crown morph", i_cr0-2, i_cr1+3)):
        w = window_stats(raw_turns, lo, hi)
        print(f"{name:15s} raw max {w.max():6.2f}° mean {w.mean():5.2f}°   (window st {lo}..{hi})")

    # ---- loft the rebuilt rings (fallback: two pieces at the crown) ----
    def wires_of(kk):
        return [Wire.make_polygon([tuple(p) for p in faired[k]], close=True) for k in kk]
    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
    idx = list(range(0, K, 3)) + ([K-1] if (K-1) % 3 else [])
    try:
        solid = Solid.make_loft(wires_of(idx), ruled=False)
        print("full-spine loft OK — volume", round(solid.volume/1e6, 2), "L")
        export_step(solid, os.path.join(out, "harp_lanes.step"))
    except Exception as e:
        print("full loft refused (%s) — lofting in two pieces at the crown" % str(e)[:80])
        k_cr = int(round((i_cr0 / (S-1)) * (K-1)))
        a_idx = [k for k in idx if k <= k_cr] + [k_cr]
        b_idx = [k_cr] + [k for k in idx if k > k_cr]
        sa = Solid.make_loft(wires_of(sorted(set(a_idx))), ruled=False)
        sb2 = Solid.make_loft(wires_of(sorted(set(b_idx))), ruled=False)
        print("two-piece loft OK — volumes", round(sa.volume/1e6, 2), "+", round(sb2.volume/1e6, 2), "L")
        export_step(Compound([sa, sb2]), os.path.join(out, "harp_lanes.step"))
    print("STEP →", os.path.join(out, "harp_lanes.step"))


if __name__ == "__main__":
    main()
