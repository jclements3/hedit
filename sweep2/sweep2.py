"""
sweep2.py — rebuilt frame-driving layer for the Clements 49 sweep.

Same section families, same authored anchors, same green backbone. Replaces ONLY
the parts diagnosed broken in the legacy _frame_rings:

  1. FIELD FILTERING   h(s), c(s): ray-cast hits are validity-filtered (misses,
     grazing spikes) and rebuilt as smooth interpolants over arc length.
     -> kills the st0-6 fallback-constant rings and the st7-12 graze wobble.
  2. SMOOTHED TANGENTS gaussian-smoothed spine for tangent/normal computation
     (origins stay exactly on green).  -> kills tilt-noise amplification.
  3. TILT-LIMITED PLANES per-station plane rotation capped at step/reach so
     adjacent section planes can never intersect inside the material.
     -> kills the shoulder-corner and neck-bend ring collisions (the fans).
  4. PHASE-LOCKED ROSE  rose vertex order follows material (spin), aligned once
     at the crown; no per-station apex re-roll.  -> lanes corkscrew continuously,
     zero index snaps.
"""
import numpy as np
import core
from shapely.geometry import Polygon

FLOOR = core.FLOOR
ROSE_TURNS = core.ROSE_TURNS


def _gauss_smooth(P, sigma=1.5, half=4):
    k = np.exp(-0.5 * (np.arange(-half, half + 1) / sigma) ** 2)
    k /= k.sum()
    out = np.copy(P).astype(float)
    for c in range(P.shape[1]):
        pad = np.r_[[P[0, c]] * half, P[:, c], [P[-1, c]] * half]
        out[:, c] = np.convolve(pad, k, "valid")
    return out


def _field(vals, s, spike=3.0):
    """Validity-filter a ray-cast scalar field and rebuild as a smooth interpolant."""
    v = np.array([np.nan if (x is None or x < 10) else float(x) for x in vals])
    ok = ~np.isnan(v)
    if ok.sum() >= 4:                                   # grazing-spike filter
        med = np.nanmedian(np.abs(np.diff(v[ok])))
        idx = np.where(ok)[0]
        for a, b in zip(idx[:-1], idx[1:]):
            if abs(v[b] - v[a]) > spike * max(med, 1.0) * (b - a):
                v[b] = np.nan
        ok = ~np.isnan(v)
    f = np.interp(s, s[ok], v[ok])                      # fill + extrapolate (edge-hold)
    # linear extrapolation at the ends from the nearest valid trend
    i0, i1 = np.where(ok)[0][0], np.where(ok)[0][-1]
    if i0 > 0:
        j = min(i0 + 6, i1)
        sl = (f[j] - f[i0]) / (s[j] - s[i0] + 1e-9)
        f[:i0] = f[i0] + sl * (s[:i0] - s[i0])
    if i1 < len(s) - 1:
        j = max(i1 - 6, i0)
        sl = (f[i1] - f[j]) / (s[i1] - s[j] + 1e-9)
        f[i1 + 1:] = f[i1] + sl * (s[i1 + 1:] - s[i1])
    # light 3-tap smooth
    g = np.copy(f)
    g[1:-1] = 0.25 * f[:-2] + 0.5 * f[1:-1] + 0.25 * f[2:]
    return np.maximum(g, 10.0)


