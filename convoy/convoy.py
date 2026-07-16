"""
convoy.py -- Lamination lanes for the Clements 49 (red/green band fill).

VENDORED into hedit/convoy/ from ~/Downloads/clements49_convoy_handoff.zip.
Exactly two adaptations, both marked "VENDOR ADAPTATION" at their site:
  1. _flatten (:116) -- the `from core import _flatten` try/except is DELETED;
     _flatten_local is the sole parser. core.py's tokenizer mis-parses H/V.
  2. smooth_closed() -- ADDED; circular [1,2,1]/4 binomial for closed lanes.
     NOT USED by lanes_dp_bp.py -- the measured HF residual does not warrant it.
Everything else -- dtw_map, loft, resample, correspondence, build_convoy,
count_crossings -- is byte-faithful to the handoff. In particular the mean-j
per-run anti-truncation (:194-196) and the endpoint taper (:208-214) are the
fixes for the truncation bug that "0 crossings" never revealed. Do not touch.

Note this module's red/green vocabulary: in hedit's use (lanes_dp_bp.py) red=BP
(bulge/outer) and green=DP (dimple/inner), and both rails are CLOSED loops cut
at a seam. See seam.py and README.md.

Produces N non-crossing "convoy" lanes between the red (outer) and green
(soundboard/inner) rails of frame.svg. See example_harp_frame.py for a runnable
demo that reproduces the canonical convoy figure.

    import convoy
    red, green = convoy.load_rails("frame.svg")
    lanes = convoy.build_convoy(red, green, iteration=3)   # 7 lanes
    convoy.count_crossings(lanes)                          # (0, [])


THE ONE LESSON
--------------
The hard part was never "stations" -- it was the CORRESPONDENCE: which green point
pairs with which red point.

  * ARC-LENGTH pairing skews where the rails are non-parallel (at the crown red runs
    ~4800 long, green ~4200, on different paths). Equal-s points stop sitting across
    the band, so a global loft tangles: 17 crossings. Hand-picked stations were
    patching that skew piecewise.
  * DTW pairing (dynamic time warping -- match the curves to each other) removes the
    skew GLOBALLY. One DTW loft, NO stations: 0 crossings through iteration 3, with
    perfectly even spacing (exact by construction) and smoothness matching the
    hand-stationed build (max turn 33.7 deg vs 32.5 -- both at the soundbox corner,
    which is real geometry).

So stations are NOT required for a valid lamination. They are required only for an
AUTHORED SEAM the geometry cannot imply (a brace, rib, or acoustic node). That is a
design decision -- pass it explicitly via stations=[...].

THE REUNION PINCH IS REAL (do not re-litigate)
---------------------------------------------
iter1/2/3 -> 0 crossings. iter4 (15 lanes) -> 3. iter5 (31) -> 19. All of them at the
base notch among the INNERMOST lanes: evenly-spaced lanes physically cannot nest
through the green head/tail reunion. This is a topological spacing limit, independent
of correspondence -- DTW does not dissolve it. (An earlier session claimed it did;
that was an artifact of a truncation bug, since fixed: the lanes were not reaching the
floor, so they never had to nest through the pinch.) To go past iteration 3: allow
non-uniform spacing through the notch, or merge inner lanes before it.


THREE THINGS THAT BITE (all handled here; do not "fix" them again)
-----------------------------------------------------------------
1. ORIENTATION. red and green are authored in OPPOSITE traversal senses:
       red  : pillar-foot -> UP the pillar   -> crown -> soundbox -> DOWN diagonal -> body-foot
       green: pillar-foot -> UP the diagonal -> soundbox -> crown -> DOWN pillar    -> body-foot
   Pairing them as-authored pairs red's pillar with green's diagonal (opposite sides
   of the band). co_orient() auto-detects and reverses green. No hint needed.

2. GREEN SELF-INTERSECTS -- AND IT DOES NOT MATTER. green crosses itself once near
   the base (~215,1846). The algorithm never inspects it. An earlier version split
   green into head/tail and matched feet by max-x to "handle" it -- that was an
   error born of mistaking the orientation problem for a topology problem.

3. VERIFY BY EYE, NOT BY COUNT. 0 crossings is necessary, not sufficient: a harmonic
   field also gives 0 crossings but collapses all spacing onto green; a distance
   field gives 0 but kinks at the medial axis. Always render and look.


ITERATIONS:  iteration n -> 2**n - 1 lanes at f = k / 2**n.
             iter1=1, iter2=3, iter3=7 (canonical figure -- 0 crossings), iter4=15 (3).

DEPENDENCIES: numpy, shapely. Optional: core (for the canonical _flatten parser).
"""

