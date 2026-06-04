#!/usr/bin/env python3
"""
minarea_bezier.py - Minimal-area closed cubic-Bezier wrap around a point set.

Self-contained, single file. Depends only on the scientific stack:
numpy, scipy, shapely. No project-local imports.

Problem
-------
Given a set of 2D points, find a CLOSED cubic-Bezier path with a fixed number
of on-curve nodes such that:
  (1) every point lies inside the path,
  (2) no point is closer than `margin` mm to the path, and
  (3) the enclosed area is as small as possible.

Method
------
1. Base shape.  Two candidates are built and the better (smaller valid area)
   is kept:
     - "ribbon": for the harp border CSV the points come in two ordered
       strands (role=pin, role=sharp). The ribbon is the simple polygon
       pins(1..N) + sharps(N..1), which hugs the band far more tightly than
       the convex hull.
     - "hull": the convex hull of all points (robust fallback for arbitrary
       point clouds with no strand structure).
2. Offset + fit.  The base polygon is buffered outward by d (>= margin) and a
   closed C1 Bezier with `n_nodes` anchors is fit to that offset boundary.
   Anchors are placed by a curvature-weighted arc-length metric (caps and
   sharp turns get nodes); each segment's handles are solved by least squares
   (Schneider's generate_bezier, inlined). A bisection finds the smallest d
   for which the fitted curve is valid, swept over a few curvature weights K.
3. Polish.  A greedy coordinate descent in a C1 parametrization
   (anchor xy, tangent angle, in/out handle lengths) shrinks the curve inward
   wherever there is clearance slack, accepting a move only if it lowers area
   AND keeps the curve valid. This is what drives the area down past the
   uniform-offset fit.
4. Verify.  Exact point-to-Bezier distance (fine sampling) confirms the final
   curve clears `margin`, then the SVG and a control-point table are written.

The greedy descent is deterministic, so runs are reproducible.

Usage
-----
    python3 minarea_bezier.py border.csv
    python3 minarea_bezier.py border.csv --margin 13 --nodes 10 -o wrap.svg
    python3 minarea_bezier.py cloud.csv --base hull --xcol x --ycol z
"""

import argparse
import csv
import math
import sys

import numpy as np
from shapely.geometry import Polygon, Point
import shapely


# ===========================================================================
# Cubic Bezier helpers (inlined; Bernstein basis + least-squares handle solve)
# ===========================================================================

def _b0(u): t = 1.0 - u; return t * t * t
def _b1(u): t = 1.0 - u; return 3.0 * u * t * t
def _b2(u): t = 1.0 - u; return 3.0 * u * u * t
def _b3(u): return u * u * u


def bezier_point(ctrl, u):
    """Evaluate a cubic Bezier (4 control points) at parameter u."""
    return (_b0(u) * ctrl[0] + _b1(u) * ctrl[1]
            + _b2(u) * ctrl[2] + _b3(u) * ctrl[3])


def _chord_param(points):
    u = [0.0]
    for i in range(1, len(points)):
        u.append(u[i - 1] + np.linalg.norm(points[i] - points[i - 1]))
    total = u[-1]
    if total == 0.0:
        return np.zeros(len(points))
    return np.array(u) / total


