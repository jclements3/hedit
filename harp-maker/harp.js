"use strict";
/*
 * harp.js -- Maker.js proof-of-concept harp designer.
 *
 * Pipeline (your roadmap):
 *   1) load string specs (from ../strings.svg)
 *   2) air-gap spacing (constant edge-to-edge gap, diameter-aware)
 *   3) alignment experiments (top | middle | bottom)
 *   4) fit a Bezier through the string BOTTOMS, node-count controlled, smooth handles
 *   5) spine: extra Bezier curves for the frame outline (neck over the tops + soundboard
 *      under the bottoms + connectors)
 *   6) "lemicons" -- placeholder, pending definition (see CONFIG.lemicons)
 *
 * Coordinates: Maker.js is Y-UP / origin bottom-left (a right-handed +X/+Z frame --
 * exactly the convention you asked for). We flip the SVG's y-down coords on load.
 *
 * Exports harp.svg and harp.dxf (DXF = fabrication / CAD).
 */

const fs = require("fs");
const path = require("path");
const makerjs = require("makerjs");

// ---------------------------------------------------------------- config
const CONFIG = {
  input: path.join(__dirname, "..", "strings.svg"),
  align: process.argv[2] || "top",        // top | middle | bottom
  airGap: parseFloat(process.argv[3]) || 13,
  fitNodes: parseInt(process.argv[4], 10) || 8,
  spine: true,
  lemicons: false,                          // TODO: define what a "lemicon" is
};

// ====================================================================
// Schneider cubic-Bezier fit (max-nodes + pinned endpoints), points = [x,y]
// ====================================================================
const Vec = {
  sub:(a,b)=>[a[0]-b[0],a[1]-b[1]], add:(a,b)=>[a[0]+b[0],a[1]+b[1]],
  mul:(a,s)=>[a[0]*s,a[1]*s], dot:(a,b)=>a[0]*b[0]+a[1]*b[1],
  len:a=>Math.hypot(a[0],a[1]), unit:a=>{const n=Math.hypot(a[0],a[1]);return n?[a[0]/n,a[1]/n]:a;},
};
const B0=u=>(1-u)**3, B1=u=>3*u*(1-u)**2, B2=u=>3*u*u*(1-u), B3=u=>u**3;
const Q=(c,u)=>Vec.add(Vec.add(Vec.mul(c[0],B0(u)),Vec.mul(c[1],B1(u))),Vec.add(Vec.mul(c[2],B2(u)),Vec.mul(c[3],B3(u))));
const Q1=(c,u)=>{const t=1-u;return Vec.add(Vec.add(Vec.mul(Vec.sub(c[1],c[0]),3*t*t),Vec.mul(Vec.sub(c[2],c[1]),6*t*u)),Vec.mul(Vec.sub(c[3],c[2]),3*u*u));};
const Q2=(c,u)=>Vec.add(Vec.mul(Vec.add(Vec.sub(c[2],Vec.mul(c[1],2)),c[0]),6*(1-u)),Vec.mul(Vec.add(Vec.sub(c[3],Vec.mul(c[2],2)),c[1]),6*u));