import numpy as np
from shapely.geometry import LineString

__all__ = ["load_rails", "co_orient", "dtw_map", "correspondence", "build_convoy",
           "count_crossings", "propose_stations", "resample", "loft",
           "lanes_to_html", "lanes_to_svg_text"]


# --------------------------------------------------------------------------- #
#  RAIL LOADING                                                                #
#  Prefers core._flatten (the canonical parser). NEVER use frame.flatten --     #
#  it has a relative-coordinate parse bug.                                      #
# --------------------------------------------------------------------------- #
def _flatten_local(d, steps=48):
    """Fallback SVG path parser: M/L/C/V/H/Z, absolute & relative.
    Mirrors core._flatten so this module runs standalone."""
    import re
    t = re.findall(r'[MmCcLlVvHhZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d)
    pts = []; i = 0; x = y = 0.0; cmd = None
    def n():
        nonlocal i
        v = float(t[i]); i += 1; return v
    while i < len(t):
        if t[i] in 'MmCcLlVvHhZz':
            cmd = t[i]; i += 1
        if cmd is None:
            i += 1; continue
        C = cmd.upper(); rel = cmd.islower()
        if C == 'M':
            a, b = n(), n(); x, y = (x + a, y + b) if (rel and pts) else (a, b)
            pts.append(np.array([x, y])); cmd = 'l' if rel else 'L'
        elif C == 'L':
            a, b = n(), n(); x, y = (x + a, y + b) if rel else (a, b); pts.append(np.array([x, y]))
        elif C == 'H':
            a = n(); x = (x + a) if rel else a; pts.append(np.array([x, y]))
        elif C == 'V':
            a = n(); y = (y + a) if rel else a; pts.append(np.array([x, y]))
        elif C == 'C':
            x1, y1, x2, y2, ex, ey = n(), n(), n(), n(), n(), n()
            if rel: x1 += x; y1 += y; x2 += x; y2 += y; ex += x; ey += y
            cur = np.array([x, y]); c1 = np.array([x1, y1]); c2 = np.array([x2, y2]); e = np.array([ex, ey])
            for s in range(1, steps + 1):
                u = s / steps
                pts.append((1-u)**3*cur + 3*(1-u)**2*u*c1 + 3*(1-u)*u**2*c2 + u**3*e)
            x, y = ex, ey
    return np.array(pts)


def _flatten(d, steps=48):
    """VENDOR ADAPTATION 1: the `from core import _flatten` try/except that used to
    live here has been REMOVED. core._flatten's tokenizer regex (core.py:31,
    `[MmCcLlZz]`) omits H/V, so it silently eats their operands as an (x,y) pair --
    `M 0,0 H 10 V 20 L 30,40` loses a point. CONVOY_ALGORITHM.md 7's "canonical
    parser; handles relative/V/H" is false. _flatten_local (above) is strictly
    stronger and is now the sole parser. The bare `except Exception` that silently
    degraded to it is gone with it.

    Barely on this project's path anyway: we read Bezier chains from JSON, not SVG.
    But leaving a known-broken import live in a fresh vendor is indefensible."""
    return _flatten_local(d, steps)


def smooth_closed(P, passes=1):
    """VENDOR ADAPTATION 2: circular [1,2,1]/4 binomial smoothing for a CLOSED lane
    (P[-1] == P[0], the seam sample duplicated).

    Lesson 1 from the 3-D convoy work (paraguayan/convoy/README.md): lofted lanes
    can carry Nyquist-frequency sawtooth from the section generator, and a [1,2,1]/4
    pass kills it while being self-limiting (moves clean regions <1mm). It would
    also cover the seam, where dtw_map's endpoint taper (:210, `t = max(4, n//50)`)
    DISABLES smoothing.

    Operates on the unique samples (P[:-1]) with wraparound, then re-closes.
    APPLY ONLY IF MEASURED HF RESIDUAL WARRANTS IT -- do not smooth reflexively.
    On this build it does NOT: lanes measure 0.079mm HF vs 0.049mm on the rails
    themselves, i.e. the lanes are as clean as their sources. Kept available and
    unit-tested (selftest.py) for when a future section generator needs it."""
    Q = np.asarray(P[:-1], float)
    for _ in range(passes):
        Q = 0.25 * np.roll(Q, 1, axis=0) + 0.5 * Q + 0.25 * np.roll(Q, -1, axis=0)
    return np.vstack([Q, Q[:1]])


def _get_d(svg, *path_ids):
    """Extract the d= of the first matching path id. Accepts legacy *_combined_path
    and re-authored *_curve ids."""
    import re
    for pid in path_ids:
        key = 'id="%s"' % pid
        if key in svg:
            i = svg.index(key)
            ps = svg.rfind('<path', 0, i)
            pe = svg.index('/>', i)
            m = re.search(r'\sd="([^"]*)"', svg[ps:pe])
            if m:
                return m.group(1)
    raise KeyError("no path id in %s" % (path_ids,))


def load_rails(svg_path="frame.svg",
               red_ids=("red_combined_path", "red_curve"),
               green_ids=("green_combined_path", "green_curve")):
    """Return (red, green) as dense polylines, parsed with core._flatten when
    available. Works on frame.svg or on a .svg.txt copy (project stores that
    disallow .svg). Blue is not needed for lane generation."""
    svg = open(svg_path).read()
    return _flatten(_get_d(svg, *red_ids)), _flatten(_get_d(svg, *green_ids))


# --------------------------------------------------------------------------- #
#  CORE                                                                        #
# --------------------------------------------------------------------------- #
def resample(P, n):
    """Arc-length resample a polyline to n points."""
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    si = np.linspace(0, s[-1], n)
    return np.c_[np.interp(si, s, P[:, 0]), np.interp(si, s, P[:, 1])]


def loft(R, G, f):
    """The lane at cross-band fraction f in [0,1]. R and G must be PAIRED."""
    return (1 - f) * R + f * G


def dtw_map(A, B, smooth=9):
    """Monotone DTW alignment A_i -> B_j (position cost). O(n*m). Returns FRACTIONAL
    indices into B (interpolate B at them; see _apply_map).

    This is the core of the method: it matches the CURVES to each other rather than
    their arc lengths, so the crown skew never arises.

    smooth: width of the moving average applied to the warp map. DTW is discrete, so
      the raw map is a STAIRCASE (runs then jumps) and those steps become visible
      kinks in the lanes -- 53.7 deg max turn on this frame, vs 33.7 deg smoothed
      (33.7 is real geometry: the soundbox corner). Smoothing does not move the
      endpoints and does not introduce crossings. Set 0 to disable."""
    n, m = len(A), len(B)
    D = np.full((n + 1, m + 1), np.inf); D[0, 0] = 0.0
    for i in range(1, n + 1):
        c = np.hypot(A[i-1, 0] - B[:, 0], A[i-1, 1] - B[:, 1])
        D[i, 1:] = c + np.minimum(np.minimum(D[i-1, 1:], D[i, :-1]), D[i-1, :-1])
    # Backtrack, collecting EVERY (i,j) on the warp path.
    i, j = n, m; pairs = []
    while i > 0 and j > 0:
        pairs.append((i-1, j-1))
        s = np.argmin([D[i-1, j-1], D[i-1, j], D[i, j-1]])
        i, j = [(i-1, j-1), (i-1, j), (i, j-1)][s]
    # DTW is many-to-many: one red point can match a RUN of green points. Take the
    # MEAN j of each run -- taking the first/last truncates the lane ends (red's last
    # point would pair with a green point well before green's end, so lanes stop short
    # of the floor). Endpoints are then anchored exactly.
    acc = {}
    for a, b in pairs:
        acc.setdefault(a, []).append(b)
    g = np.array([np.mean(acc[k]) if k in acc else np.nan for k in range(n)])
    idx = np.arange(n)
    ok = ~np.isnan(g)
    g = np.interp(idx, idx[ok], g[ok])

    if smooth and smooth > 1:
        w = int(smooth)
        s = np.convolve(g, np.ones(w) / w, "same")
        k = w // 2
        s[:k] = g[:k]; s[-k:] = g[-k:]          # convolution droops at the edges
        g = s

    # Anchor both ends of the band (red[0]<->green[0], red[-1]<->green[-1]) with a
    # short taper, so the anchor does not create a jump at the last sample.
    t = max(4, n // 50)
    ramp = np.linspace(0, 1, t)
    g[:t] = g[:t] * ramp + 0.0 * (1 - ramp)
    g[-t:] = g[-t:] * (1 - ramp) + (m - 1) * ramp
    g[0], g[-1] = 0.0, m - 1.0
    return np.maximum.accumulate(g)


def _apply_map(G, g):
    """Sample G at (possibly fractional) mapped indices g -> partners for R."""
    idx = np.arange(len(G))
    return np.c_[np.interp(g, idx, G[:, 0]), np.interp(g, idx, G[:, 1])]


def _mid_crossings(R, G):
    lanes = [loft(R, G, k / 4) for k in (1, 2, 3)]
    L = [LineString(P) for P in lanes]
    return sum(1 for a in range(3) for b in range(a + 1, 3) if L[a].crosses(L[b]))


def co_orient(red, green, n=400):
    """Orient green to CO-TRAVERSE the band with red.

    The Clements rails are authored in opposite senses, so this returns green
    reversed. Auto-detected (no hint): try both senses through a DTW loft, keep the
    one with fewer mid-lane crossings. Works for any frame."""
    R = resample(red, n)
    best, choice = None, green
    for cand in (green, green[::-1]):
        G = resample(cand, n)
        c = _mid_crossings(R, _apply_map(G, dtw_map(R, G)))
        if best is None or c < best:
            best, choice = c, cand
    return choice


def correspondence(red, green, n=500):
    """Return (R, Gp): n red samples and their DTW-matched green partners.
    R[i] pairs with Gp[i]. Orientation handled internally."""
    green = co_orient(red, green)
    R = resample(red, n); G = resample(green, n)
    return R, _apply_map(G, dtw_map(R, G))


def build_convoy(red, green, iteration=3, stations=None, n=500):
    """2**iteration - 1 lanes between red and green.

    stations=None   -> DTW correspondence loft (RECOMMENDED; no cuts needed).
    stations=[f,..] -> authored seams at red arc-fractions in (0,1). The DTW-paired
                       arrays are split at the cuts and lofted per piece WITHOUT
                       resampling (resampling would break the pairing and reintroduce
                       skew). Geometry is identical to the no-station loft; the cuts
                       only plant seam nodes. Use ONLY when the instrument dictates a
                       seam -- never to "fix" crossings.
    """
    R, Gp = correspondence(red, green, n)
    M = 2 ** iteration - 1
    if not stations:
        return [loft(R, Gp, k / 2 ** iteration) for k in range(1, M + 1)]
    cuts = sorted({0, n - 1} | {int(round(s * (n - 1))) for s in stations})
    lanes = []
    for k in range(1, M + 1):
        f = k / 2 ** iteration
        pieces = [loft(R[a:b+1], Gp[a:b+1], f) for a, b in zip(cuts[:-1], cuts[1:])]
        lanes.append(np.vstack([pieces[0]] + [p[1:] for p in pieces[1:]]))
    return lanes


def count_crossings(lanes):
    """(count, [(i,j),...]) of lane-lane crossings. 0 is necessary, not sufficient
    -- always look at the render too."""
    L = [LineString(P) for P in lanes]
    hits = [(a + 1, b + 1) for a in range(len(L)) for b in range(a + 1, len(L))
            if L[a].crosses(L[b])]
    return len(hits), hits


# --------------------------------------------------------------------------- #
#  STATION PROPOSERS -- suggest a confirmable superset; never authoritative     #
# --------------------------------------------------------------------------- #
def propose_stations(red, method="rdp", n=600, eps=18.0):
    """Red arc-fractions where a GEOMETRIC cut is suggested.

    Scored against the five hand-picked crosswalks on this harp:
      rdp       -> pillar 3px, crown 5px, soundbox 16px   (best; over-proposes ~17)
      curvature -> finds base/soundbox, MISSES pillar by 333px
    The pillar is straight, so no finder sees it -- it is closest to a STRUCTURAL cut.
    Proposals are to be confirmed by eye, never trusted blind."""
    R = resample(red, n)
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(R, axis=0), axis=1))]; s /= s[-1]
    if method == "rdp":
        def _rdp(P, eps, off=0):
            if len(P) < 3: return []
            a, b = P[0], P[-1]; ab = b - a; L = np.hypot(*ab) + 1e-9
            d = np.abs(ab[0] * (a[1] - P[:, 1]) - ab[1] * (a[0] - P[:, 0])) / L
            i = int(np.argmax(d))
            if d[i] > eps:
                return _rdp(P[:i+1], eps, off) + [off + i] + _rdp(P[i:], eps, off + i)
            return []
        return [s[i] for i in sorted(set(_rdp(R, eps))) if 0 < i < n - 1]
    if method == "curvature":
        from scipy.signal import find_peaks
        d1 = np.gradient(R, axis=0); d2 = np.gradient(d1, axis=0)
        k = np.abs(d1[:, 0]*d2[:, 1] - d1[:, 1]*d2[:, 0]) / ((d1[:, 0]**2 + d1[:, 1]**2)**1.5 + 1e-9)
        k = np.convolve(k, np.ones(7) / 7, "same")
        pk, _ = find_peaks(k, distance=30, height=np.percentile(k, 80))
        return [s[i] for i in pk]
    raise ValueError(method)


