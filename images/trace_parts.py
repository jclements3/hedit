#!/usr/bin/env python3
"""
trace_parts.py - extract the GOLD and GRAY part outlines from a CAD/3D
screenshot frame and emit them as SVG paths (openable in hedit).

Pure Python: needs only Pillow + numpy (no potrace/cv2/skimage).

Pipeline:
  1. color-key each pixel as 'gold' or 'gray' (tunable thresholds below)
  2. clean the mask (drop tiny speckles, close 1px gaps)
  3. connected-components, Moore-neighbour boundary trace each blob
  4. Ramer-Douglas-Peucker simplify each contour
  5. write <frame>.traced.svg  (+ <frame>.gold.png / .gray.png debug masks)

Usage:
  python3 trace_parts.py harp_0600.jpg                 # one frame
  python3 trace_parts.py harp_0600.jpg --eps 2.0 --min-area 80
  python3 trace_parts.py harp_0600.jpg --only gold     # gold or gray
LOOK at the *.gold.png / *.gray.png masks first to confirm the color key
is catching the right pixels, then tune --gold-* / --gray-* / thresholds.
"""
import sys, argparse, collections
import numpy as np
from PIL import Image

# ---- color key -------------------------------------------------------------
def masks(rgb, args):
    f = rgb.reshape(-1, 3).astype(int)
    r, g, b = f[:, 0], f[:, 1], f[:, 2]
    mx = f.max(1); mn = f.min(1); sat = mx - mn
    dark = mx < args.dark               # background / unlit
    gold = (~dark) & (r >= g) & (g > b) & ((r - b) > args.gold_warmth) \
           & (mx > args.gold_min)
    gray = (~dark) & (sat < args.gray_sat) & (mx >= args.gray_min)
    H, W, _ = rgb.shape
    return gold.reshape(H, W), gray.reshape(H, W)

# ---- mask cleanup (binary open then close, 3x3) ----------------------------
def _shift_or(m):
    out = m.copy()
    out[1:, :] |= m[:-1, :]; out[:-1, :] |= m[1:, :]
    out[:, 1:] |= m[:, :-1]; out[:, :-1] |= m[:, 1:]
    return out
def _shift_and(m):
    out = m.copy()
    out[1:, :] &= m[:-1, :]; out[:-1, :] &= m[1:, :]
    out[:, 1:] &= m[:, :-1]; out[:, :-1] &= m[:, 1:]
    return out
def clean(m, close=1, open_=1):
    for _ in range(open_):  m = _shift_or(_shift_and(m))   # erode then dilate
    for _ in range(close):  m = _shift_and(_shift_or(m))   # dilate then erode
    return m

# ---- connected components (4-conn, iterative BFS) --------------------------
def components(m, min_area):
    H, W = m.shape
    seen = np.zeros_like(m)
    comps = []
    ys, xs = np.nonzero(m)
    for sy, sx in zip(ys, xs):
        if seen[sy, sx]:
            continue
        stack = [(sy, sx)]; seen[sy, sx] = True; pts = []
        while stack:
            y, x = stack.pop(); pts.append((y, x))
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny, nx = y+dy, x+dx
                if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; stack.append((ny, nx))
        if len(pts) >= min_area:
            comps.append(pts)
    return comps

# ---- Moore-neighbour boundary trace of one blob ----------------------------
_N8 = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
def trace(blob, shape):
    H, W = shape
    s = set(blob)
    start = min(blob)                      # top-most, then left-most
    contour = [start]
    cur = start; b_idx = 6                  # came from the left
    for _ in range(8 * len(blob) + 8):
        found = False
        for k in range(8):
            d = _N8[(b_idx + 1 + k) % 8]
            nb = (cur[0] + d[0], cur[1] + d[1])
            if nb in s:
                contour.append(nb)
                b_idx = (_N8.index(d) + 4) % 8   # back-direction
                cur = nb; found = True; break
        if not found:
            break
        if cur == start and len(contour) > 2:
            break
    return contour

# ---- Ramer-Douglas-Peucker -------------------------------------------------
def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a = np.array(pts, float)
    keep = np.zeros(len(a), bool); keep[0] = keep[-1] = True
    stack = [(0, len(a) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        p, q = a[i], a[j]; seg = q - p; L = np.hypot(*seg)
        if L == 0:
            d = np.hypot(*(a[i+1:j] - p).T)
        else:
            d = np.abs(np.cross(np.tile(seg, (j-i-1, 1)), a[i+1:j] - p)) / L
        m = d.argmax()
        if d[m] > eps:
            k = i + 1 + m; keep[k] = True
            stack += [(i, k), (k, j)]
    return [pts[i] for i in range(len(a)) if keep[i]]

# ---- SVG -------------------------------------------------------------------
def contour_to_d(c):
    # c is list of (y,x); SVG wants x,y
    pts = [f"{x},{y}" for y, x in c]
    return "M" + " L".join(pts) + " Z"

def run(path, args):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    H, W, _ = rgb.shape
    gold, gray = masks(rgb, args)
    layers = []
    if args.only in (None, "gold"): layers.append(("gold", "#caa64a", gold))
    if args.only in (None, "gray"): layers.append(("gray", "#9aa0a6", gray))
    body = []
    stem = path.rsplit(".", 1)[0]
    for name, color, m in layers:
        m = clean(m, args.close, args.open)
        Image.fromarray((m * 255).astype("uint8")).save(f"{stem}.{name}.png")
        ds = []
        for blob in components(m, args.min_area):
            c = rdp(trace(blob, (H, W)), args.eps)
            if len(c) >= 3:
                ds.append(contour_to_d(c))
        body.append(f'  <g id="{name}" fill="none" stroke="{color}" '
                    f'stroke-width="{args.sw}">')
        body += [f'    <path d="{d}"/>' for d in ds]
        body.append("  </g>")
        print(f"{name}: {len(ds)} paths")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">\n'
           f'  <rect width="{W}" height="{H}" fill="#202020"/>\n'
           + "\n".join(body) + "\n</svg>\n")
    out = f"{stem}.traced.svg"
    open(out, "w").write(svg)
    print("wrote", out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--only", choices=["gold", "gray"])
    ap.add_argument("--eps", type=float, default=1.5, help="RDP tolerance px")
    ap.add_argument("--min-area", type=int, default=60, dest="min_area")
    ap.add_argument("--sw", type=float, default=1.5, help="stroke width")
    ap.add_argument("--close", type=int, default=1)
    ap.add_argument("--open", type=int, default=1)
    ap.add_argument("--dark", type=int, default=60)
    ap.add_argument("--gold-warmth", type=int, default=30, dest="gold_warmth")
    ap.add_argument("--gold-min", type=int, default=70, dest="gold_min")
    ap.add_argument("--gray-sat", type=int, default=16, dest="gray_sat")
    ap.add_argument("--gray-min", type=int, default=60, dest="gray_min")
    run(ap.parse_args().image, ap.parse_args())
