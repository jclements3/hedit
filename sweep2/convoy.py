"""
convoy.py  --  Lamination lanes for the Clements 49 (red/green band fill).

Produces N non-crossing "convoy" lanes between the red (outer) and green (inner)
rails of frame.svg. The recommended method is a DTW correspondence loft; an older
station-based loft is kept for cases that need authored seams.

WHAT WE LEARNED (read this)
---------------------------
The hard part was never "stations" - it was the CORRESPONDENCE: which green point
pairs with which red point.

  * Pairing by ARC LENGTH skews where the rails are non-parallel (the crown: red
    ~4800 long, green ~4200, different paths). That skew is what tangles a global
    loft (17 crossings) and what hand-picked stations were patching piecewise.
  * Pairing by DTW (dynamic time warping: match the curves to each other) removes
    the skew GLOBALLY. A single DTW loft, NO stations, gives 0 crossings with even,
    smooth spacing - matching the hand-picked result. So stations are NOT required
    for a valid lamination.
  * Orientation IS required but auto-detects: red and green are authored in
    opposite senses, so green is reversed (co_orient tries both, keeps the better).
  * The green self-intersection is irrelevant; the algorithm never inspects it.

WHEN YOU STILL WANT STATIONS
----------------------------
Only for an AUTHORED SEAM the geometry doesn't imply - a lane boundary the
instrument requires at a brace, rib, or acoustic node. That is a design decision,
not derivable from the curves. build_convoy(..., stations=[...]) supports it.
propose_stations() will suggest geometric cuts (RDP best in testing) as a
confirmable superset, but a finder can never invent a seam that isn't a bend.

ITERATIONS:  iter n -> 2**n - 1 lanes at f = k/2**n.
  DTW: iter1/2/3 -> 0 crossings; iter4 (15 lanes) -> see __main__ printout.
PINCH: the reunion notch may still pinch the innermost lanes at high iteration -
  a topological spacing limit, independent of correspondence or stations.

DEPENDENCIES: numpy, shapely, svgpathtools.
"""

import numpy as np
from shapely.geometry import LineString

# ----- authored crosswalks (only used by the optional station path) -----
FLOOR, BASE, PILLAR, CROWN = 1920.6178, 1846.7, 368.2, 229.4

# --------------------------------------------------------------------------- #
#  CORE                                                                        #
# --------------------------------------------------------------------------- #
def resample(P, n):
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    si = np.linspace(0, s[-1], n)
    return np.c_[np.interp(si, s, P[:, 0]), np.interp(si, s, P[:, 1])]

def loft(R, G, f):
    return (1 - f) * R + f * G

def _crossings(R, G):
    n = len(R)
    lanes = [loft(R, G, k / 4) for k in (1, 2, 3)]
    L = [LineString(P) for P in lanes]
    return sum(1 for i in range(3) for j in range(i + 1, 3) if L[i].crosses(L[j]))

def co_orient(red, green, n=400):
    """Orient green to co-traverse the band with red. Try both senses on a DTW
    loft; keep the one with fewer mid-lane crossings. (Clements -> reversed.)"""
    R = resample(red, n)
    best, choice = None, green
    for G0 in (green, green[::-1]):
        G = resample(G0, n)
        c = _crossings(R, G[dtw_map(R, G)])
        if best is None or c < best:
            best, choice = c, G0
    return choice

def dtw_map(A, B):
    """Monotone DTW alignment index map A_i -> B_j (position cost)."""
    n, m = len(A), len(B)
    D = np.full((n + 1, m + 1), 1e18); D[0, 0] = 0.0
    for i in range(1, n + 1):
        c = np.hypot(A[i - 1, 0] - B[:, 0], A[i - 1, 1] - B[:, 1])
        D[i, 1:] = c + np.minimum(np.minimum(D[i - 1, 1:], D[i, :-1]), D[i - 1, :-1])
    i, j = n, m; mp = {}
    while i > 0 and j > 0:
        mp[i - 1] = j - 1
        s = np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]])
        i, j = [(i - 1, j - 1), (i - 1, j), (i, j - 1)][s]
    return np.maximum.accumulate(np.array([mp.get(k, 0) for k in range(n)]))

def correspondence(red, green, n=500):
    """Return (R, Gp): n red samples and their DTW-matched green partners."""
    green = co_orient(red, green)
    R = resample(red, n); G = resample(green, n)
    return R, G[dtw_map(R, G)]

