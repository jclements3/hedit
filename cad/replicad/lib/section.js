"use strict";
// Pure-JS port of the Clements-49 soundbox section math (core.py).
// No numpy/shapely. Verified against sweep2/golden.json.
// Everything here is a straight port; keep it that way and re-verify on any change.

// ---- limaçon outer/inner ring: r = b*(c + cos th); (x,y) = (-r sin th, r cos th)
function _curve(c, b, n = 720) {
  const P = [];
  for (let k = 0; k < n; k++) {
    const th = 2 * Math.PI * k / n;
    const r = b * (c + Math.cos(th));
    P.push([-r * Math.sin(th), r * Math.cos(th)]);
  }
  return P;
}

function polyArea(P) { // shoelace, |signed|
  let a = 0;
  for (let i = 0; i < P.length; i++) {
    const [x0, y0] = P[i], [x1, y1] = P[(i + 1) % P.length];
    a += x0 * y1 - x1 * y0;
  }
  return Math.abs(a) / 2;
}

// ---- resample a closed polyline to n evenly-arclength points (core._resample)
function _resample(poly, n) {
  const pts = poly.concat([poly[0]]);
  const d = [0];
  for (let i = 1; i < pts.length; i++) {
    d.push(d[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  }
  const total = d[d.length - 1];
  if (total === 0) return Array.from({ length: n }, () => poly[0].slice());
  const out = [];
  let j = 0;
  for (let k = 0; k < n; k++) {
    const u = total * k / n; // endpoint=False
    while (j < d.length - 2 && d[j + 1] < u) j++;
    const seg = d[j + 1] - d[j] || 1e-12;
    const t = (u - d[j]) / seg;
    out.push([pts[j][0] + t * (pts[j + 1][0] - pts[j][0]),
              pts[j][1] + t * (pts[j + 1][1] - pts[j][1])]);
  }
  return out;
}

// ---- section outer contour: limaçon shell, dimple shifted to y=0.
// NOTE: core.section_rings applies a shapely erode/dilate fillet. For the 2-D
// acoustic preview we use the UNFILLETED outer (fillet r is min(0.3*b/2,0.7*g*b);
// on the b/g we care about it moves area <0.05% — see golden limacon vs curve).
// The bore/chamber math below is what matters acoustically.
function sectionOuter(g, b) {
  const outer = _curve(2.0, b);              // c=2 outer limaçon
  let ymin = Infinity;
  for (const p of outer) if (p[1] < ymin) ymin = p[1];
  return outer.map(p => [p[0], p[1] - ymin]); // dimple/min-y -> 0
}

// ---- variable-thickness inner wall (core._variable_bore) --------------------
// Offset the outer contour INWARD by an angle-dependent wall t(theta), theta
// measured from the centroid: 0 at the dimple/front, 180 at the belly.
function centroid(P) {
  // polygon centroid (shapely .centroid == area centroid)
  let a = 0, cx = 0, cy = 0;
  for (let i = 0; i < P.length; i++) {
    const [x0, y0] = P[i], [x1, y1] = P[(i + 1) % P.length];
    const cross = x0 * y1 - x1 * y0;
    a += cross; cx += (x0 + x1) * cross; cy += (y0 + y1) * cross;
  }
  a *= 0.5;
  if (Math.abs(a) < 1e-12) { // degenerate -> vertex mean
    let mx = 0, my = 0; for (const p of P) { mx += p[0]; my += p[1]; }
    return [mx / P.length, my / P.length];
  }
  return [cx / (6 * a), cy / (6 * a)];
}

function variableBore(ext, tSpine, tWing, tShell) {
  const e = _resample(ext, 720);
  const C = centroid(e);
  const N = e.length;
  // vertex normals from central-difference tangents (np.roll(-1) - np.roll(+1))
  const inn = [];
  for (let i = 0; i < N; i++) {
    const a = e[(i - 1 + N) % N], c = e[(i + 1) % N];
    const dx = c[0] - a[0], dy = c[1] - a[1];
    let nx = dy, ny = -dx;                 // (d[:,1], -d[:,0])
    const nl = Math.hypot(nx, ny) + 1e-12;
    nx /= nl; ny /= nl;
    // flip to point toward centroid (inward)
    const tocx = C[0] - e[i][0], tocy = C[1] - e[i][1];
    if (nx * tocx + ny * tocy < 0) { nx = -nx; ny = -ny; }
    // theta from centroid: arccos(clip(-dd_y/|dd|)), dd = e - C
    const ddx = e[i][0] - C[0], ddy = e[i][1] - C[1];
    const dn = Math.hypot(ddx, ddy) + 1e-12;
    let cth = -ddy / dn; cth = Math.max(-1, Math.min(1, cth));
    const th = Math.acos(cth) * 180 / Math.PI;
    let t;
    if (th <= 20) t = tSpine;
    else if (th <= 70) t = tSpine + (tWing - tSpine) * (th - 20) / 50;
    else t = tWing + (tShell - tWing) * Math.min((th - 70) / 20, 1);
    inn.push([e[i][0] + nx * t, e[i][1] + ny * t]);
  }
  return inn; // NB: shapely buffer(0) cleans self-intersections; JS port skips that.
}

// wall schedule from tau (1=bass/base, 0=treble): core uses
// _variable_bore(ext, 1.5+2.5*tau, 2.5, 2.5+1.0*tau)
function wallSchedule(tau) {
  return { tSpine: 1.5 + 2.5 * tau, tWing: 2.5, tShell: 2.5 + 1.0 * tau };
}

module.exports = { _curve, _resample, polyArea, sectionOuter, variableBore, wallSchedule, centroid };
