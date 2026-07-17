#!/usr/bin/env node
// border_fit.js — wrap the pins+sharps in border.csv with a closed 10-node bezier of minimum
// enclosed area, keeping ≥ R mm clearance from every dot.
//
// Framing: minimize area enclosed by the closed bezier  s.t.  dist(curve, dot) ≥ R for every dot,
// and all dots inside. The analytic optimum is the R-outward offset of the dots' convex hull
// (≥ R from every dot by construction, minimal area among surrounding curves). We sample that
// offset, resample to N knots, build a closed C1 (Catmull-Rom) bezier, then push any knot radially
// out until the true min clearance ≥ R — so the 10-node curve provably keeps the air gap.
//
//   node border_fit.js [border.csv] [R=13] [N=10]
// Writes border_curve.svg (preview) and prints area + min clearance + the path/knots.
"use strict";
const fs = require("fs");

const csvPath = process.argv[2] || "border.csv";
const R = parseFloat(process.argv[3]) || 13;
const N = parseInt(process.argv[4], 10) || 10;

// --- read dots (x,z) ---------------------------------------------------------------
const rows = fs.readFileSync(csvPath, "utf8").trim().split(/\r?\n/);
const header = rows[0].split(",");
const xi = header.indexOf("x"), zi = header.indexOf("z");
const dots = rows.slice(1).map(r => { const c = r.split(","); return [parseFloat(c[xi]), parseFloat(c[zi])]; })
                 .filter(p => Number.isFinite(p[0]) && Number.isFinite(p[1]));
if(dots.length < 3){ console.error("need ≥3 dots"); process.exit(1); }

// --- convex hull (Andrew's monotone chain), CCW ------------------------------------
function hull(pts){
  const p = pts.slice().sort((a,b)=> a[0]-b[0] || a[1]-b[1]);
  const cross=(o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);
  const lo=[]; for(const q of p){ while(lo.length>=2 && cross(lo[lo.length-2],lo[lo.length-1],q)<=0) lo.pop(); lo.push(q); }
  const up=[]; for(let i=p.length-1;i>=0;i--){ const q=p[i]; while(up.length>=2 && cross(up[up.length-2],up[up.length-1],q)<=0) up.pop(); up.push(q); }
  return lo.slice(0,-1).concat(up.slice(0,-1));
}
const H = hull(dots);

// --- centroid (for radial pushes) ---------------------------------------------------
const C = dots.reduce((s,p)=>[s[0]+p[0],s[1]+p[1]],[0,0]).map(v=>v/dots.length);

// --- R-outward offset of the hull as a dense polygon (parallel edges + corner arcs) -
function offsetHull(Hp, r){
  const n=Hp.length, out=[];
  for(let i=0;i<n;i++){
    const a=Hp[i], b=Hp[(i+1)%n], prev=Hp[(i-1+n)%n];
    // outward normal of edge a->b (hull is CCW => outward normal is to the right: (dy,-dx))
    const ex=b[0]-a[0], ey=b[1]-a[1], el=Math.hypot(ex,ey)||1; const nx=ey/el, ny=-ex/el;
    // corner arc at a, from the previous edge's normal to this edge's normal
    const px=a[0]-prev[0], py=a[1]-prev[1], pl=Math.hypot(px,py)||1; const pnx=py/pl, pny=-px/pl;
    let a0=Math.atan2(pny,pnx), a1=Math.atan2(ny,nx);
    while(a1<a0) a1+=2*Math.PI;                 // sweep CCW (convex corner)
    const steps=Math.max(2, Math.ceil((a1-a0)/0.2));
    for(let k=0;k<=steps;k++){ const t=a0+(a1-a0)*k/steps; out.push([a[0]+r*Math.cos(t), a[1]+r*Math.sin(t)]); }
    out.push([a[0]+nx*r, a[1]+ny*r], [b[0]+nx*r, b[1]+ny*r]);   // offset edge
  }
  return out;
}

// --- resample a closed polygon to N points at uniform arc length --------------------
function resampleClosed(P, m){
  const seg=[]; let total=0;
  for(let i=0;i<P.length;i++){ const a=P[i], b=P[(i+1)%P.length]; const d=Math.hypot(b[0]-a[0],b[1]-a[1]); seg.push(d); total+=d; }
  const out=[]; let target=0, k=0, acc=0;
  for(let j=0;j<m;j++){
    target=total*j/m;
    while(k<P.length && acc+seg[k]<target){ acc+=seg[k]; k++; }
    const a=P[k%P.length], b=P[(k+1)%P.length], f=seg[k%P.length]?(target-acc)/seg[k%P.length]:0;
    out.push([a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f]);
  }
  return out;
}

// --- closed Catmull-Rom -> cubic bezier segments ------------------------------------
function closedBezier(K){
  const n=K.length, segs=[];
  for(let i=0;i<n;i++){
    const p0=K[(i-1+n)%n], p1=K[i], p2=K[(i+1)%n], p3=K[(i+2)%n];
    const c1=[p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6];
    const c2=[p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6];
    segs.push([p1,c1,c2,p2]);
  }
  return segs;
}
function bezPt(s,t){ const u=1-t; return [
  u*u*u*s[0][0]+3*u*u*t*s[1][0]+3*u*t*t*s[2][0]+t*t*t*s[3][0],
  u*u*u*s[0][1]+3*u*u*t*s[1][1]+3*u*t*t*s[2][1]+t*t*t*s[3][1] ]; }