def build(svg_path="frame.svg", anchors=None, P=None):
    P = dict(core.PARAMS, **(P or {}))
    S, M = P["S"], P["M"]
    green, red, blue = core.load_frame(svg_path)
    if P.get("TRIM_Z") is not None:                     # wishbone: drop the crossed floor tails
        z = FLOOR - green[:, 1]
        a = 0
        while a < len(green) // 2 and z[a] < P["TRIM_Z"]: a += 1
        b = len(green) - 1
        while b > len(green) // 2 and z[b] < P["TRIM_Z"]: b -= 1
        green = green[a:b + 1]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(green, axis=0).T))]
    us = np.linspace(0, seg[-1], S)
    spine = np.c_[np.interp(us, seg, green[:, 0]), np.interp(us, seg, green[:, 1])]
    sm = _gauss_smooth(spine)                            # tangents only
    step = seg[-1] / (S - 1)

    # ---- anchors (authored, picker spec) ----
    def snap(a):
        return int(np.argmin(np.hypot(spine[:, 0] - a["x"], spine[:, 1] - a["y"])))
    if anchors:
        arc1 = us[snap(anchors["sh_in"])]; arc3 = us[snap(anchors["sh_out"])]
        crown_i = snap(anchors["cr_out"]); CROWN_WIN = max(crown_i - snap(anchors["cr_in"]), 1)
    else:
        ip = int(np.argmin(np.hypot(spine[:, 0] - 963., spine[:, 1] - 560.)))
        arc1 = us[max(ip - 1, 0)]; arc3 = us[min(ip + 1, S - 1)]
        apex_i = int(np.argmin(spine[:, 1]))
        crown_i = apex_i + 20; CROWN_WIN = 8

    # ---- raw normal angles from smoothed tangents, sign-propagated ----
    T = np.gradient(sm, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    Nraw = np.c_[-T[:, 1], T[:, 0]]
    cen = np.array([400., 900.])
    if (spine[S // 4] - cen) @ Nraw[S // 4] < 0:
        Nraw = -Nraw
    for i in range(1, S):
        if Nraw[i] @ Nraw[i - 1] < 0:
            Nraw[i] = -Nraw[i]
    phi = np.unwrap(np.arctan2(Nraw[:, 1], Nraw[:, 0]))

    # ---- provisional fields on raw normals (for reach estimate) ----
    def cast(i, ang):
        n = np.array([np.cos(ang), np.sin(ang)])
        return (core._frame_rings.__globals__, n)  # unused; placeholder guard
    def fh(p, d, poly):
        best = None
        for k in range(len(poly) - 1):
            a = poly[k]; b = poly[k + 1]; e = b - a
            den = d[0] * (-e[1]) - d[1] * (-e[0])
            if abs(den) < 1e-9:
                continue
            r = a - p
            t = (r[0] * (-e[1]) - r[1] * (-e[0])) / den
            u = (d[0] * r[1] - d[1] * r[0]) / den
            if 0 <= u <= 1 and t > 1e-3 and (best is None or t < best):
                best = t
        return best
    h0 = _field([fh(spine[i], Nraw[i], red) for i in range(S)], us)

    # ---- tilt-limited plane propagation (cap dphi at step/reach) ----
    ph = np.copy(phi); hc = np.copy(h0)
    for outer in range(3):                               # cap-field consistency loop
        for _ in range(6):                               # iterated fwd/bwd clamping
            for i in range(1, S):
                cap = 0.7 * step / max(hc[i], 40.0)
                ph[i] = ph[i - 1] + np.clip(ph[i] - ph[i - 1], -cap, cap)
            for i in range(S - 2, -1, -1):
                cap = 0.7 * step / max(hc[i], 40.0)
                ph[i] = ph[i + 1] + np.clip(ph[i] - ph[i + 1], -cap, cap)
        Nc = np.c_[np.cos(ph), np.sin(ph)]
        hc = _field([fh(spine[i], Nc[i], red) for i in range(S)], us)
    N = np.c_[np.cos(ph), np.sin(ph)]

    # ---- final fields on the limited normals ----
    h = _field([fh(spine[i], N[i], red) for i in range(S)], us)
    # BLUE: DTW-correspondence-gated ray-cast (blue tails cross like green's;
    # nearest-hit mates the wrong branch near the floor — GREEN_ORIENTATION.md).
    def blue_candidates(i):
        p = spine[i]; d = N[i]; out = []
        for k in range(len(blue) - 1):
            a = blue[k]; b2 = blue[k + 1]; e = b2 - a
            den = d[0] * (-e[1]) - d[1] * (-e[0])
            if abs(den) < 1e-9: continue
            rr = a - p
            t = (rr[0] * (-e[1]) - rr[1] * (-e[0])) / den
            u2 = (d[0] * rr[1] - d[1] * rr[0]) / den
            if 0 <= u2 <= 1 and 3.0 < t < h[i] * 0.98:
                out.append(t)
        return sorted(out)[:4]
    cand = [blue_candidates(i) for i in range(S)]
    # Viterbi: pick one candidate per station minimizing total |c_i - c_{i-1}|
    INF = 1e18
    prev_cost = {j: 0.0 for j in range(len(cand[0]))} or {0: 0.0}
    back = []
    if not cand[0]:
        prev_cost = {-1: 0.0}
    for i in range(1, S):
        cc = {}; bk = {}
        cur = cand[i] if cand[i] else [None]
        for j, tj in enumerate(cur):
            best = (INF, -1)
            for pj, pc in prev_cost.items():
                tp = cand[i - 1][pj] if (pj >= 0 and cand[i - 1]) else None
                step = 0.0 if (tj is None or tp is None) else abs(tj - tp)
                if pc + step < best[0]: best = (pc + step, pj)
            cc[j if cur[0] is not None else -1] = best[0]
            bk[j if cur[0] is not None else -1] = best[1]
        prev_cost = cc; back.append(bk)
    j = min(prev_cost, key=prev_cost.get)
    sel = [None] * S; sel[S - 1] = j
    for i in range(S - 2, -1, -1):
        j = back[i][j]; sel[i] = j
    vals = [cand[i][sel[i]] if (sel[i] is not None and sel[i] >= 0 and cand[i]) else None for i in range(S)]
    c = _field(vals, us)

    # ---- g / width machinery (same as legacy, anchored) ----
    i1 = int(np.argmin(np.abs(us - arc1)))
    g1 = float(np.clip(2 * c[i1] / h[i1], 0.05, 0.49))
    def gv(s, hh, cc):
        # BLUE-DRIVEN everywhere (CODE_VERIFIED fix): c = spine->blue is the single
        # inner scalar for limaçon dimple, U arch height, and neck legs alike.
        if s < arc1:
            return float(np.clip(2 * cc / hh, 0.03, 0.49))
        if s <= arc3:
            return float(np.clip(2 * cc / hh, g1, 1.0))
        return float(np.clip(2 * cc / hh, 0.55, 1.0))
    ext1 = core.limacon(g1, h[i1] / 4); W1 = np.ptp(ext1[:, 0])
    ifl = int(np.argmin(np.abs(FLOOR - spine[:, 1])))
    bf = h[ifl] / 4
    W_out = np.ptp(core._curve(2.0, bf)[:, 0])
    ub = [i for i in range(S) if us[i] > arc3]
    n0 = np.array([251.243, 1781.29])
    ic = min(ub, key=lambda i: np.hypot(*(spine[i] - n0)))
    sc, se = us[ic], us[-1]

    _sb = [spine[i, 1] for i in range(S) if us[i] < arc1]
    ymin, ymax = (min(_sb), max(_sb)) if _sb else (0., 1.)

    rings, bores, fam = [], [], []
    r_lock = None
    for i in range(S):
        s = us[i]; hh = h[i]; cc = c[i]; b = hh / 4
        g = gv(s, hh, cc)
        o = np.array([spine[i, 0], 0., FLOOR - spine[i, 1]])
        v = np.array([N[i, 0], 0., -N[i, 1]]); u = np.array([0., 1., 0.])
        bore2 = None
        if s < arc1:
            ext = core.limacon(g, b); f = 0
        elif s <= arc3:
            ext = core.opened(g, b)
            nat = np.ptp(ext[:, 0]); tw = W1 + (P["PLATE_OUT"] - W1) * (s - arc1) / (arc3 - arc1)
            if nat > 1e-6: ext[:, 0] *= tw / nat
            f = 1
        elif i < crown_i - CROWN_WIN:
            ext = core.opened(g, b)
            nat = np.ptp(ext[:, 0]); tt = min(max((s - sc) / (se - sc), 0), 1) if se > sc else 0
            tw = P["PLATE_OUT"] + (W_out - P["PLATE_OUT"]) * tt
            if nat > 1e-6: ext[:, 0] *= tw / nat
            f = 2
        elif i < crown_i:
            t = (i - (crown_i - CROWN_WIN)) / float(CROWN_WIN); t = t * t * (3 - 2 * t)
            eU = core.opened(g, b)
            nat = np.ptp(eU[:, 0]); tt = min(max((s - sc) / (se - sc), 0), 1) if se > sc else 0
            tw = P["PLATE_OUT"] + (W_out - P["PLATE_OUT"]) * tt
            if nat > 1e-6: eU[:, 0] *= tw / nat
            th = np.linspace(0, 2 * np.pi, M, endpoint=False)
            fl = (3 + 0.4 * np.sin(12 * th)) / 3.4
            eR = np.c_[(hh / 2) * fl * np.cos(th), hh / 2 + (hh / 2) * fl * np.sin(th)]
            eU = core._resample(core._roll(eU), M); eR = core._resample(core._roll(eR), M)
            ext = (1 - t) * eU + t * eR
            f = 3
        else:
            spin = ROSE_TURNS * 2 * np.pi * (i - crown_i) / max(S - 1 - crown_i, 1)
            th = np.linspace(0, 2 * np.pi, M, endpoint=False) + spin
            fl = (3 + 0.4 * np.sin(12 * th)) / 3.4
            ext = np.c_[(hh / 2) * fl * np.cos(th), hh / 2 + (hh / 2) * fl * np.sin(th)]
            rD = P.get("BORE_D") or cc                  # cylinder: ONE authored scalar
            rb = np.c_[(rD / 2) * np.cos(th), hh / 2 + (rD / 2) * np.sin(th)]
            bore2 = rb
            f = 4
        fam.append(f)
        if f < 4:
            ext = core._roll(ext)
            R2 = core._resample(ext, M)
        else:
            R2 = ext                                     # material order (helix)
            if r_lock is None:                           # align ONCE to the previous ring
                prev = rings[-1]
                loc = np.c_[(prev - o) @ u, (prev - o) @ v]  # back to section plane
                cand = np.array([o + q[1] * v + q[0] * u for q in R2])
                costs = [np.linalg.norm(np.roll(cand, r, axis=0) - prev, axis=1).mean() for r in range(M)]
                r_lock = int(np.argmin(costs))
            R2 = np.roll(R2, r_lock, axis=0)
            if bore2 is not None:
                bore2 = np.roll(core._resample(bore2, M) if len(bore2) != M else bore2, r_lock, axis=0)
        # bores
        if f == 4 and bore2 is not None:
            bores.append(np.array([o + q[1] * v + q[0] * u for q in bore2]))
        elif s < arc1:
            tau = min(max((spine[i, 1] - ymin) / (ymax - ymin + 1e-9), 0.), 1.)
            iw = core._variable_bore(ext, 1.5 + 2.5 * tau, 2.5, 2.5 + 1.0 * tau)
            bores.append(np.array([o + q[1] * v + q[0] * u for q in core._resample(iw, M)]))
        elif f == 3:
            # crown morph: blend inner wall buffer->circle with the same smoothstep
            t = (i - (crown_i - CROWN_WIN)) / float(CROWN_WIN); t = t * t * (3 - 2 * t)
            crown = float(np.clip(2 * g * b, 2.0, 0.42 * min(np.ptp(ext[:, 0]), np.ptp(ext[:, 1]) + 1e-9)))
            poly = Polygon(ext)
            if not poly.is_valid: poly = poly.buffer(0)
            inn = poly.buffer(-crown, join_style="round")
            if inn.is_empty: inn = poly.buffer(-0.5 * crown, join_style="round")
            if getattr(inn, "geom_type", "") == "MultiPolygon":
                inn = max(inn.geoms, key=lambda gg: gg.area)
            iwU = np.array(inn.exterior.coords) if (not inn.is_empty and inn.area > 1e-6) else ext.mean(0) + 0.6 * (ext - ext.mean(0))
            thc = np.linspace(0, 2 * np.pi, M, endpoint=False)
            rD = P.get("BORE_D") or cc
            circ = np.c_[(rD / 2) * np.cos(thc), hh / 2 + (rD / 2) * np.sin(thc)]
            bw = (1 - t) * core._resample(core._roll(iwU), M) + t * core._resample(core._roll(circ), M)
            bores.append(np.array([o + q[1] * v + q[0] * u for q in bw]))
        else:
            crown = float(np.clip(2 * g * b, 2.0, 0.42 * min(np.ptp(ext[:, 0]), np.ptp(ext[:, 1]) + 1e-9)))
            poly = Polygon(ext)
            if not poly.is_valid: poly = poly.buffer(0)
            inn = poly.buffer(-crown, join_style="round")
            if inn.is_empty: inn = poly.buffer(-0.5 * crown, join_style="round")
            if getattr(inn, "geom_type", "") == "MultiPolygon":
                inn = max(inn.geoms, key=lambda gg: gg.area)
            iw = np.array(inn.exterior.coords) if (not inn.is_empty and inn.area > 1e-6) else ext.mean(0) + 0.6 * (ext - ext.mean(0))
            iw = core._roll(iw)                          # stable apex anchor -> bore lanes stay aligned
            bores.append(np.array([o + q[1] * v + q[0] * u for q in core._resample(iw, M)]))
        rings.append(np.array([o + q[1] * v + q[0] * u for q in R2]))
    meta = dict(arc1=arc1, arc3=arc3, crown_i=crown_i, CROWN_WIN=CROWN_WIN, fam=fam,
                h=h, c=c, phi_raw=phi, phi_lim=ph)
    return rings, bores, meta


def _fit_lobe(lobe, F, Mn):
    """Register a 2D authored lobe onto formula ring F (world, near-flat):
    translation + uniform scale + reflection/180 choice + cyclic/direction alignment.
    Returns the fitted flat ring (Mn,3) at z=0 and the applied scale."""
    Fxy = F[:, :2]
    Fc = Fxy.mean(0)
    def area(P):
        Q = np.vstack([P, P[:1]])
        return 0.5 * abs(np.sum(Q[:-1, 0] * Q[1:, 1] - Q[1:, 0] * Q[:-1, 1]))
    L = lobe - lobe.mean(0)
    sc = np.sqrt(max(area(Fxy - Fc), 1.0) / max(area(L), 1.0))
    Ft = core._resample(Fxy - Fc, Mn)
    best = None
    for T in (np.diag([1., 1.]), np.diag([-1., 1.]), np.diag([1., -1.]), np.diag([-1., -1.])):
        for rev in (False, True):
            C = (L[::-1] if rev else L) @ T.T * sc
            Cr = core._resample(C, Mn)
            d = np.linalg.norm(Ft, axis=1)  # noqa
            costs = [np.linalg.norm(np.roll(Cr, r, axis=0) - Ft, axis=1).mean() for r in range(Mn)]
            k = int(np.argmin(costs))
            if best is None or costs[k] < best[0]:
                best = (costs[k], np.roll(Cr, k, axis=0))
    fitted = best[1] + Fc
    return np.c_[fitted, np.zeros(Mn)], sc, best[0]


def anchor_floor(rings, base_svg, K=3):
    """Ring-0 (and ring-end) anchoring to the authored floor: station 0 = soundbox
    lobe of base.svg flat at z=0, station S-1 = rose lobe; displacement-blended
    into the formula over K stations. Per HANDOFF: base is canonical, formula
    takes over by station ~1-2."""
    import re
    svg = open(base_svg).read()
    def load(idv):
        i = svg.index('id="%s"' % idv); ps = svg.rfind('<path', 0, i)
        pe = svg.index('/>', i) if '/>' in svg[i:i + 12000] else svg.index('>', i)
        return core._flatten(re.search(r'\sd="([^"]*)"', svg[ps:pe]).group(1))
    red = load("red_outer")
    def split(P, xs, keep):
        side = (P[:, 0] > xs) if keep == 'right' else (P[:, 0] < xs)
        idx = np.where(side)[0]
        runs, cur = [], [idx[0]]
        for a, b in zip(idx[:-1], idx[1:]):
            if b == a + 1: cur.append(b)
            else: runs.append(cur); cur = [b]
        runs.append(cur)
        if side[0] and side[-1] and len(runs) > 1:
            runs[0] = runs[-1] + runs[0]; runs.pop()
        run = max(runs, key=len); L = P[run]
        return np.vstack([L, [[xs, L[-1][1]], [xs, L[0][1]]]])
    A = split(red, 80.0, 'right')          # soundbox lobe
    B = split(red, 80.0, 'left')           # rose lobe
    Mn = len(rings[0]); S = len(rings)
    R0, scA, eA = _fit_lobe(A, rings[0], Mn)
    R1, scB, eB = _fit_lobe(B, rings[-1], Mn)
    out = [np.copy(r) for r in rings]
    D0 = R0 - rings[0]
    D1 = R1 - rings[-1]
    for k in range(K + 1):
        w = (k / K); w = w * w * (3 - 2 * w)             # 0 at anchor -> 1 at K
        out[k] = rings[k] + (1 - w) * D0
        out[S - 1 - k] = rings[S - 1 - k] + (1 - w) * D1
    return out, dict(scale_A=scA, scale_B=scB, fit_err_A=eA, fit_err_B=eB)


def anchor_floor_exact(rings, base_svg, spine_z, Z_RE=130.0):
    """EXACT authored floor: base.svg placed 1:1 (rigid: mirror/rotate + translate,
    NO scaling). Station 0 mouth = soundbox lobe, station S-1 mouth = rose lobe,
    both open flat at z=0. Each arm grows independently from its lobe to the
    formula section over the base region (spine z < Z_RE = reunion height)."""
    import re
    svg = open(base_svg).read()
    def load(idv):
        i = svg.index('id="%s"' % idv); ps = svg.rfind('<path', 0, i)
        pe = svg.index('/>', i) if '/>' in svg[i:i + 12000] else svg.index('>', i)
        return core._flatten(re.search(r'\sd="([^"]*)"', svg[ps:pe]).group(1))
    red = load("red_outer")
    def split(P, xs, keep):
        side = (P[:, 0] > xs) if keep == 'right' else (P[:, 0] < xs)
        idx = np.where(side)[0]
        runs, cur = [], [idx[0]]
        for a, b in zip(idx[:-1], idx[1:]):
            if b == a + 1: cur.append(b)
            else: runs.append(cur); cur = [b]
        runs.append(cur)
        if side[0] and side[-1] and len(runs) > 1:
            runs[0] = runs[-1] + runs[0]; runs.pop()
        run = max(runs, key=len); L = P[run]
        return np.vstack([L, [[xs, L[-1][1]], [xs, L[0][1]]]])
    A = split(red, 80.0, 'right')                       # soundbox lobe (authored)
    B = split(red, 80.0, 'left')                        # rose lobe (authored)
    S = len(rings); Mn = len(rings[0])
    fA = rings[0][:, :2].mean(0)                        # world feet (x,y)
    fB = rings[-1][:, :2].mean(0)
    cA = A.mean(0); cB = B.mean(0)
    best = None
    for T in (np.diag([1., 1.]), np.diag([-1., 1.]), np.diag([1., -1.]), np.diag([-1., -1.])):
        a = A @ T.T; b = B @ T.T
        ca = a.mean(0); cb = b.mean(0)
        # single rigid translation for the WHOLE footprint: match midpoints,
        # score by both lobe-centroid errors (footprint stays exactly authored)
        t = 0.5 * (fA + fB) - 0.5 * (ca + cb)
        err = np.linalg.norm(ca + t - fA) + np.linalg.norm(cb + t - fB)
        if best is None or err < best[0]:
            best = (err, T, t)
    err, T, t = best
    A2 = A @ T.T + t; B2 = B @ T.T + t
    Ai2 = Ai @ T.T + t; Bi2 = Bi @ T.T + t
    def ring0(L2, F):
        C = core._resample(L2, Mn)
        Ft = F[:, :2]
        costs = [np.linalg.norm(np.roll(C, r, axis=0) - Ft, axis=1).mean() for r in range(Mn)]
        costs_r = [np.linalg.norm(np.roll(C[::-1], r, axis=0) - Ft, axis=1).mean() for r in range(Mn)]
        if min(costs_r) < min(costs):
            C = C[::-1]; costs = costs_r
        C = np.roll(C, int(np.argmin(costs)), axis=0)
        return np.c_[C, np.zeros(Mn)]
    R0 = ring0(A2, rings[0]); R1 = ring0(B2, rings[-1])
    KA = max(1, sum(1 for z in spine_z if z < Z_RE and list(spine_z).index(z) < S // 2))
    KA = 1
    while KA < S // 2 and spine_z[KA] < Z_RE: KA += 1
    KB = 1
    while KB < S // 2 and spine_z[S - 1 - KB] < Z_RE: KB += 1
    out = [np.copy(r) for r in rings]
    D0 = R0 - rings[0]; D1 = R1 - rings[-1]
    for k in range(KA + 1):
        w = k / KA; w = w * w * (3 - 2 * w)
        out[k] = rings[k] + (1 - w) * D0
    for k in range(KB + 1):
        w = k / KB; w = w * w * (3 - 2 * w)
        out[S - 1 - k] = rings[S - 1 - k] + (1 - w) * D1
    return out, dict(placement_err=err, mirror=T.tolist(), shift=t.tolist(), KA=KA, KB=KB)


def _plane_basis(F):
    """Basis of a ring plane containing u=(0,1,0): returns (c, e2) with e2 in xz."""
    c = F.mean(0)
    Q = F - c
    # strip the y-component, take dominant xz direction
    xz = Q[:, [0, 2]]
    k = int(np.argmax((xz ** 2).sum(1)))
    e = xz[k] / (np.linalg.norm(xz[k]) + 1e-12)
    return c, np.array([e[0], 0., e[1]])


def anchor_floor_launch(rings, base_svg, spine_z, Z_L=130.0):
    """Vertical launch: floor mouths = exact 1:1 base.svg lobes flat at z=0; each
    arm rises VERTICALLY off its mouth, bending to meet the untouched formula
    sweep at the top of the launch zone (spine z > Z_L). Center path = quadratic
    bezier with vertical takeoff; plane tilts horizontal->formula; shape morphs
    mouth->formula. Both mouths open (no caps)."""
    import re
    svg = open(base_svg).read()
    def load(idv):
        i = svg.index('id="%s"' % idv); ps = svg.rfind('<path', 0, i)
        pe = svg.index('/>', i) if '/>' in svg[i:i + 12000] else svg.index('>', i)
        return core._flatten(re.search(r'\sd="([^"]*)"', svg[ps:pe]).group(1))
    red = load("red_outer")
    def split(P, xs, keep):
        side = (P[:, 0] > xs) if keep == 'right' else (P[:, 0] < xs)
        idx = np.where(side)[0]
        runs, cur = [], [idx[0]]
        for a, b in zip(idx[:-1], idx[1:]):
            if b == a + 1: cur.append(b)
            else: runs.append(cur); cur = [b]
        runs.append(cur)
        if side[0] and side[-1] and len(runs) > 1:
            runs[0] = runs[-1] + runs[0]; runs.pop()
        run = max(runs, key=len); L = P[run]
        return np.vstack([L, [[xs, L[-1][1]], [xs, L[0][1]]]])
    A = split(red, 80.0, 'right'); B = split(red, 80.0, 'left')
    S = len(rings); Mn = len(rings[0])
    # rigid 1:1 placement of the whole footprint (mirror/rotate + translate, no scale)
    fA = rings[0][:, :2].mean(0); fB = rings[-1][:, :2].mean(0)
    best = None
    for T in (np.diag([1., 1.]), np.diag([-1., 1.]), np.diag([1., -1.]), np.diag([-1., -1.])):
        a = A @ T.T; b = B @ T.T
        t = 0.5 * (fA + fB) - 0.5 * (a.mean(0) + b.mean(0))
        err = np.linalg.norm(a.mean(0) + t - fA) + np.linalg.norm(b.mean(0) + t - fB)
        if best is None or err < best[0]:
            best = (err, T, t)
    err, T, t = best
    A2 = A @ T.T + t; B2 = B @ T.T + t
    Ai2 = Ai @ T.T + t; Bi2 = Bi @ T.T + t
    out = [np.copy(r) for r in rings]

    def launch(lobe, end):
        # stations inside the launch zone, measured from this end
        K = 1
        idx = (lambda k: k) if end == 0 else (lambda k: S - 1 - k)
        while K < S // 2 and spine_z[idx(K)] < Z_L: K += 1
        FK = rings[idx(K)]                              # first untouched formula ring
        cK, e2 = _plane_basis(FK)
        f2 = np.c_[(FK - cK) @ np.array([0., 1., 0.]), (FK - cK) @ e2]   # formula 2D
        m0 = np.array([lobe.mean(0)[0], lobe.mean(0)[1], zm])            # mouth center
        a2 = np.array([np.sign(e2[0]) if abs(e2[0]) > 1e-6 else 1., 0., 0.])  # horizontal
        L2 = core._resample(lobe - lobe.mean(0), Mn)                     # mouth 2D (x,y)
        # mouth 2D in (b1=y, b2=horizontal) frame: coords = (y, sgn*x)
        mo = np.c_[L2[:, 1], L2[:, 0] * np.sign(a2[0])]
        # align to formula 2D (direction + cyclic roll)
        costs = [np.linalg.norm(np.roll(mo, r, axis=0) - f2, axis=1).mean() for r in range(Mn)]
        costs_r = [np.linalg.norm(np.roll(mo[::-1], r, axis=0) - f2, axis=1).mean() for r in range(Mn)]
        if min(costs_r) < min(costs):
            mo = mo[::-1]; costs = costs_r
        mo = np.roll(mo, int(np.argmin(costs)), axis=0)
        # bezier center path with vertical takeoff
        ctrl = np.array([m0[0], m0[1], max(cK[2] * 0.75, 20.0)])
        ang_e2 = np.arctan2(e2[2], e2[0]); ang_a2 = np.arctan2(0., a2[0])
        d_ang = (ang_e2 - ang_a2 + np.pi) % (2 * np.pi) - np.pi
        b1 = np.array([0., 1., 0.])
        for k in range(K):                              # k=K stays formula
            u = k / K
            C = (1 - u) ** 2 * m0 + 2 * (1 - u) * u * ctrl + u ** 2 * cK
            w = u * u * (3 - 2 * u)
            ang = ang_a2 + w * d_ang
            b2 = np.array([np.cos(ang), 0., np.sin(ang)])
            sh = (1 - w) * mo + w * f2
            out[idx(k)] = C + sh[:, :1] * b1 + sh[:, 1:2] * b2
        return K
    KA = launch(A2, 0)
    KB = launch(B2, S - 1)
    return out, dict(placement_err=err, KA=KA, KB=KB)


def assert_green_orientation(svg_path="frame.svg"):
    """THE FOUR-MONTH INVARIANT — never determine arm identity from the floor.
    green START = SOUNDBOX foot: the curve climbs the string diagonal and reaches
      the shoulder (~968,545) at ~38%% arc.
    green END = PILLAR foot: the last ~1.4 m runs the vertical column x~203.
    The floor TAILS CROSS: each green endpoint lands beside the OTHER arm's red
    foot. Proximity pairing at the floor is therefore ALWAYS WRONG."""
    g, _, _ = core.load_frame(svg_path)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(g, axis=0).T))]
    def at(s):
        return np.array([np.interp(s, seg, g[:, 0]), np.interp(s, seg, g[:, 1])])
    p = at(0.376 * seg[-1])
    assert np.hypot(p[0] - 968., p[1] - 545.) < 60., \
        "GREEN SWAPPED: start side does not climb to the shoulder — start must be the SOUNDBOX foot"
    xs = [at(seg[-1] - s)[0] for s in (400, 800, 1200)]
    assert max(xs) - min(xs) < 25. and abs(np.mean(xs) - 203.) < 40., \
        "GREEN SWAPPED: end side is not the vertical pillar column"
    return True


def wishbone(svg_path="frame.svg", base_svg="base.svg", anchors=None, Z_TRIM=130.0, NL=8, P=None):
    assert_green_orientation(svg_path)
    """The wishbone sweep: green tails (which cross at the floor) are discarded;
    the formula sweep runs only above Z_TRIM; each arm then launches vertically
    from its own authored base.svg lobe (exact 1:1, flat z=0, open mouth) up to
    its trimmed end. Union of the two mouths = the authored footprint."""
    import re
    svg = open(base_svg).read()
    import re as _re
    def _load0(idv):
        i = svg.index('id="%s"' % idv); ps = svg.rfind('<path', 0, i)
        pe = svg.index('/>', i) if '/>' in svg[i:i + 12000] else svg.index('>', i)
        return core._flatten(_re.search(r'\sd="([^"]*)"', svg[ps:pe]).group(1))
    from scipy.optimize import least_squares as _lsq
    _bp = _load0("blue_outer"); _bp = _bp[_bp[:, 0] < 68]
    _bcx, _bcy, _bR = _lsq(lambda q: np.hypot(*(_bp - q[:2]).T) - q[2],
                           [_bp[:, 0].mean(), _bp[:, 1].mean(), 25]).x
    rings, bores, meta = build(svg_path, anchors=anchors,
                               P=dict(P or {}, TRIM_Z=Z_TRIM, BORE_D=2 * _bR))
    S = len(rings); Mn = len(rings[0])
    def load(idv):
        i = svg.index('id="%s"' % idv); ps = svg.rfind('<path', 0, i)
        pe = svg.index('/>', i) if '/>' in svg[i:i + 12000] else svg.index('>', i)
        return core._flatten(re.search(r'\sd="([^"]*)"', svg[ps:pe]).group(1))
    red = load("red_outer")
    blue_f = load("blue_outer")
    # BOOLEAN-JOIN model: the footprint is the union of two SEPARATE complete
    # shapes. Reconstruct the full 12-flute rose and full c=2 limaçon by fitting
    # their visible arcs of red_outer (authored shapes are never edited).
    from scipy.optimize import least_squares
    rp = red[red[:, 0] < 68]; lp = red[red[:, 0] > 96]
    def rres(q):
        cx, cy, R, p = q
        d = rp - [cx, cy]; r = np.hypot(d[:, 0], d[:, 1]); th = np.arctan2(d[:, 1], d[:, 0])
        return r - R * (3 + 0.4 * np.sin(12 * th + p)) / 3.4
    cx, cy, Rr, phs = least_squares(rres, [rp[:, 0].mean(), rp[:, 1].mean(), 30, 0]).x
    def lres(q):
        px, py, b, t0 = q
        d = lp - [px, py]; r = np.hypot(d[:, 0], d[:, 1]); th = np.arctan2(d[:, 1], d[:, 0])
        return r - b * (2 + np.cos(th - t0))
    px, py, bb, t0 = least_squares(lres, [lp[:, 0].mean(), lp[:, 1].mean(), 15, np.pi]).x
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    B = np.c_[cx + Rr * (3 + 0.4 * np.sin(12 * th + phs)) / 3.4 * np.cos(th),
              cy + Rr * (3 + 0.4 * np.sin(12 * th + phs)) / 3.4 * np.sin(th)]   # FULL rose
    A = np.c_[px + bb * (2 + np.cos(th - t0)) * np.cos(th),
              py + bb * (2 + np.cos(th - t0)) * np.sin(th)]                     # FULL limaçon
    # INNER wall (the blue system): rose bore = plain circle, inner limaçon — fitted to blue_outer
    bpts = blue_f[blue_f[:, 0] < 68]; lpts = blue_f[blue_f[:, 0] > 96]
    def cres(q):
        d = bpts - [q[0], q[1]]; return np.hypot(d[:, 0], d[:, 1]) - q[2]
    bcx, bcy, bR = least_squares(cres, [bpts[:, 0].mean(), bpts[:, 1].mean(), 25]).x
    def ires(q):
        d = lpts - [q[0], q[1]]; r = np.hypot(d[:, 0], d[:, 1]); a = np.arctan2(d[:, 1], d[:, 0])
        return r - q[2] * (q[3] + np.cos(a - q[4]))
    ipx, ipy, ib, ic, it0 = least_squares(ires, [lpts[:, 0].mean(), lpts[:, 1].mean(), 15, 2.0, np.pi]).x
    Bi = np.c_[bcx + bR * np.cos(th), bcy + bR * np.sin(th)]                    # bore circle
    Ai = np.c_[ipx + ib * (ic + np.cos(th - it0)) * np.cos(th),
               ipy + ib * (ic + np.cos(th - it0)) * np.sin(th)]                 # inner limaçon
    fA = rings[0][:, :2].mean(0); fB = rings[-1][:, :2].mean(0)
    best = None
    for T in (np.diag([1., 1.]), np.diag([-1., 1.]), np.diag([1., -1.]), np.diag([-1., -1.])):
        a = A @ T.T; b = B @ T.T
        t = fB - b.mean(0)                              # PIN the rose lobe under the pillar
        e = np.linalg.norm(a.mean(0) + t - fA)          # score by soundbox mismatch only
        if best is None or e < best[0]: best = (e, T, t)
    err, T, t = best
    A2 = A @ T.T + t; B2 = B @ T.T + t
    Ai2 = Ai @ T.T + t; Bi2 = Bi @ T.T + t

    def launch(lobe, F, zm=0.0, align_phase=False):
        cK, e2 = _plane_basis(F)
        f2raw = np.c_[(F - cK) @ np.array([0., 1., 0.]), (F - cK) @ e2]
        cf = f2raw.mean(0)
        aF = np.arctan2(f2raw[:, 1] - cf[1], f2raw[:, 0] - cf[0])
        aU = np.unwrap(aF)                               # monotone vertex angles of F
        sgn = 1.0 if aU[-1] > aU[0] else -1.0
        grid = aU[0] + sgn * 2 * np.pi * np.arange(Mn) / Mn   # uniform, same start/direction
        rF = np.hypot(f2raw[:, 0] - cf[0], f2raw[:, 1] - cf[1])
        m0 = np.array([lobe.mean(0)[0], lobe.mean(0)[1], zm])
        a2s = np.sign(e2[0]) if abs(e2[0]) > 1e-6 else 1.
        L2 = lobe - lobe.mean(0)
        mo2 = np.c_[L2[:, 1], L2[:, 0] * a2s]
        if align_phase:                                  # rotate 12-fold mouth to match F's flutes
            thq = np.linspace(-np.pi, np.pi, 360, endpoint=False)
            aT = np.arctan2(mo2[:, 1], mo2[:, 0]); rT = np.hypot(mo2[:, 0], mo2[:, 1])
            oT = np.argsort(aT)
            rMp = np.interp(thq, np.r_[aT[oT] - 2 * np.pi, aT[oT], aT[oT] + 2 * np.pi],
                            np.r_[rT[oT], rT[oT], rT[oT]])
            aFq = np.arctan2(f2raw[:, 1] - cf[1], f2raw[:, 0] - cf[0])
            rFq = np.hypot(f2raw[:, 0] - cf[0], f2raw[:, 1] - cf[1])
            oQ = np.argsort(aFq)
            rFp = np.interp(thq, np.r_[aFq[oQ] - 2 * np.pi, aFq[oQ], aFq[oQ] + 2 * np.pi],
                            np.r_[rFq[oQ], rFq[oQ], rFq[oQ]])
            best = max(range(30), key=lambda d: np.dot(np.roll(rMp, d), rFp))  # within one flute
            rot = thq[best] - thq[0]
            ca_, sa_ = np.cos(rot), np.sin(rot)
            mo2 = mo2 @ np.array([[ca_, -sa_], [sa_, ca_]]).T
        aM = np.arctan2(mo2[:, 1], mo2[:, 0]); rM = np.hypot(mo2[:, 0], mo2[:, 1])
        oM = np.argsort(aM); aMs = aM[oM]; rMs = rM[oM]
        aMs = np.r_[aMs - 2 * np.pi, aMs, aMs + 2 * np.pi]; rMs = np.r_[rMs, rMs, rMs]
        def r_mouth(th):
            return np.interp((th + np.pi) % (2 * np.pi) - np.pi, aMs, rMs)
        aFs2 = np.r_[np.sort(((aF + np.pi) % (2 * np.pi)) - np.pi)]
        oF = np.argsort(((aF + np.pi) % (2 * np.pi)) - np.pi)
        aFs = (((aF + np.pi) % (2 * np.pi)) - np.pi)[oF]; rFs = rF[oF]
        aFs = np.r_[aFs - 2 * np.pi, aFs, aFs + 2 * np.pi]; rFs = np.r_[rFs, rFs, rFs]
        def r_form(th):
            return np.interp((th + np.pi) % (2 * np.pi) - np.pi, aFs, rFs)
        ctrl = np.array([m0[0], m0[1], zm + 0.75 * (cK[2] - zm)])
        ang_e2 = np.arctan2(e2[2], e2[0]); ang_a2 = np.arctan2(0., a2s)
        d_ang = (ang_e2 - ang_a2 + np.pi) % (2 * np.pi) - np.pi
        b1 = np.array([0., 1., 0.])
        seq = []
        for k in range(NL):                              # k=NL would equal F exactly
            u = k / NL
            C = (1 - u) ** 2 * m0 + 2 * (1 - u) * u * ctrl + u ** 2 * cK
            w = u * u * (3 - 2 * u)
            th = (1 - w) * grid + w * aU                 # vertex angles morph uniform -> F's own
            rr = (1 - w) * r_mouth(th) + w * r_form(th)
            cx2 = w * cf[0]; cy2 = w * cf[1]             # centroid offset morphs in
            x2 = cx2 + rr * np.cos(th); y2 = cy2 + rr * np.sin(th)
            ang = ang_a2 + w * d_ang
            b2 = np.array([np.cos(ang), 0., np.sin(ang)])
            ring = C + x2[:, None] * b1 + y2[:, None] * b2
            tgt = w * max(float(F[:, 2].min()), 0.0)     # underside schedule: 0 -> F floor
            ring[:, 2] += tgt - ring[:, 2].min()
            seq.append(ring)
        return seq
    # lateral easing: pull each sweep end to sit directly above its lobe center,
    # decaying over EASE stations so the upper sweep is untouched
    EASE_A = 30                                      # long gentle drift, soundbox only
    dA = np.r_[A2.mean(0) - rings[0][:, :2].mean(0), 0.0]
    for k in range(min(EASE_A, S)):
        w = 1 - k / EASE_A; w = w * w * (3 - 2 * w)
        rings[k] = rings[k] + w * dA
        if bores[k] is not None: bores[k] = bores[k] + w * dA
    # pillar: rose lobe is pinned under the column -> NO easing, column stays straight
    # green-crossing height = the reunion: the base merges into the arms HERE
    gfull, _, _ = core.load_frame(svg_path)
    ZM = 69.2
    for i in range(len(gfull) - 1):
        for j in range(i + 3, len(gfull) - 1):
            A1, B1, C1, D1 = gfull[i], gfull[i + 1], gfull[j], gfull[j + 1]
            d1 = B1 - A1; d2 = D1 - C1
            den = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(den) < 1e-9: continue
            tt = ((C1[0] - A1[0]) * d2[1] - (C1[1] - A1[1]) * d2[0]) / den
            uu = ((C1[0] - A1[0]) * d1[1] - (C1[1] - A1[1]) * d1[0]) / den
            if 0 <= tt <= 1 and 0 <= uu <= 1 and (A1 + tt * d1)[1] > 1700:
                ZM = float(FLOOR - (A1 + tt * d1)[1])
    upA = launch(A2, rings[0], zm=0.0)
    upB = launch(B2, rings[-1], zm=0.0, align_phase=True)
    biA = launch(Ai2, bores[0], zm=0.0)
    biB = launch(Bi2, bores[-1], zm=0.0)
    out = upA + rings + upB[::-1]
    bout = biA + bores + biB[::-1]
    # BASE OBJECT: hollow shell, no green — outer = red_outer union outline,
    # inner = blue_outer, rising vertically z=0 -> ZM where it merges into the arms
    redT = red @ T.T + t
    bluT = blue_f @ T.T + t
    NB = 6
    base_o = []; base_i = []
    Ro2 = core._resample(redT, Mn); Bi2r = core._resample(bluT, Mn)
    for k in range(NB):
        zk = ZM * k / (NB - 1)
        base_o.append(np.c_[Ro2, np.full(Mn, zk)])
        base_i.append(np.c_[Bi2r, np.full(Mn, zk)])
    fam = [meta["fam"][0]] * NL + meta["fam"] + [meta["fam"][-1]] * NL
    # bore lane continuity: align successive bore rings by cyclic roll outside the
    # rose; apply ONE constant roll to the whole rose block (keeps the helix
    # phase-lock while joining cleanly at the crown).
    def _br(Aq, Bq, w=20):
        costs = [np.linalg.norm(Aq - np.roll(Bq, r, axis=0), axis=1).mean() for r in range(-w, w + 1)]
        return int(np.argmin(costs)) - w
    i = 1
    while i < len(bout):
        if fam[i] == 4 and fam[i - 1] != 4:              # entering the rose: constant roll for the block
            r = _br(bout[i - 1], bout[i])
            j = i
            while j < len(bout) and fam[j] == 4:
                bout[j] = np.roll(bout[j], r, axis=0); j += 1
            i = j
        else:
            if fam[i] != 4:
                r = _br(bout[i - 1], bout[i])
                if r: bout[i] = np.roll(bout[i], r, axis=0)
            i += 1
    sh_z = [i for i, f in enumerate(fam) if f == 1]
    cr_z = [i for i, f in enumerate(fam) if f == 3]
    zones = []
    if sh_z:
        za, zb = max(min(sh_z) - 6, 1), min(max(sh_z) + 6, len(bout) - 2)
        bout = smooth_bores(bout, fam, [(za, zb)], iters=22)          # smooth SHAPES
        Acb = bout[za].mean(0); Bcb = bout[zb].mean(0)                # straighten the PATH
        AB = Bcb - Acb; AB /= np.linalg.norm(AB) + 1e-12
        for i in range(za + 1, zb):
            cbi = bout[i].mean(0)
            tgt = Acb + ((cbi - Acb) @ AB) * AB
            w = np.sin(np.pi * (i - za) / (zb - za))                  # full pull mid-zone, 0 at ends
            bout[i] = bout[i] + w * (tgt - cbi)
        bout = enforce_wall(bout, out, range(max(za - 2, 1), min(zb + 8, len(bout) - 1)), wmin=4.4, iters=6)
        bout = enforce_wall(bout, out, range(max(za - 2, 1), min(zb + 8, len(bout) - 1)), wmin=4.4, iters=6)
    if cr_z: zones.append((min(cr_z) - 3, max(cr_z) + 4))
    if zones: bout = smooth_bores(bout, fam, zones, iters=5)
    # outer fairing: same shoulder/crown zones (authored mouths + rose flutes untouched)
    if zones: out = smooth_bores(out, fam, zones, iters=4)
    nz = [i for i, f in enumerate(fam) if f != 4]
    out = smooth_bores(out, fam, [(nz[0] + 1, nz[-1])], iters=1)      # gentle global fairing
    bout = smooth_bores(bout, fam, [(nz[0] + 1, nz[-1])], iters=1)
    out = [np.c_[rg[:, 0], rg[:, 1], np.maximum(rg[:, 2], 0.0)] for rg in out]
    bout = [np.c_[rg[:, 0], rg[:, 1], np.maximum(rg[:, 2], 0.0)] for rg in bout]
    meta2 = dict(meta, fam=fam, NL=NL, placement_err=err, S=len(out), ZM=ZM)
    return out, bout, (base_o, base_i), meta2


def _polar(sh2, Mn):
    """Resample a closed 2D shape at Mn uniform angles about its centroid
    (angle-locked correspondence: blending two polar-resampled shapes cannot swirl)."""
    c = sh2.mean(0)
    d = sh2 - c
    th = np.arctan2(d[:, 1], d[:, 0])
    r = np.hypot(d[:, 0], d[:, 1])
    o = np.argsort(th)
    th = th[o]; r = r[o]
    th = np.r_[th - 2 * np.pi, th, th + 2 * np.pi]
    r = np.r_[r, r, r]
    q = np.linspace(-np.pi, np.pi, Mn, endpoint=False)
    rq = np.interp(q, th, r)
    return np.c_[c[0] + rq * np.cos(q), c[1] + rq * np.sin(q)]


def smooth_bores(bout, fam, zones, iters=4):
    """Laplacian smoothing of bore rings along the station axis inside the given
    station zones (rings are index-aligned, so per-vertex smoothing is valid)."""
    B = [np.copy(b) for b in bout]
    idx = sorted(set(i for a, b in zones for i in range(max(a, 1), min(b, len(B) - 1))))
    for _ in range(iters):
        new = {i: 0.25 * B[i - 1] + 0.5 * B[i] + 0.25 * B[i + 1] for i in idx}
        for i, v in new.items():
            B[i] = v
    return B


def enforce_wall(bout, out, idx, wmin=4.0, iters=3):
    """Push bore vertices inward wherever the outer<->bore wall is thinner than
    wmin (structural minimum), within the given station indices."""
    from shapely.geometry import Polygon, Point
    from shapely.ops import nearest_points
    B = [np.copy(b) for b in bout]
    for i in idx:
        O = np.asarray(out[i]); c = O.mean(0); Q = O - c
        _, _, vt = np.linalg.svd(Q, full_matrices=False)
        e1, e2 = vt[0], vt[1]
        po = Polygon(np.c_[Q @ e1, Q @ e2]).buffer(0)
        shr = po.buffer(-wmin)
        if shr.is_empty:
            shr = po.buffer(-0.4 * wmin)
            if shr.is_empty: continue
        if shr.geom_type == "MultiPolygon":
            shr = max(shr.geoms, key=lambda g: g.area)
        b2 = np.c_[(B[i] - c) @ e1, (B[i] - c) @ e2]
        nrm = (B[i] - c) - np.outer(b2[:, 0], e1) - np.outer(b2[:, 1], e2)  # off-plane part
        moved = False
        for k in range(len(b2)):
            p = Point(b2[k])
            if not shr.contains(p):
                q = nearest_points(shr, p)[0]
                b2[k] = [q.x, q.y]; moved = True
        if moved:
            B[i] = c + np.outer(b2[:, 0], e1) + np.outer(b2[:, 1], e2) + nrm
    return B


def wishbone_spec(spec, svg_path="frame.svg", base_svg="base.svg"):
    """Build from a full harp_spec dict (see harp_spec.json). Every knob that was
    ever a discussion is a key here; unknown keys are ignored, missing keys take
    the approved 2026-07-17 defaults."""
    import json
    if isinstance(spec, str):
        spec = json.load(open(spec))
    w = spec.get("windows", {})
    anchors = {k: w[k] for k in ("sh_in", "sh_out", "cr_in", "cr_out") if k in w} or None
    ln = spec.get("launch", {})
    ba = spec.get("base", {})
    ro = spec.get("rose", {})
    st = spec.get("structure", {})
    sa = spec.get("sampling", {})
    global _SPEC
    _SPEC = dict(
        ease=int(ln.get("soundbox_ease_stations", 30)),
        ctrl=float(ln.get("ctrl_height_frac", 0.75)),
        flat=bool(ln.get("flat_underside", True)),
        phase=bool(ln.get("rose_phase_align", True)),
        wall=float(st.get("wall_min_shoulder", 4.4)),
        sh_mode=st.get("shoulder_blue", "straight_path"),
        sh_half=int(st.get("shoulder_zone_halfwidth", 6)),
        sh_iters=int(st.get("shoulder_smooth_iters", 22)),
        cr_pad=int(st.get("crown_zone_pad", 3)),
        cr_iters=int(st.get("crown_smooth_iters", 5)),
        out_iters=int(st.get("outer_zone_smooth_iters", 4)),
        fair=int(st.get("global_fair_iters", 1)),
        nb=int(ba.get("base_stations", 6)),
    )
    P = {"S": int(sa.get("S", 160)), "M": int(sa.get("M", 90))}
    if isinstance(ro.get("bore_diameter"), (int, float)):
        P["BORE_D"] = float(ro["bore_diameter"])
    return wishbone(svg_path, base_svg, anchors=anchors,
                    Z_TRIM=float(ba.get("trim_z", 130.0)),
                    NL=int(ln.get("stations", 8)), P=P)