# --------------------------------------------------------------------------- #
#  OUTPUT                                                                      #
# --------------------------------------------------------------------------- #
def _d(P):
    return "M " + " L ".join("%.2f,%.2f" % (x, y) for x, y in P)


def _svg_body(lanes, red, green):
    o = ['<path d="%s" fill="none" stroke="#ff0000" stroke-width="2.4"/>' % _d(red),
         '<path d="%s" fill="none" stroke="#00aa00" stroke-width="2.4"/>' % _d(green)]
    o += ['<path d="%s" fill="none" stroke="#1d4ed8" stroke-width="1.4"/>' % _d(P) for P in lanes]
    return "\n".join(o)


def _viewbox(red, green, pad=25):
    xs = np.r_[red[:, 0], green[:, 0]]; ys = np.r_[red[:, 1], green[:, 1]]
    return (xs.min()-pad, ys.min()-pad, np.ptp(xs)+2*pad, np.ptp(ys)+2*pad)


def lanes_to_svg_text(lanes, red, green, path_out):
    """Write an SVG. Use a .svg.txt name for project stores that disallow .svg."""
    vb = _viewbox(red, green)
    open(path_out, "w").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f">\n%s\n</svg>\n'
        % (vb[0], vb[1], vb[2], vb[3], _svg_body(lanes, red, green)))