function fitCurve(points, err){
  if(points.length<2) return [];
  const lt=Vec.unit(Vec.sub(points[1],points[0]));
  const rt=Vec.unit(Vec.sub(points[points.length-2],points[points.length-1]));
  return fitCubic(points,lt,rt,err);
}
function fitCubic(pts,lt,rt,err){
  if(pts.length===2){const d=Vec.len(Vec.sub(pts[0],pts[1]))/3;
    return [[pts[0],Vec.add(pts[0],Vec.mul(lt,d)),Vec.add(pts[1],Vec.mul(rt,d)),pts[1]]];}
  let u=chord(pts), bez=gen(pts,u,lt,rt), [e,sp]=maxErr(pts,bez,u);
  if(e<err) return [bez];
  if(e<err*err){for(let i=0;i<20;i++){const up=u.map((uu,k)=>newton(bez,pts[k],uu));
    bez=gen(pts,up,lt,rt);[e,sp]=maxErr(pts,bez,up);if(e<err)return[bez];u=up;}}
  const ct=ctan(pts,sp);
  return fitCubic(pts.slice(0,sp+1),lt,ct,err).concat(fitCubic(pts.slice(sp),Vec.mul(ct,-1),rt,err));
}
function gen(pts,par,lt,rt){
  const n=pts.length,first=pts[0],last=pts[n-1];
  const A=par.map(u=>[Vec.mul(lt,B1(u)),Vec.mul(rt,B2(u))]);
  let C=[[0,0],[0,0]],X=[0,0];
  for(let i=0;i<n;i++){C[0][0]+=Vec.dot(A[i][0],A[i][0]);C[0][1]+=Vec.dot(A[i][0],A[i][1]);C[1][0]=C[0][1];C[1][1]+=Vec.dot(A[i][1],A[i][1]);
    const u=par[i],tmp=Vec.sub(pts[i],Vec.add(Vec.add(Vec.mul(first,B0(u)),Vec.mul(first,B1(u))),Vec.add(Vec.mul(last,B2(u)),Vec.mul(last,B3(u)))));
    X[0]+=Vec.dot(A[i][0],tmp);X[1]+=Vec.dot(A[i][1],tmp);}
  const dCC=C[0][0]*C[1][1]-C[1][0]*C[0][1],dCX=C[0][0]*X[1]-C[1][0]*X[0],dXC=X[0]*C[1][1]-X[1]*C[0][1];
  const aL=dCC===0?0:dXC/dCC,aR=dCC===0?0:dCX/dCC,sl=Vec.len(Vec.sub(first,last)),eps=1e-6*sl;
  if(aL<eps||aR<eps) return [first,Vec.add(first,Vec.mul(lt,sl/3)),Vec.add(last,Vec.mul(rt,sl/3)),last];
  return [first,Vec.add(first,Vec.mul(lt,aL)),Vec.add(last,Vec.mul(rt,aR)),last];
}
function newton(b,p,u){const d=Vec.sub(Q(b,u),p),qp=Q1(b,u),qpp=Q2(b,u),num=Vec.dot(d,qp),den=Vec.dot(qp,qp)+Vec.dot(d,qpp);return Math.abs(den)<1e-10?u:u-num/den;}
function chord(pts){const u=[0];for(let i=1;i<pts.length;i++)u.push(u[i-1]+Vec.len(Vec.sub(pts[i],pts[i-1])));const t=u[u.length-1];return t===0?pts.map(()=>0):u.map(v=>v/t);}
function maxErr(pts,b,par){let m=0,sp=Math.floor(pts.length/2);for(let i=0;i<pts.length;i++){const d=Vec.len(Vec.sub(Q(b,par[i]),pts[i]))**2;if(d>=m){m=d;sp=i;}}return[m,sp];}
function ctan(pts,c){return Vec.unit(Vec.mul(Vec.add(Vec.sub(pts[c-1],pts[c]),Vec.sub(pts[c],pts[c+1])),0.5));}
function fitCurveMaxNodes(points, maxNodes){
  if(points.length<2) return [];
  const maxSegs=Math.max(1,(maxNodes|0)-1);
  let best=fitCurve(points,1e-9);
  if(best.length<=maxSegs) return pin(best,points);
  let mnx=Infinity,mny=Infinity,mxx=-Infinity,mxy=-Infinity;
  for(const p of points){mnx=Math.min(mnx,p[0]);mxx=Math.max(mxx,p[0]);mny=Math.min(mny,p[1]);mxy=Math.max(mxy,p[1]);}
  let hi=Math.max(Math.hypot(mxx-mnx,mxy-mny),1);
  while(fitCurve(points,hi).length>maxSegs) hi*=2;
  best=fitCurve(points,hi);let lo=0;
  for(let i=0;i<48;i++){const mid=(lo+hi)/2,c=fitCurve(points,mid);if(c.length<=maxSegs){best=c;hi=mid;}else lo=mid;if(hi-lo<1e-3)break;}
  return pin(best,points);
}
function pin(curves,pts){if(curves.length){curves[0][0]=pts[0];curves[curves.length-1][3]=pts[pts.length-1];}return curves;}

// ====================================================================
// 1) load string specs from the SVG
// ====================================================================
function attr(tag,n){const m=tag.match(new RegExp('\\b'+n+'="([^"]+)"'));return m?m[1]:null;}
function loadSpecs(file){
  const svg=fs.readFileSync(file,"utf8");
  const vb=(attr(svg,"viewBox")||"0 0 800 600").split(/[\s,]+/).map(Number);
  const H=vb[3];
  const specs=[];
  for(const m of svg.matchAll(/<line\b[^>]*?\/?>/g)){
    const t=m[0];
    if(/data-role="s-axis"/.test(t)) continue;
    const x1=+attr(t,"x1"),y1=+attr(t,"y1"),x2=+attr(t,"x2"),y2=+attr(t,"y2");
    if([x1,y1,x2,y2].some(isNaN)) continue;
    const dia=parseFloat(attr(t,"data-dia")||attr(t,"stroke-width")||"1");
    const len=parseFloat(attr(t,"data-len")||String(Math.abs(y2-y1)));
    specs.push({ x:x1, dia, len,
      note:attr(t,"data-note")||"", color:attr(t,"stroke")||"#000",
      ten:parseFloat(attr(t,"data-ten")||"0") });
  }
  specs.sort((a,b)=>a.x-b.x);
  return { specs, H };
}