def _generate_bezier(points, params, left_tangent, right_tangent):
    """Least-squares cubic with fixed endpoints and fixed end-tangent
    directions (Schneider, Graphics Gems 1990). Solves for the two handle
    lengths along the given tangents."""
    bez = [points[0], None, None, points[-1]]
    A = np.zeros((len(points), 2, 2))
    for i, u in enumerate(params):
        A[i][0] = left_tangent * _b1(u)
        A[i][1] = right_tangent * _b2(u)
    C = np.zeros((2, 2))
    X = np.zeros(2)
    for i, (pt, u) in enumerate(zip(points, params)):
        C[0][0] += np.dot(A[i][0], A[i][0])
        C[0][1] += np.dot(A[i][0], A[i][1])
        C[1][0] = C[0][1]
        C[1][1] += np.dot(A[i][1], A[i][1])
        tmp = pt - (_b0(u) * points[0] + _b1(u) * points[0]
                    + _b2(u) * points[-1] + _b3(u) * points[-1])
        X[0] += np.dot(A[i][0], tmp)
        X[1] += np.dot(A[i][1], tmp)
    det_C0_C1 = C[0][0] * C[1][1] - C[1][0] * C[0][1]
    det_C0_X = C[0][0] * X[1] - C[1][0] * X[0]
    det_X_C1 = X[0] * C[1][1] - X[1] * C[0][1]
    alpha_l = 0.0 if det_C0_C1 == 0.0 else det_X_C1 / det_C0_C1
    alpha_r = 0.0 if det_C0_C1 == 0.0 else det_C0_X / det_C0_C1
    seg_len = np.linalg.norm(points[0] - points[-1])
    eps = 1.0e-6 * seg_len
    if alpha_l < eps or alpha_r < eps:
        bez[1] = bez[0] + left_tangent * (seg_len / 3.0)
        bez[2] = bez[3] + right_tangent * (seg_len / 3.0)
    else:
        bez[1] = bez[0] + left_tangent * alpha_l
        bez[2] = bez[3] + right_tangent * alpha_r
    return np.array(bez)


# ===========================================================================
# Closed-curve fitting
# ===========================================================================

def _resample_closed(coords, n):
    """Resample a closed polyline to n distinct points by arc length."""
    c = np.asarray(coords, float)
    if np.allclose(c[0], c[-1]):
        c = c[:-1]
    c = np.vstack([c, c[0]])
    seg = np.hypot(*(np.diff(c, axis=0).T))
    s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], n, endpoint=False)
    return np.column_stack([np.interp(u, s, c[:, 0]),
                            np.interp(u, s, c[:, 1])])