def lanes_to_html(lanes, red, green, path_out, title="convoy"):
    """Write a self-contained pan/zoom viewer (HTML is project-store legal)."""
    vb = _viewbox(red, green)
    n, _ = count_crossings(lanes)
    html = """<!doctype html><html><head><meta charset="utf-8"><title>__T__</title><style>
html,body{margin:0;height:100%;background:#f4f4f2;font:12px system-ui}
#wrap{position:absolute;inset:0;overflow:hidden;cursor:grab}#wrap.drag{cursor:grabbing}
svg{width:100%;height:100%;touch-action:none}
#t{position:fixed;top:8px;left:10px;font-weight:700;color:#333}
#b{position:fixed;top:8px;right:8px}
button{background:#1b1b1d;color:#eee;border:1px solid #555;border-radius:6px;padding:5px 11px}
</style></head><body>
<div id="t">__T__ &mdash; __N__ lanes &middot; __X__ crossings</div>
<div id="b"><button id="rst">reset</button></div>
<div id="wrap"><svg viewBox="__VB__">__BODY__</svg></div><script>
var s=document.querySelector('svg');s.removeAttribute('width');s.removeAttribute('height');
var B={x:__X0__,y:__Y0__,w:__W__,h:__H__},V=Object.assign({},B);
function A(){s.setAttribute('viewBox',V.x+' '+V.y+' '+V.w+' '+V.h)}A();
var w=document.getElementById('wrap'),d=0,px,py;
w.onmousedown=function(e){d=1;px=e.clientX;py=e.clientY;w.classList.add('drag')};
onmouseup=function(){d=0;w.classList.remove('drag')};
onmousemove=function(e){if(!d)return;var r=w.getBoundingClientRect();
 V.x-=(e.clientX-px)*V.w/r.width;V.y-=(e.clientY-py)*V.h/r.height;px=e.clientX;py=e.clientY;A()};
w.addEventListener('wheel',function(e){e.preventDefault();var r=w.getBoundingClientRect(),
 mx=V.x+(e.clientX-r.left)/r.width*V.w,my=V.y+(e.clientY-r.top)/r.height*V.h,
 f=e.deltaY<0?.86:1.16;V.x=mx-(mx-V.x)*f;V.y=my-(my-V.y)*f;V.w*=f;V.h*=f;A()},{passive:false});
document.getElementById('rst').onclick=function(){V=Object.assign({},B);A()};
</script></body></html>"""
    html = (html.replace("__T__", title).replace("__N__", str(len(lanes)))
                .replace("__X__", str(n))
                .replace("__VB__", "%.1f %.1f %.1f %.1f" % vb)
                .replace("__X0__", "%.1f" % vb[0]).replace("__Y0__", "%.1f" % vb[1])
                .replace("__W__", "%.1f" % vb[2]).replace("__H__", "%.1f" % vb[3])
                .replace("__BODY__", _svg_body(lanes, red, green)))
    open(path_out, "w").write(html)


if __name__ == "__main__":
    import sys
    svg = sys.argv[1] if len(sys.argv) > 1 else "frame.svg"
    red, green = load_rails(svg)
    for it in (1, 2, 3, 4):
        lanes = build_convoy(red, green, iteration=it)
        n, hits = count_crossings(lanes)
        print("iter %d: %2d lanes, %d crossings %s" % (it, len(lanes), n, hits[:5]))