// ====================================================================
// build the harp
// ====================================================================
function build(){
  const { specs, H } = loadSpecs(CONFIG.input);

  // 2) air gap: re-space x by a constant edge-to-edge gap (diameter-aware)
  let prevX = specs[0].x;
  specs.forEach((s,i)=>{ if(i===0){ s.X=prevX; return; }
    s.X = prevX + specs[i-1].dia/2 + CONFIG.airGap + s.dia/2; prevX = s.X; });

  // 3) alignment in Y-up (origin bottom-left). Reference from a flat band.
  const maxLen = Math.max(...specs.map(s=>s.len));
  specs.forEach(s=>{
    let baseZ, topZ;                          // baseZ = bottom end, topZ = upper end
    if(CONFIG.align==="bottom"){ baseZ=0; topZ=s.len; }
    else if(CONFIG.align==="middle"){ const c=maxLen/2; baseZ=c-s.len/2; topZ=c+s.len/2; }
    else { topZ=maxLen; baseZ=maxLen-s.len; }  // "top": tops level at maxLen
    s.baseZ=baseZ; s.topZ=topZ;
  });

  const harp = { units: makerjs.unitType.Millimeter, models:{}, paths:{} };

  // strings as vertical lines (X spacing, baseZ..topZ)
  const strs={ paths:{} };
  specs.forEach((s,i)=>{ strs.paths["s"+i]=new makerjs.paths.Line([s.X,s.baseZ],[s.X,s.topZ]); });
  harp.models.strings=strs;

  // 4) fit a Bezier through the bottoms (node-count controlled, smooth joins)
  const bottoms = specs.map(s=>[s.X, s.baseZ]);
  const bottomCurves = fitCurveMaxNodes(bottoms, CONFIG.fitNodes);
  harp.models.soundboard = bezierModel(bottomCurves, "soundboard");

  // 5) spine: a neck curve over the tops + connectors closing the frame
  let topCurves = null;
  if(CONFIG.spine){
    const tops = specs.map(s=>[s.X, s.topZ]);
    topCurves = fitCurveMaxNodes(tops, CONFIG.fitNodes);
    harp.models.neck = bezierModel(topCurves, "neck");
    // connect neck<->soundboard ends to suggest pillar/base (placeholder frame)
    const nStart=topCurves[0][0], nEnd=topCurves[topCurves.length-1][3];
    const sStart=bottomCurves[0][0], sEnd=bottomCurves[bottomCurves.length-1][3];
    harp.models.frame={ paths:{
      pillar:new makerjs.paths.Line(nEnd, sEnd),   // treble side
      base:new makerjs.paths.Line(sStart, nStart), // bass side
    }};
  }

  // 6) lemicons -- pending definition
  if(CONFIG.lemicons){ /* TODO once "lemicon" is defined */ }

  return { harp, specs, bottomCurves, topCurves };
}

function bezierModel(curves, name){
  const m={ models:{} };
  curves.forEach((c,i)=>{ m.models[name+i]=new makerjs.models.BezierCurve(c[0],c[1],c[2],c[3]); });
  return m;
}

// ====================================================================
// export
// ====================================================================
function main(){
  const { harp, specs, bottomCurves, topCurves } = build();
  const svg = makerjs.exporter.toSVG(harp, { units: makerjs.unitType.Millimeter });
  const dxf = makerjs.exporter.toDXF(harp, { units: makerjs.unitType.Millimeter });
  fs.writeFileSync(path.join(__dirname,"harp.svg"), svg);
  fs.writeFileSync(path.join(__dirname,"harp.dxf"), dxf);

  const ext = makerjs.measure.modelExtents(harp);
  const f1 = n => n.toFixed(1);
  console.log(`align=${CONFIG.align}  airGap=${CONFIG.airGap}  fitNodes=${CONFIG.fitNodes}`);
  console.log(`strings        : ${specs.length}  (X ${f1(specs[0].X)}..${f1(specs[specs.length-1].X)})`);
  console.log(`soundboard     : ${bottomCurves.length} cubic segment(s) / ${bottomCurves.length+1} nodes (endpoints pinned)`);
  if(topCurves) console.log(`neck           : ${topCurves.length} cubic segment(s) / ${topCurves.length+1} nodes`);
  console.log(`extents (mm)   : ${f1(ext.width)} x ${f1(ext.height)}  (origin bottom-left, +X right, +Z up)`);
  console.log("wrote          : harp.svg, harp.dxf");
}

main();
