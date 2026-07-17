#!/usr/bin/env python3
"""harp.py — build123d (OpenCascade) soundbox-arm solid from hedit's harp_spec.

    python3 harp.py [harp_spec.json] [frame.svg]
    -> out/soundbox.step               exact B-rep (open in FreeCAD / Fusion)
    -> out/soundbox_front.svg          projected profile (visible + hidden)

For fully certified ISO drawings: open out/soundbox.step in FreeCAD, insert a
TechDraw page (ISO 7200 template), and drop projection groups — TechDraw does
standards-compliant hidden lines, dimensions, and title blocks from this STEP.

Sections come from sweep2's verified math (same pipeline golden-tested against
core.py): green spine trimmed at z=130, arc-resampled to S stations, h from the
red-rail ray-cast, outer ring = limaçon r=b(c+cosθ) with b=h/b_divisor.
"""
import ctypes, json, math, os, re, sys

# miniconda's pip OCP wheel needs conda's libexpat loaded first (symbol clash
# with the system one); harmless anywhere else.
try:
    ctypes.CDLL(os.path.expanduser("~/miniconda3/lib/libexpat.so.1"))
except OSError:
    pass

from build123d import Wire, Face, loft, export_step  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR = 1915.254


# ---- frame parsing (port of core._flatten; verified against golden.json) ----
def flatten(d, steps=48):
    toks = re.findall(r"[MmCcLlVvHhZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    pts, i, x, y, cmd = [], 0, 0.0, 0.0, None
    def n():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r"[MmCcLlVvHhZz]", toks[i]):
            cmd = toks[i]; i += 1
        if cmd is None:
            i += 1; continue
        C, rel = cmd.upper(), cmd.islower()
        if C == "M":
            a, b = n(), n()
            x, y = ((x + a), (y + b)) if (rel and pts) else (a, b)
            pts.append((x, y)); cmd = "l" if rel else "L"
        elif C == "L":
            a, b = n(), n(); x, y = ((x + a), (y + b)) if rel else (a, b); pts.append((x, y))
        elif C == "H":
            a = n(); x = (x + a) if rel else a; pts.append((x, y))
        elif C == "V":
            a = n(); y = (y + a) if rel else a; pts.append((x, y))
        elif C == "C":
            x1, y1, x2, y2, ex, ey = n(), n(), n(), n(), n(), n()
            if rel:
                x1 += x; y1 += y; x2 += x; y2 += y; ex += x; ey += y
            for s in range(1, steps + 1):
                u = s / steps; m = 1 - u
                pts.append((m*m*m*x + 3*m*m*u*x1 + 3*m*u*u*x2 + u*u*u*ex,
                            m*m*m*y + 3*m*m*u*y1 + 3*m*u*u*y2 + u*u*u*ey))
            x, y = ex, ey
    return pts


def getd(svg, pid):
    i = svg.index('id="%s"' % pid)
    ps = svg.rfind("<path", 0, i); pe = svg.index("/>", i)
    return re.search(r'\sd="([^"]*)"', svg[ps:pe]).group(1)


def cumseg(P):
    s = [0.0]
    for i in range(1, len(P)):
        s.append(s[-1] + math.hypot(P[i][0]-P[i-1][0], P[i][1]-P[i-1][1]))
    return s


def interp(u, seg, P):
    if u <= 0: return P[0]
    if u >= seg[-1]: return P[-1]
    lo, hi = 0, len(seg) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if seg[m] <= u: lo = m
        else: hi = m
    f = (u - seg[lo]) / ((seg[hi] - seg[lo]) or 1)
    return (P[lo][0] + f*(P[hi][0]-P[lo][0]), P[lo][1] + f*(P[hi][1]-P[lo][1]))


def ray_hit(p, d, poly):
    best = None
    for k in range(len(poly) - 1):
        a, b = poly[k], poly[k+1]
        ex, ey = b[0]-a[0], b[1]-a[1]
        den = d[0]*(-ey) - d[1]*(-ex)
        if abs(den) < 1e-9: continue
        rx, ry = a[0]-p[0], a[1]-p[1]
        t = (rx*(-ey) - ry*(-ex)) / den
        u = (d[0]*ry - d[1]*rx) / den
        if 0 <= u <= 1 and t > 1e-3 and (best is None or t < best):
            best = t
    return best


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../sweep2/harp_spec.json")
    frame_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "../../sweep2/frame.svg")
    spec = json.load(open(spec_path))
    svg = open(frame_path).read()
    green = flatten(getd(svg, "green_curve"))
    red = flatten(getd(svg, "red_curve"))

    sb = spec.get("soundbox", {})
    c_out = sb.get("c_out", 2.0)
    b_div = sb.get("b_divisor", 4)
    S = spec.get("sampling", {}).get("S", 160)
    trim = spec.get("base", {}).get("trim_z", 130.0)
    sh_in = spec.get("windows", {}).get("sh_in", {"x": 965.2, "y": 525.3})

    a, b = 0, len(green) - 1
    while a < len(green)//2 and (FLOOR - green[a][1]) < trim: a += 1
    while b > len(green)//2 and (FLOOR - green[b][1]) < trim: b -= 1
    g = green[a:b+1]
    seg = cumseg(g)
    us = [seg[-1] * k / (S - 1) for k in range(S)]
    spine = [interp(u, seg, g) for u in us]

    # tangents (simple central difference is adequate for the loft; the exact
    # gaussian variant lives in cad/replicad/lib/pipeline.js and hedit)
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

    h = [ray_hit(spine[i], N[i], red) or 200.0 for i in range(S)]

    si = min(range(S), key=lambda i: math.hypot(spine[i][0]-sh_in["x"], spine[i][1]-sh_in["y"]))
    arc1 = us[si]
    stations = [i for i in range(S) if us[i] < arc1]
    print(f"stations: {len(stations)}  c_out: {c_out}  b_div: {b_div}")

    wires = []
    RING, STRIDE = 96, 3
    for k in stations[::STRIDE]:
        bb = h[k] / b_div
        ring = []
        for j in range(RING):
            th = 2*math.pi*j/RING
            r = bb * (c_out + math.cos(th))
            ring.append((-r*math.sin(th), r*math.cos(th)))
        ymin = min(p[1] for p in ring)
        o = (spine[k][0], 0.0, FLOOR - spine[k][1])
        nx, ny = N[k]
        pts = [(o[0] + (p[1]-ymin)*nx, p[0], o[2] + (p[1]-ymin)*(-ny)) for p in ring]
        wires.append(Face(Wire.make_polygon(pts, close=True)))

    print(f"lofting {len(wires)} wires through OCC…")
    solid = loft(sections=wires, ruled=False)
    print("solid volume:", round(solid.volume/1e6, 2), "L")

    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
    export_step(solid, os.path.join(out, "soundbox.step"))
    print("STEP →", os.path.join(out, "soundbox.step"))

    try:  # projected profile with hidden-line removal
        visible, hidden = solid.project_to_viewport((0, -5000, 800))
        from build123d import ExportSVG, LineType
        exp = ExportSVG(scale=0.2)
        exp.add_layer("hidden", line_type=LineType.HIDDEN)
        exp.add_shape(visible)
        exp.add_shape(hidden, layer="hidden")
        exp.write(os.path.join(out, "soundbox_front.svg"))
        print("profile →", os.path.join(out, "soundbox_front.svg"))
    except Exception as e:
        print("projection skipped:", e)
    print("done. For certified ISO sheets: FreeCAD → TechDraw → insert this STEP.")


if __name__ == "__main__":
    main()