def _anchor_indices(D, n, K):
    """Pick n anchor indices on closed polyline D using a
    (arclen + K * |turning angle|) cumulative metric, so high-curvature
    regions (caps, corners) attract nodes."""
    nd = len(D)
    nxt = np.roll(D, -1, axis=0)
    prv = np.roll(D, 1, axis=0)
    seglen = np.hypot(*((nxt - D).T))
    a1 = np.arctan2((D - prv)[:, 1], (D - prv)[:, 0])
    a2 = np.arctan2((nxt - D)[:, 1], (nxt - D)[:, 0])
    dth = np.abs((a2 - a1 + np.pi) % (2 * np.pi) - np.pi)
    cum = np.concatenate([[0], np.cumsum(seglen + K * dth)])
    targets = np.linspace(0, cum[-1], n, endpoint=False)
    idx = sorted(set(int(i % nd) for i in np.searchsorted(cum, targets)))
    while len(idx) < n:  # split widest gaps until we have n distinct anchors
        gaps = [(((idx[(k + 1) % len(idx)] - idx[k]) % nd), k)
                for k in range(len(idx))]
        g, k = max(gaps)
        ins = (idx[k] + g // 2) % nd
        if ins in idx:
            break
        idx = sorted(idx + [ins])
    return idx[:n]


def _tangent(D, i, delta=3):
    nd = len(D)
    v = D[(i + delta) % nd] - D[(i - delta) % nd]
    L = np.hypot(*v)
    return v / L if L > 0 else np.array([1.0, 0.0])


def closed_fit(exterior, n_nodes, K):
    """Fit a closed C1 cubic-Bezier with exactly n_nodes anchors to the
    ordered closed boundary `exterior`."""
    D = _resample_closed(exterior, max(400, n_nodes * 40))
    idx = _anchor_indices(D, n_nodes, K)
    curves = []
    for k in range(n_nodes):
        i0 = idx[k]
        i1 = idx[(k + 1) % n_nodes]
        seg = D[i0:i1 + 1] if i1 > i0 else np.vstack([D[i0:], D[:i1 + 1]])
        if len(seg) < 2:
            seg = np.vstack([D[i0], D[i1]])
        left = _tangent(D, i0)
        right = -_tangent(D, i1)
        bez = _generate_bezier(seg, _chord_param(seg), left, right)
        bez[0] = D[i0]
        bez[3] = D[i1]
        curves.append(np.asarray(bez, float))
    return curves


# ===========================================================================
# Geometry / evaluation
# ===========================================================================

def curve_polygon(curves, per=80):
    out = []
    for c in curves:
        for t in np.linspace(0, 1, per, endpoint=False):
            out.append(bezier_point(c, t))
    return Polygon(out)


def evaluate(curves, point_geoms, margin, per=80):
    """Return (area, min_signed_clearance, valid). Signed clearance is
    +distance if inside, -distance if outside."""
    poly = curve_polygon(curves, per)
    if not poly.is_valid:
        return poly.area, -1.0, False
    ext = poly.exterior
    dist = shapely.distance(ext, point_geoms)
    inside = shapely.contains(poly, point_geoms)
    signed = np.where(inside, dist, -dist)
    valid = bool(inside.all()) and float(signed.min()) >= margin - 1e-3
    return poly.area, float(signed.min()), valid


def exact_min_clearance(curves, pts, per=1500):
    samp = np.vstack([np.array([bezier_point(c, t)
                                for t in np.linspace(0, 1, per)])
                      for c in curves])
    return min(np.hypot(samp[:, 0] - p[0], samp[:, 1] - p[1]).min()
               for p in pts)


# ===========================================================================
# Stage 1+2: offset bisection + curvature-weight sweep
# ===========================================================================

def fit_min_offset(base_poly, point_geoms, margin, n_nodes, K,
                   symmetric=True, bisect_iters=16):
    """Smallest outward offset d >= margin giving a valid n_node fit, for a
    fixed curvature weight K. Returns (curves, area, d). When symmetric is
    True the fitted handles are forced to equal length per node before the
    validity check, so the returned start is feasible under that constraint."""
    def fit_at(d):
        ext = base_poly.buffer(d, quad_segs=48, join_style=1).exterior.coords
        cv = closed_fit(np.array(ext), n_nodes, K)
        if symmetric:
            cv = _symmetrize(cv)
        a, _, ok = evaluate(cv, point_geoms, margin)
        return cv, a, ok

    lo = hi = margin
    cv, a, ok = fit_at(hi)
    while not ok:
        hi *= 1.18
        cv, a, ok = fit_at(hi)
        if hi > margin * 8:
            break
    for _ in range(bisect_iters):
        mid = 0.5 * (lo + hi)
        cv, a, ok = fit_at(mid)
        if ok:
            hi = mid
        else:
            lo = mid
    cv, a, ok = fit_at(hi)
    return cv, a, hi


def best_initial_fit(base_poly, point_geoms, margin, n_nodes, symmetric=True,
                     K_values=(4, 8, 12, 16, 22, 30, 45, 70), verbose=True):
    best = None
    for K in K_values:
        cv, a, d = fit_min_offset(base_poly, point_geoms, margin, n_nodes, K,
                                  symmetric=symmetric)
        if verbose:
            print(f"    K={K:>3}  d*={d:6.2f}  area={a:10.0f}")
        if best is None or a < best[1]:
            best = (cv, a, d, K)
    return best


# ===========================================================================
# Stage 3: greedy C1-preserving area-minimizing polish
# ===========================================================================

def _to_params(curves):
    n = len(curves)
    A = np.array([curves[k][0] for k in range(n)])
    phi = np.zeros(n)
    lin = np.zeros(n)
    lout = np.zeros(n)
    for k in range(n):
        out_dir = curves[k][1] - curves[k][0]
        in_dir = curves[k][0] - curves[(k - 1) % n][2]
        t = (out_dir / (np.hypot(*out_dir) + 1e-9)
             + in_dir / (np.hypot(*in_dir) + 1e-9))
        phi[k] = math.atan2(t[1], t[0])
        lout[k] = np.hypot(*out_dir)
        lin[k] = np.hypot(*in_dir)
    return A, phi, lin, lout


def _build(A, phi, lin, lout, hcap=0.95):
    """Build cubic segments. Each handle is clamped to `hcap` x the segment chord so a control
    point can never run past its neighbour anchor (which is what makes the curve bulge/loop)."""
    n = len(A)
    u = np.column_stack([np.cos(phi), np.sin(phi)])
    curves = []
    for k in range(n):
        kn = (k + 1) % n
        chord = np.hypot(*(A[kn] - A[k]))
        lo = min(lout[k], hcap * chord)      # out-handle of this segment
        li = min(lin[kn], hcap * chord)      # in-handle of this segment (at the next anchor)
        curves.append(np.array([A[k],
                                A[k] + lo * u[k],
                                A[kn] - li * u[kn],
                                A[kn]]))
    return curves


def _symmetrize(curves):
    """Force equal in/out handle length at every node (mirror handles),
    preserving the collinear tangent direction."""
    A, phi, lin, lout = _to_params(curves)
    L = 0.5 * (lin + lout)
    return _build(A, phi, L, L)


def polish(curves, point_geoms, centroid, margin, n_nodes, symmetric=True,
           fixed=frozenset(), circle=None, fixed_angles=None,
           per=140, max_iters=80, verbose=True):
    circle = circle or {}                 # {idx: (cx, cy, R)}: anchor slides on this circle
    fixed_angles = fixed_angles or {}     # {idx: radians}: tangent angle pinned, not optimized
    A, phi, lin, lout = _to_params(curves)
    for k, a in fixed_angles.items():
        phi[k % n_nodes] = a
    if symmetric:                       # single length per node, tied
        L = 0.5 * (lin + lout)
    cen = np.asarray(centroid, float)
    th = {k: math.atan2(A[k][1]-cy, A[k][0]-cx) for k, (cx, cy, R) in circle.items()}

    def place_circle():
        for k, (cx, cy, R) in circle.items():
            A[k] = np.array([cx + R*math.cos(th[k]), cy + R*math.sin(th[k])])

    def build():
        place_circle()
        return _build(A, phi, L, L) if symmetric else _build(A, phi, lin, lout)

    # Lexicographic score: first drive the min clearance up to `margin` (repair — a pinned anchor
    # can start the curve invalid), then minimize area. Higher tuple is better.
    def score():
        a, s, _ = evaluate(build(), point_geoms, margin, per)
        return (min(s, margin), -a)

    # Full-circle search: for each on-buffer node, test clock positions ALL the way around its
    # circle and keep the best-scoring one. This decides which side the node sits on by the actual
    # area/clearance instead of an outward guess, and lets it jump sides — the greedy ±step slide
    # can't do that (it stalls on whichever side it started). Returns True if anything improved.
    def global_clock(M=96):
        moved = False
        for k in list(circle):
            best_th, best_sc = th[k], score()
            for j in range(M):
                th[k] = -math.pi + 2 * math.pi * j / M
                sc = score()
                if sc > best_sc:
                    best_sc, best_th, moved = sc, th[k], True
            th[k] = best_th
        return moved

    if circle:
        global_clock()                  # seat every node on its best side before local descent
    best = score()
    for it in range(max_iters):
        improved = False
        if circle and it % 8 == 7:      # periodically re-search the full circle (free nodes shift)
            if global_clock():
                best = score(); improved = True
        for dscale, ascale, lscale in [(6, .10, 8), (3, .05, 4),
                                        (1.5, .025, 2), (.6, .01, 1)]:
            for k in range(n_nodes):
                if k in fixed:                 # pinned anchor — position locked
                    continue
                if k in circle:                # slide along its clearance circle (angle is the DOF)
                    dth = dscale / circle[k][2]
                    for s in (dth, -dth):
                        old = th[k]; th[k] += s
                        sc = score()
                        if sc > best:
                            best = sc; improved = True
                        else:
                            th[k] = old
                    continue
                d = (cen - A[k])
                d = d / (np.hypot(*d) + 1e-9)
                old = A[k].copy()
                A[k] = A[k] + d * dscale
                sc = score()
                if sc > best:
                    best = sc; improved = True
                else:
                    A[k] = old
                for ax in range(2):
                    for s in (dscale, -dscale):
                        old = A[k].copy()
                        A[k, ax] += s
                        sc = score()
                        if sc > best:
                            best = sc; improved = True
                        else:
                            A[k] = old
            for k in range(n_nodes):           # tangent angles (free even at pinned nodes)
                if k in fixed_angles:          # ...except where the angle is pinned
                    continue
                for s in (ascale, -ascale):
                    old = phi[k]; phi[k] += s
                    sc = score()
                    if sc > best:
                        best = sc; improved = True
                    else:
                        phi[k] = old
            for k in range(n_nodes):           # handle lengths
                # cap at ~the local chord so a handle can't balloon into a spike
                cap = 1.2 * max(np.hypot(*(A[(k+1) % n_nodes] - A[k])),
                                np.hypot(*(A[k] - A[(k-1) % n_nodes])))
                arrays = (L,) if symmetric else (lin, lout)
                for arr in arrays:
                    for s in (lscale, -lscale):
                        old = arr[k]; arr[k] = min(cap, max(1.0, arr[k] + s))
                        sc = score()
                        if sc > best:
                            best = sc; improved = True
                        else:
                            arr[k] = old
        if verbose and it % 5 == 0:
            print(f"    iter {it:>2}  minclr={best[0]:6.2f}  area={-best[1]:10.0f}")
        if not improved:
            break
    return build()


# ===========================================================================
# I/O
# ===========================================================================

def load_points(path, xcol, ycol, role_col="role"):
    rows = list(csv.DictReader(open(path)))
    has_role = role_col in rows[0]
    strands = {}
    allp = []
    for r in rows:
        p = (float(r[xcol]), float(r[ycol]))
        allp.append(p)
        if has_role:
            strands.setdefault(r[role_col], []).append(p)
    return allp, strands


def path_d(curves):
    s = f"M {curves[0][0][0]:.3f} {curves[0][0][1]:.3f} "
    for seg in curves:
        s += (f"C {seg[1][0]:.3f} {seg[1][1]:.3f} "
              f"{seg[2][0]:.3f} {seg[2][1]:.3f} "
              f"{seg[3][0]:.3f} {seg[3][1]:.3f} ")
    return s + "Z"


def write_svg(path, curves, strands, allp, margin, area, flip_y=True):
    dense = np.vstack([np.array([bezier_point(c, t)
                                 for t in np.linspace(0, 1, 200, endpoint=False)])
                       for c in curves])
    cen = np.array(Polygon(dense).centroid.coords[0])
    xs = [p[0] for p in allp] + list(dense[:, 0])
    ys = [p[1] for p in allp] + list(dense[:, 1])
    pad = 24
    xmin, xmax = min(xs) - pad, max(xs) + pad
    ymin, ymax = min(ys) - pad, max(ys) + pad
    W, H = xmax - xmin, ymax - ymin
    ysum = ymin + ymax
    colors = ["#cf3b2d", "#3f86d0", "#5aa469", "#c8923a"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="{xmin:.2f} {ymin:.2f} {W:.2f} {H:.2f}" '
           f'width="860" height="{860 * H / W:.0f}" '
           f'font-family="Cormorant Garamond, Georgia, serif">']
    out.append(f'<rect x="{xmin:.2f}" y="{ymin:.2f}" width="{W:.2f}" '
               f'height="{H:.2f}" fill="#14110d"/>')
    tf = (f'<g transform="translate(0,{ysum:.3f}) scale(1,-1)">'
          if flip_y else '<g>')
    out.append(tf)
    for (x, y) in allp:
        out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{margin:.3f}" '
                   f'fill="none" stroke="#463c28" stroke-width="0.6"/>')
    out.append(f'<path d="{path_d(curves)}" fill="#caa24a" fill-opacity="0.10" '
               f'stroke="#e8c46a" stroke-width="2.4" stroke-linejoin="round"/>')
    # control handles: anchor -> out-control, and next-anchor -> in-control
    for seg in curves:
        A0, P1, P2, A3 = seg
        out.append(f'<line x1="{A0[0]:.3f}" y1="{A0[1]:.3f}" '
                   f'x2="{P1[0]:.3f}" y2="{P1[1]:.3f}" '
                   f'stroke="#5fb0e0" stroke-width="1.1"/>')
        out.append(f'<line x1="{A3[0]:.3f}" y1="{A3[1]:.3f}" '
                   f'x2="{P2[0]:.3f}" y2="{P2[1]:.3f}" '
                   f'stroke="#5fb0e0" stroke-width="1.1"/>')
    for seg in curves:
        for q in (seg[1], seg[2]):
            out.append(f'<rect x="{q[0] - 2.6:.3f}" y="{q[1] - 2.6:.3f}" '
                       f'width="5.2" height="5.2" fill="#5fb0e0"/>')
    strand_names = list(strands) if strands else []
    for si, name in enumerate(strand_names):
        c = colors[si % len(colors)]
        for (x, y) in strands[name]:
            out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3.1" fill="{c}"/>')
    if not strand_names:
        for (x, y) in allp:
            out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3.1" fill="#cf3b2d"/>')
    for seg in curves:
        out.append(f'<circle cx="{seg[0][0]:.3f}" cy="{seg[0][1]:.3f}" '
                   f'r="5.0" fill="#14110d" stroke="#f4e3b0" stroke-width="2"/>')
    out.append('</g>')
    # upright node numbers
    out.append('<g font-size="22" font-weight="600" fill="#f4e3b0">')
    for i, seg in enumerate(curves):
        x, y = seg[0]
        v = np.array([x, y]) - cen
        v = v / (np.hypot(*v) + 1e-9)
        lx, ly = x + v[0] * 22, y + v[1] * 22
        sy = (ysum - ly) if flip_y else ly
        out.append(f'<text x="{lx:.2f}" y="{sy + 7:.2f}" '
                   f'text-anchor="middle">{i}</text>')
    out.append('</g>')
    lx, ly = xmin + 16, ymin + 30
    out.append('<g font-size="20">')
    out.append(f'<text x="{lx}" y="{ly}" fill="#f4e3b0">'
               f'{len(curves)}-node closed Bezier &#183; area {area:,.0f} mm&#178; '
               f'&#183; min clearance {margin:g} mm</text>')
    out.append('</g></svg>')
    open(path, "w").write("\n".join(out))