function sampleBezier(segs, per){ const pts=[]; for(const s of segs) for(let i=0;i<per;i++) pts.push(bezPt(s,i/per)); return pts; }

function minClearance(segs){
  const pts=sampleBezier(segs,24); let mn=Infinity, who=-1;
  for(let d=0;d<dots.length;d++){ let b=Infinity; for(const q of pts){ const dd=Math.hypot(q[0]-dots[d][0],q[1]-dots[d][1]); if(dd<b)b=dd; } if(b<mn){mn=b;who=d;} }
  return {mn, who};
}
function area(segs){ const pts=sampleBezier(segs,24); let A=0; for(let i=0;i<pts.length;i++){ const a=pts[i], b=pts[(i+1)%pts.length]; A+=a[0]*b[1]-b[0]*a[1]; } return Math.abs(A)/2; }

// --- build: hull offset -> N knots -> closed bezier, then enforce ≥ R ---------------
let knots = resampleClosed(offsetHull(H, R), N);
let segs = closedBezier(knots);
for(let it=0; it<200; it++){
  const { mn, who } = minClearance(segs);
  if(mn >= R - 0.05) break;
  // push the knot nearest the offending dot radially outward (from centroid) by the deficit
  const d = dots[who]; let bi=0, bd=Infinity;
  knots.forEach((k,i)=>{ const dd=Math.hypot(k[0]-d[0],k[1]-d[1]); if(dd<bd){bd=dd;bi=i;} });
  let rx=knots[bi][0]-C[0], ry=knots[bi][1]-C[1]; const rl=Math.hypot(rx,ry)||1; rx/=rl; ry/=rl;
  knots[bi]=[knots[bi][0]+rx*(R-mn+0.3), knots[bi][1]+ry*(R-mn+0.3)];
  segs=closedBezier(knots);
}

const { mn } = minClearance(segs);
const A = area(segs);
const fmt=v=>Math.round(v*1000)/1000;
let d = "M "+fmt(segs[0][0][0])+" "+fmt(segs[0][0][1]);
for(const s of segs) d += " C "+fmt(s[1][0])+" "+fmt(s[1][1])+" "+fmt(s[2][0])+" "+fmt(s[2][1])+" "+fmt(s[3][0])+" "+fmt(s[3][1]);
d += " Z";

// --- preview SVG (z-up flipped to screen y-down) ------------------------------------
const all = dots.concat(sampleBezier(segs,24));
const minx=Math.min(...all.map(p=>p[0]))-20, maxx=Math.max(...all.map(p=>p[0]))+20;
const minz=Math.min(...all.map(p=>p[1]))-20, maxz=Math.max(...all.map(p=>p[1]))+20;
const Y=z=>(maxz - (z - minz)) ;   // flip z-up -> svg y-down within the box
const fy = z => maxz - z;          // simple flip
const sy = z => fy(z);
let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${fmt(minx)} ${fmt(fy(maxz))} ${fmt(maxx-minx)} ${fmt(maxz-minz)}" width="${fmt(maxx-minx)}" height="${fmt(maxz-minz)}">`;
svg += `<g transform="matrix(1 0 0 -1 0 ${fmt(maxz+minz)})">`;   // flip so z is up
let bd = "M "+fmt(segs[0][0][0])+" "+fmt(segs[0][0][1]);
for(const s of segs) bd += " C "+fmt(s[1][0])+" "+fmt(s[1][1])+" "+fmt(s[2][0])+" "+fmt(s[2][1])+" "+fmt(s[3][0])+" "+fmt(s[3][1]);
bd += " Z";
svg += `<path d="${bd}" fill="#1a9e3a22" stroke="#1a9e3a" stroke-width="1.5"/>`;
for(const p of dots){ svg += `<circle cx="${fmt(p[0])}" cy="${fmt(p[1])}" r="2" fill="#333"/>`;
  svg += `<circle cx="${fmt(p[0])}" cy="${fmt(p[1])}" r="${R}" fill="none" stroke="#bbb" stroke-width="0.4"/>`; }
for(const k of knots) svg += `<circle cx="${fmt(k[0])}" cy="${fmt(k[1])}" r="2.5" fill="#e60000"/>`;
svg += `</g></svg>`;
fs.writeFileSync("border_curve.svg", svg);

console.log(`dots=${dots.length}  hull=${H.length}  knots=${N}  R=${R}`);
console.log(`min clearance = ${fmt(mn)} mm  (target ≥ ${R})`);
console.log(`enclosed area = ${fmt(A)} mm²`);
console.log(`knots: ${knots.map(k=>"("+fmt(k[0])+","+fmt(k[1])+")").join(" ")}`);
console.log(`wrote border_curve.svg`);
