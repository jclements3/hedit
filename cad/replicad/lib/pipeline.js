"use strict";
// Frame -> spine -> h field. Vanilla-JS port of sweep2.py's essential soundbox
// path (core._flatten, trim, arc-resample, gauss tangents, sign-propagated
// normals, fh ray-cast, _field filter). Verified against sweep2/golden.json.
const FLOOR = 1915.254;

// ---- core._flatten: M/L/C/V/H/Z, abs+rel, 48 uniform steps per cubic --------
function flatten(d, steps = 48) {
  const toks = d.match(/[MmCcLlVvHhZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?/g) || [];
  const pts = []; let i = 0, x = 0, y = 0, cmd = null;
  const num = () => parseFloat(toks[i++]);
  while (i < toks.length) {
    if (/[MmCcLlVvHhZz]/.test(toks[i])) { cmd = toks[i]; i++; }
    if (cmd === null) { i++; continue; }
    const C = cmd.toUpperCase(), rel = cmd !== C;
    if (C === 'M') {
      let a = num(), b = num();
      if (rel && pts.length) { x += a; y += b; } else { x = a; y = b; }
      pts.push([x, y]); cmd = rel ? 'l' : 'L';
    } else if (C === 'L') {
      let a = num(), b = num(); if (rel) { x += a; y += b; } else { x = a; y = b; } pts.push([x, y]);
    } else if (C === 'H') {
      let a = num(); x = rel ? x + a : a; pts.push([x, y]);
    } else if (C === 'V') {
      let a = num(); y = rel ? y + a : a; pts.push([x, y]);
    } else if (C === 'C') {
      let x1 = num(), y1 = num(), x2 = num(), y2 = num(), ex = num(), ey = num();
      if (rel) { x1 += x; y1 += y; x2 += x; y2 += y; ex += x; ey += y; }
      const cx = x, cy = y;
      for (let s = 1; s <= steps; s++) {
        const u = s / steps, m = 1 - u;
        pts.push([m*m*m*cx + 3*m*m*u*x1 + 3*m*u*u*x2 + u*u*u*ex,
                  m*m*m*cy + 3*m*m*u*y1 + 3*m*u*u*y2 + u*u*u*ey]);
      }
      x = ex; y = ey;
    } // Z: no-op (paths stay open)
  }
  return pts;
}

function cumseg(P) { const s = [0]; for (let i = 1; i < P.length; i++) s.push(s[i-1] + Math.hypot(P[i][0]-P[i-1][0], P[i][1]-P[i-1][1])); return s; }
function interpXY(us, seg, P) { // np.interp per axis, clamped
  const out = [];
  for (const u of us) {
    let lo = 0, hi = seg.length - 1;
    if (u <= 0) { out.push(P[0].slice()); continue; }
    if (u >= seg[hi]) { out.push(P[hi].slice()); continue; }
    while (hi - lo > 1) { const m = (lo+hi) >> 1; if (seg[m] <= u) lo = m; else hi = m; }
    const f = (u - seg[lo]) / (seg[hi] - seg[lo] || 1);
    out.push([P[lo][0] + f*(P[hi][0]-P[lo][0]), P[lo][1] + f*(P[hi][1]-P[lo][1])]);
  }
  return out;
}
function linspace(a, b, n) { const o = []; for (let k = 0; k < n; k++) o.push(a + (b-a)*k/(n-1)); return o; }

// sweep2._gauss_smooth (sigma=1.5, half=4), edge-clamp padding
function gaussSmooth(P, sigma = 1.5, half = 4) {
  const k = []; let ks = 0;
  for (let j = -half; j <= half; j++) { const w = Math.exp(-0.5*(j/sigma)**2); k.push(w); ks += w; }
  for (let j = 0; j < k.length; j++) k[j] /= ks;
  const n = P.length, out = P.map(p => p.slice());
  for (let c = 0; c < 2; c++) {
    for (let idx = 0; idx < n; idx++) {
      let acc = 0;
      for (let j = -half; j <= half; j++) {
        let src = idx + j; src = src < 0 ? 0 : src >= n ? n-1 : src; // clamp == pad with ends
        acc += k[j+half] * P[src][c];
      }
      out[idx][c] = acc;
    }
  }
  return out;
}

// ray-cast: nearest forward hit of ray (p, +d) against open polyline `poly`
function fh(p, d, poly) {
  let best = null;
  for (let k = 0; k < poly.length - 1; k++) {
    const a = poly[k], b = poly[k+1], ex = b[0]-a[0], ey = b[1]-a[1];
    const den = d[0]*(-ey) - d[1]*(-ex);
    if (Math.abs(den) < 1e-9) continue;
    const rx = a[0]-p[0], ry = a[1]-p[1];
    const t = (rx*(-ey) - ry*(-ex)) / den;
    const u = (d[0]*ry - d[1]*rx) / den;
    if (u >= 0 && u <= 1 && t > 1e-3 && (best === null || t < best)) best = t;
  }
  return best;
}

// sweep2._field: validity filter + spike reject + interp + edge extrap + 3-tap + clamp10
function field(vals, s, spike = 3.0, minScalar = 10.0) {
  const n = vals.length;
  let v = vals.map(x => (x === null || x < minScalar) ? NaN : +x);
  let ok = v.map(x => !Number.isNaN(x));
  const okIdx = () => { const o = []; for (let i = 0; i < n; i++) if (ok[i]) o.push(i); return o; };
  let idx = okIdx();
  if (idx.length >= 4) {
    const diffs = [];
    for (let j = 1; j < idx.length; j++) diffs.push(Math.abs(v[idx[j]] - v[idx[j-1]]));
    diffs.sort((a,b)=>a-b);
    const med = diffs.length % 2 ? diffs[(diffs.length-1)/2] : 0.5*(diffs[diffs.length/2-1]+diffs[diffs.length/2]);
    for (let j = 1; j < idx.length; j++) {
      const a = idx[j-1], b = idx[j];
      if (Math.abs(v[b] - v[a]) > spike * Math.max(med, 1.0) * (b - a)) v[b] = NaN;
    }
    ok = v.map(x => !Number.isNaN(x));
    idx = okIdx();
  }
  // linear interp over valid stations in arc-length s
  const f = new Array(n);
  for (let i = 0; i < n; i++) {
    if (ok[i]) { f[i] = v[i]; continue; }
    let lo = idx[0], hi = idx[idx.length-1];
    for (let j = 0; j < idx.length; j++) { if (idx[j] <= i) lo = idx[j]; if (idx[j] >= i) { hi = idx[j]; break; } }
    if (i <= idx[0]) { f[i] = v[idx[0]]; }
    else if (i >= idx[idx.length-1]) { f[i] = v[idx[idx.length-1]]; }
    else { const t = (s[i]-s[lo])/(s[hi]-s[lo]||1); f[i] = v[lo] + t*(v[hi]-v[lo]); }
  }
  const i0 = idx[0], i1 = idx[idx.length-1];
  if (i0 > 0) { const j = Math.min(i0+6, i1); const sl = (f[j]-f[i0])/(s[j]-s[i0]+1e-9); for (let i = 0; i < i0; i++) f[i] = f[i0] + sl*(s[i]-s[i0]); }
  if (i1 < n-1) { const j = Math.max(i1-6, i0); const sl = (f[i1]-f[j])/(s[i1]-s[j]+1e-9); for (let i = i1+1; i < n; i++) f[i] = f[i1] + sl*(s[i]-s[i1]); }
  const gg = f.slice();
  for (let i = 1; i < n-1; i++) gg[i] = 0.25*f[i-1] + 0.5*f[i] + 0.25*f[i+1];
  return gg.map(x => Math.max(x, minScalar));
}

function assertGreenOrientation(green) {
  const seg = cumseg(green), total = seg[seg.length-1];
  const at = (s) => interpXY([s], seg, green)[0];
  const p = at(0.376*total);
  if (Math.hypot(p[0]-968, p[1]-545) >= 60) throw new Error("GREEN SWAPPED: start side does not climb to the shoulder");
  const xs = [400,800,1200].map(s => at(total-s)[0]);
  const spread = Math.max(...xs)-Math.min(...xs), mean = (xs[0]+xs[1]+xs[2])/3;
  if (!(spread < 25 && Math.abs(mean-203) < 40)) throw new Error("GREEN SWAPPED: end side is not the vertical pillar column");
  return true;
}

// Full soundbox pipeline: returns per-soundbox-station {s, spine, h, b, tau}.
function soundboxStations(green, red, opts = {}) {
  const S = opts.S || 160, TRIM = opts.trimZ ?? 130.0;
  const shIn = opts.sh_in || { x: 965.2, y: 525.3 };
  // 1. trim green tails below z=TRIM
  let a = 0, b = green.length - 1;
  while (a < green.length/2 && (FLOOR - green[a][1]) < TRIM) a++;
  while (b > green.length/2 && (FLOOR - green[b][1]) < TRIM) b--;
  const g = green.slice(a, b+1);
  // 2. arc-length resample to S
  const seg = cumseg(g), us = linspace(0, seg[seg.length-1], S);
  const spine = interpXY(us, seg, g);
  // 3. tangents from gaussian-smoothed spine (np.gradient)
  const sm = gaussSmooth(spine);
  const T = spine.map((_, i) => {
    let dx, dy;
    if (i === 0) { dx = sm[1][0]-sm[0][0]; dy = sm[1][1]-sm[0][1]; }
    else if (i === S-1) { dx = sm[S-1][0]-sm[S-2][0]; dy = sm[S-1][1]-sm[S-2][1]; }
    else { dx = (sm[i+1][0]-sm[i-1][0])/2; dy = (sm[i+1][1]-sm[i-1][1])/2; }
    const nl = Math.hypot(dx, dy) + 1e-12; return [dx/nl, dy/nl];
  });
  // 4. normals (-Ty, Tx), global handedness at S/4 vs cen, then sign-propagate
  const N = T.map(t => [-t[1], t[0]]);
  const cen = [400, 900], q = S >> 2;
  if ((spine[q][0]-cen[0])*N[q][0] + (spine[q][1]-cen[1])*N[q][1] < 0) for (const nn of N) { nn[0]=-nn[0]; nn[1]=-nn[1]; }
  for (let i = 1; i < S; i++) if (N[i][0]*N[i-1][0] + N[i][1]*N[i-1][1] < 0) { N[i][0]=-N[i][0]; N[i][1]=-N[i][1]; }
  // 5. h = fh(spine, N, red), filtered
  const hRaw = spine.map((p, i) => fh(p, N[i], red));
  const h = field(hRaw, us);
  // 6. arc1 = us[nearest station to sh_in]; soundbox = us[i] < arc1
  let si = 0, sd = Infinity;
  for (let i = 0; i < S; i++) { const dd = Math.hypot(spine[i][0]-shIn.x, spine[i][1]-shIn.y); if (dd < sd) { sd = dd; si = i; } }
  const arc1 = us[si];
  const sbI = []; for (let i = 0; i < S; i++) if (us[i] < arc1) sbI.push(i);
  let ymin = Infinity, ymax = -Infinity; for (const i of sbI) { ymin = Math.min(ymin, spine[i][1]); ymax = Math.max(ymax, spine[i][1]); }
  return sbI.map(i => ({
    i, s: us[i], spine: spine[i], N: N[i], h: h[i], b: h[i]/4,
    tau: Math.min(Math.max((spine[i][1]-ymin)/(ymax-ymin+1e-9), 0), 1),
  }));
}

module.exports = { FLOOR, flatten, cumseg, interpXY, linspace, gaussSmooth, fh, field, assertGreenOrientation, soundboxStations };