# ===========================================================================
# Driver
# ===========================================================================

def solve(allp, strands, margin, n_nodes, base="auto", safety=0.05,
          symmetric=True, verbose=True, fixed_anchors=None, start_pt=None,
          circle_anchors=None, perimeter=False, fixed_angles=None,
          free_nodes=None):
    fixed_angles = fixed_angles or {}
    free_nodes = set(free_nodes or ())   # excluded from perimeter auto-home (stay free anchors)
    # All interior validity checks use margin+safety so that the *true*
    # (continuous) curve clears `margin` despite polygon-sampling error.
    eff = margin + safety
    point_geoms = np.array([Point(p) for p in allp], dtype=object)
    candidates = {}
    pin = strands.get("pin")
    sharp = strands.get("sharp")
    if base in ("ribbon", "auto") and pin and sharp:
        candidates["ribbon"] = Polygon(pin + sharp[::-1])
    hull = Polygon(allp).convex_hull
    if base in ("hull", "auto") or not candidates:
        candidates["hull"] = hull

    best = None
    for name, poly in candidates.items():
        if not poly.is_valid or poly.area == 0:
            continue
        if verbose:
            print(f"[base: {name}]  raw area={poly.area:.0f}")
        cv, a, d, K = best_initial_fit(poly, point_geoms, eff, n_nodes,
                                       symmetric=symmetric, verbose=verbose)
        if verbose:
            print(f"  best fit: area={a:.0f}  d*={d:.2f}  K={K}")
        if best is None or a < best[1]:
            best = (cv, a, name, poly)

    cv, _, name, poly = best
    if start_pt is not None:                # rotate FIRST so node 0 = nearest start, then the
        sx, sy = start_pt                   # fixed-anchor indices refer to this (user) numbering
        k = min(range(len(cv)),
                key=lambda i: (cv[i][0][0]-sx)**2 + (cv[i][0][1]-sy)**2)
        cv = cv[k:] + cv[:k]
        if verbose:
            print(f"rotated numbering: node 0 -> anchor nearest ({sx:.1f},{sy:.1f})")
    # 1) polish UNCONSTRAINED to the tight base curve first
    if verbose:
        print(f"[polish from base '{name}', "
              f"{'symmetric' if symmetric else 'asymmetric'} handles]")
    cen = np.array(curve_polygon(cv, 200).centroid.coords[0])
    cv = polish(cv, point_geoms, cen, eff, n_nodes, symmetric=symmetric,
                fixed=frozenset(), fixed_angles=fixed_angles, verbose=verbose)
    # 2) pin the requested anchors (small moves off the tight curve) + short repair polish
    fixed = frozenset((fixed_anchors or {}).keys())
    if fixed_anchors:
        A, phi, lin, lout = _to_params(cv)
        L = 0.5 * (lin + lout)
        for idx, (x, y) in fixed_anchors.items():
            A[idx % n_nodes] = np.array([x, y], float)
        cv = _build(A, phi, L, L) if symmetric else _build(A, phi, lin, lout)
        if verbose:
            print(f"[pinned anchors: " + ", ".join(f"N{i}=({x:.1f},{y:.1f})"
                  for i, (x, y) in fixed_anchors.items()) + "]")
        cv = polish(cv, point_geoms, cen, eff, n_nodes, symmetric=symmetric,
                    fixed=fixed, fixed_angles=fixed_angles, max_iters=40,
                    verbose=verbose)
    # 3) circle-constrained anchors. Every constrained node slides on the eff-radius circle of a
    # "home" dot: explicit homes from circle_anchors; in --perimeter mode every other node auto-
    # homes onto its NEAREST dot, so all nodes end up sitting one air gap from some pin/sharp.
    if circle_anchors or perimeter:
        circle = {}
        A, phi, lin, lout = _to_params(cv)
        L = 0.5 * (lin + lout)
        fixed_centers = {idx % n_nodes: (cx, cy) for idx, (cx, cy) in (circle_anchors or {}).items()}
        pts_arr = np.array(allp, float)
        for i in range(n_nodes):
            if i in free_nodes:                # left free: polish moves it to hug what binds
                continue
            if i in fixed_centers:
                cx, cy = fixed_centers[i]
            elif perimeter:
                j = int(((pts_arr - A[i]) ** 2).sum(1).argmin())   # nearest dot = this node's home
                cx, cy = pts_arr[j]
            else:
                continue
            v = A[i] - np.array([cx, cy]); nn = np.hypot(*v) or 1.0
            A[i] = np.array([cx, cy]) + v / nn * eff               # project node onto its eff circle
            circle[i] = (cx, cy, eff)
        cv = _build(A, phi, L, L) if symmetric else _build(A, phi, lin, lout)
        if verbose:
            print(f"[on-circle: {len(circle)} nodes on dot perimeters (r={eff:.2f}); "
                  f"fixed homes {sorted(fixed_centers)}]")
        cv = polish(cv, point_geoms, cen, eff, n_nodes, symmetric=symmetric,
                    circle=circle, fixed_angles=fixed_angles, max_iters=80,
                    verbose=verbose)
    return cv, name


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="input CSV of points")
    ap.add_argument("--margin", type=float, default=13.0,
                    help="minimum clearance (default 13)")
    ap.add_argument("--nodes", type=int, default=8,
                    help="number of on-curve Bezier nodes (default 8)")
    ap.add_argument("--xcol", default="x")
    ap.add_argument("--ycol", default="z")
    ap.add_argument("--base", choices=["auto", "ribbon", "hull"], default="auto")
    ap.add_argument("--handles", choices=["symmetric", "asymmetric"],
                    default="symmetric",
                    help="node handles: symmetric=equal-length mirror (default), "
                         "asymmetric=collinear but independent lengths (tighter)")
    ap.add_argument("--safety", type=float, default=0.05,
                    help="interior clearance safety epsilon, mm (default 0.05)")
    ap.add_argument("-o", "--out", default="wrap.svg")
    ap.add_argument("--fix", default="",
                    help="pin anchors to fixed positions: 'idx:x,y;idx:x,y' "
                         "(e.g. '4:540.152,-717.584;7:-106.26,-184.653')")
    ap.add_argument("--start", default="",
                    help="rotate node numbering so node 0 is the node nearest 'x,y'")
    ap.add_argument("--oncircle", default="",
                    help="constrain anchors to the eff-radius circle of a dot, angle free: "
                         "'idx:cx,cy;idx:cx,cy' (node slides around that dot's clearance circle)")
    ap.add_argument("--angle", default="",
                    help="pin a node's tangent angle (degrees, z-up frame), not optimized: "
                         "'idx:deg;idx:deg' (e.g. '1:-45')")
    ap.add_argument("--perimeter", action="store_true",
                    help="put EVERY node on a dot's clearance circle: --oncircle gives fixed "
                         "homes, the rest auto-home onto their nearest dot")
    ap.add_argument("--free", default="",
                    help="comma-separated node indices left FREE (not perimeter-homed); the "
                         "area polish presses them against whatever binds (e.g. '4' for the G7 cap)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    circle_anchors = {}
    if args.oncircle:
        for part in args.oncircle.split(";"):
            idx, xy = part.split(":"); cx, cy = xy.split(",")
            circle_anchors[int(idx)] = (float(cx), float(cy))

    fixed_angles = {}
    if args.angle:
        for part in args.angle.split(";"):
            idx, deg = part.split(":")
            fixed_angles[int(idx)] = math.radians(float(deg))

    free_nodes = set()
    if args.free:
        free_nodes = {int(v) for v in args.free.split(",") if v.strip() != ""}

    fixed_anchors = {}
    if args.fix:
        for part in args.fix.split(";"):
            idx, xy = part.split(":"); x, y = xy.split(",")
            fixed_anchors[int(idx)] = (float(x), float(y))

    allp, strands = load_points(args.csv, args.xcol, args.ycol)
    verbose = not args.quiet
    print(f"Loaded {len(allp)} points"
          + (f" ({', '.join(f'{k}:{len(v)}' for k, v in strands.items())})"
             if strands else ""))

    start_pt = None
    if args.start:
        sx, sy = (float(v) for v in args.start.split(","))
        start_pt = (sx, sy)

    curves, base = solve(allp, strands, args.margin, args.nodes, args.base,
                         args.safety, args.handles == "symmetric", verbose,
                         fixed_anchors=fixed_anchors, start_pt=start_pt,
                         circle_anchors=circle_anchors, perimeter=args.perimeter,
                         fixed_angles=fixed_angles, free_nodes=free_nodes)

    area = curve_polygon(curves, 400).area
    clr = exact_min_clearance(curves, allp)
    pg = np.array([Point(p) for p in allp], dtype=object)
    inside_ok = bool(shapely.contains(curve_polygon(curves, 400), pg).all())

    print("\n=== result ===")
    print(f"base shape        : {base}")
    print(f"handles           : {args.handles}")
    print(f"nodes / segments  : {len(curves)}")
    print(f"all points inside : {inside_ok}")
    print(f"exact min clear   : {clr:.4f} mm  (target {args.margin:g})")
    print(f"enclosed area     : {area:,.0f} mm^2")

    write_svg(args.out, curves, strands, allp, args.margin, area)
    print(f"\nWrote {args.out}")

    print("\nControl points (anchor, out-handle, in-handle-of-next):")
    for i, seg in enumerate(curves):
        print(f"  N{i}: A=({seg[0][0]:9.3f},{seg[0][1]:9.3f})  "
              f"H+=({seg[1][0]:9.3f},{seg[1][1]:9.3f})  "
              f"H-=({seg[2][0]:9.3f},{seg[2][1]:9.3f})")
    print("\nSVG path d-string:")
    print(path_d(curves))


if __name__ == "__main__":
    main()