# --------------------------------------------------------------------------- #
#  BUILD                                                                       #
# --------------------------------------------------------------------------- #
def build_convoy(red, green, iteration=3, stations=None, n=500):
    """2**iteration - 1 lanes between red and green.

    stations=None  -> DTW correspondence loft (recommended; no cuts needed).
    stations=[...]  -> authored seams: red arc-fractions in (0,1) at which to force
                       a lane boundary; each station lofts on DTW-matched partners.
    """
    R, Gp = correspondence(red, green, n)
    M = 2 ** iteration - 1
    if not stations:
        return [loft(R, Gp, k / 2 ** iteration) for k in range(1, M + 1)]
    # authored seams: split the DTW-paired arrays at the cuts and loft each piece
    # WITHOUT resampling (resampling would break the pairing and reintroduce skew).
    # Geometry is identical to the no-station loft; the cuts just mark seam nodes.
    cuts = sorted({0, n - 1} | {int(round(s * (n - 1))) for s in stations})
    lanes = []
    for k in range(1, M + 1):
        f = k / 2 ** iteration
        pieces = [loft(R[a:b + 1], Gp[a:b + 1], f) for a, b in zip(cuts[:-1], cuts[1:])]
        lanes.append(np.vstack([pieces[0]] + [p[1:] for p in pieces[1:]]))
    return lanes

def count_crossings(lanes):
    L = [LineString(P) for P in lanes]
    hits = [(i + 1, j + 1) for i in range(len(L)) for j in range(i + 1, len(L))
            if L[i].crosses(L[j])]
    return len(hits), hits

# --------------------------------------------------------------------------- #
#  STATION PROPOSERS (suggest a confirmable superset; never authoritative)     #
# --------------------------------------------------------------------------- #
def propose_stations(red, method="rdp", n=600):
    """Return red arc-fractions in (0,1) where a geometric cut is suggested.
    Tested ranking on this harp: rdp > curvature > divergence. None finds the
    pillar reliably (it is not a bend) and none finds authored seams."""
    R = resample(red, n)
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(R, axis=0), axis=1))]; s /= s[-1]
    from scipy.signal import find_peaks
    if method == "rdp":
        def rdp(P, eps, off=0):
            if len(P) < 3: return []
            a, b = P[0], P[-1]; ab = b - a; L = np.hypot(*ab) + 1e-9
            d = np.abs((ab[0]) * (a[1] - P[:, 1]) - (ab[1]) * (a[0] - P[:, 0])) / L
            i = int(np.argmax(d))
            if d[i] > eps:
                return rdp(P[:i + 1], eps, off) + [off + i] + rdp(P[i:], eps, off + i)
            return []
        idx = sorted(set(rdp(R, 18)))
        return [s[i] for i in idx if 0 < i < n - 1]
    if method == "curvature":
        d1 = np.gradient(R, axis=0); d2 = np.gradient(d1, axis=0)
        k = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / ((d1[:, 0]**2 + d1[:, 1]**2)**1.5 + 1e-9)
        k = np.convolve(k, np.ones(7) / 7, "same")
        pk, _ = find_peaks(k, distance=30, height=np.percentile(k, 80))
        return [s[i] for i in pk]
    raise ValueError(method)

# --------------------------------------------------------------------------- #
#  IO                                                                          #
# --------------------------------------------------------------------------- #
def load_rails(svg_path, red_id="red_curve", green_id="green_curve", samples=1200):
    """Dense polylines for red/green via core._flatten (canonical; svgpathtools not required)."""
    import re, core
    svg=open(svg_path).read()
    def poly(idv):
        i=svg.index('id="%s"'%idv); ps=svg.rfind('<path',0,i)
        pe=svg.index('/>',i) if '/>' in svg[i:i+9000] else svg.index('>',i)
        d=re.search(r'\sd="([^"]*)"',svg[ps:pe]).group(1)
        P=core._flatten(d); return resample(P, samples)
    return poly(red_id), poly(green_id)

def lanes_to_svg(lanes, red, green, path_out):
    def d(P): return "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in P)
    body  = f'<path d="{d(red)}" fill="none" stroke="#f00" stroke-width="2"/>\n'
    body += f'<path d="{d(green)}" fill="none" stroke="#0a0" stroke-width="2"/>\n'
    body += "".join(f'<path d="{d(P)}" fill="none" stroke="#1d4ed8" stroke-width="1.3"/>\n'
                    for P in lanes)
    xs = np.r_[red[:, 0], green[:, 0]]; ys = np.r_[red[:, 1], green[:, 1]]
    vb = f"{xs.min()-20:.0f} {ys.min()-20:.0f} {xs.ptp()+40:.0f} {ys.ptp()+40:.0f}"
    open(path_out, "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n{body}</svg>\n')

if __name__ == "__main__":
    import sys
    svg = sys.argv[1] if len(sys.argv) > 1 else "frame.svg"
    red, green = load_rails(svg)
    print("DTW correspondence loft (no stations):")
    for it in (1, 2, 3, 4):
        lanes = build_convoy(red, green, iteration=it)
        n, hits = count_crossings(lanes)
        print(f"  iter {it}: {len(lanes):2d} lanes, {n} crossings", hits[:6])
    lanes = build_convoy(red, green, iteration=3)
    lanes_to_svg(lanes, red, green, "convoy_iter3.svg")
    print("wrote convoy_iter3.svg")
    print("proposed RDP stations (arc-fractions):",
          [round(x, 3) for x in propose_stations(red, "rdp")])
