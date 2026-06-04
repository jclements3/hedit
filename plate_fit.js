#!/usr/bin/env node
// plate_fit.js — JS port of minarea_bezier.py (ribbon base, greedy area-min polish, constraints).
// Standalone test harness: reads border.csv (x,z), reproduces plate.svg. The same core
// (everything below the I/O) is what gets dropped into hedit as fitPlate().
"use strict";
const fs = require("fs");

// ---------- vector helpers ----------
const sub = (a,b)=>[a[0]-b[0],a[1]-b[1]];
const add = (a,b)=>[a[0]+b[0],a[1]+b[1]];
const mul = (a,s)=>[a[0]*s,a[1]*s];
const len = a=>Math.hypot(a[0],a[1]);
const norm = a=>{const l=len(a)||1;return [a[0]/l,a[1]/l];};

// ---------- cubic bezier ----------
function bez(c,u){const t=1-u;return [
  t*t*t*c[0][0]+3*t*t*u*c[1][0]+3*t*u*u*c[2][0]+u*u*u*c[3][0],
  t*t*t*c[0][1]+3*t*t*u*c[1][1]+3*t*u*u*c[2][1]+u*u*u*c[3][1]];}

function curvePolygon(curves, per){
  const out=[];
  for(const c of curves) for(let i=0;i<per;i++) out.push(bez(c,i/per));
  return out;
}

// ---------- polygon geometry (replaces shapely) ----------
function polyArea(p){let a=0;for(let i=0;i<p.length;i++){const b=p[(i+1)%p.length];a+=p[i][0]*b[1]-b[0]*p[i][1];}return Math.abs(a)/2;}
function pointInPoly(pt,p){let c=false;for(let i=0,j=p.length-1;i<p.length;j=i++){
  const xi=p[i][0],yi=p[i][1],xj=p[j][0],yj=p[j][1];
  if(((yi>pt[1])!==(yj>pt[1]))&&(pt[0]<(xj-xi)*(pt[1]-yi)/(yj-yi)+xi))c=!c;}return c;}
function distToSeg(pt,a,b){const ab=sub(b,a),ap=sub(pt,a);const d=ab[0]*ab[0]+ab[1]*ab[1]||1;
  let t=(ap[0]*ab[0]+ap[1]*ab[1])/d; t=Math.max(0,Math.min(1,t));
  return len(sub(pt,[a[0]+ab[0]*t,a[1]+ab[1]*t]));}
function distToPolyline(pt,p){let m=Infinity;for(let i=0;i<p.length;i++){const d=distToSeg(pt,p[i],p[(i+1)%p.length]);if(d<m)m=d;}return m;}

// Uniform-grid accelerator over a closed polyline: edges bucketed into square cells (for nearest-
// segment distance) and into y-rows (for the ray-cast inside test). Replaces the O(dots*edges)
// scan in evaluate with O(dots) lookups — same answers, ~30x fewer ops.
function makeAccel(poly, cell){
  const n=poly.length;
  let minx=Infinity,miny=Infinity,maxx=-Infinity,maxy=-Infinity;
  for(const p of poly){if(p[0]<minx)minx=p[0];if(p[0]>maxx)maxx=p[0];if(p[1]<miny)miny=p[1];if(p[1]>maxy)maxy=p[1];}
  const gx=i=>Math.floor((i-minx)/cell), gy=i=>Math.floor((i-miny)/cell);
  const cells=new Map(), rows=new Map();
  const addC=(x,y,e)=>{const k=x+","+y;let a=cells.get(k);if(!a)cells.set(k,a=[]);a.push(e);};
  const addR=(y,e)=>{let a=rows.get(y);if(!a)rows.set(y,a=[]);a.push(e);};
  for(let i=0;i<n;i++){const a=poly[i],b=poly[(i+1)%n];
    const x0=Math.min(gx(a[0]),gx(b[0])),x1=Math.max(gx(a[0]),gx(b[0]));
    const y0=Math.min(gy(a[1]),gy(b[1])),y1=Math.max(gy(a[1]),gy(b[1]));
    for(let X=x0;X<=x1;X++)for(let Y=y0;Y<=y1;Y++)addC(X,Y,i);
    for(let Y=y0;Y<=y1;Y++)addR(Y,i);}
  function nearest(pt){            // min distance from pt to any edge (expanding cell rings)
    const cx=gx(pt[0]),cy=gy(pt[1]);let best=Infinity;
    for(let r=0;r<64;r++){
      const seen=new Set();
      for(let X=cx-r;X<=cx+r;X++)for(let Y=cy-r;Y<=cy+r;Y++){
        if(r>0&&X>cx-r&&X<cx+r&&Y>cy-r&&Y<cy+r)continue;   // only the new ring
        const a=cells.get(X+","+Y);if(!a)continue;
        for(const e of a){if(seen.has(e))continue;seen.add(e);
          const d=distToSeg(pt,poly[e],poly[(e+1)%n]);if(d<best)best=d;}}
      if(best<=r*cell)break;       // closer than the next ring could contain -> done
    }
    return best;
  }
  function inside(pt){             // ray to +x, count crossings among edges in this y-row
    const a=rows.get(gy(pt[1]));if(!a)return false;let c=false;
    for(const i of a){const A=poly[i],B=poly[(i+1)%n];const yi=A[1],yj=B[1],xi=A[0],xj=B[0];
      if(((yi>pt[1])!==(yj>pt[1]))&&(pt[0]<(xj-xi)*(pt[1]-yi)/(yj-yi)+xi))c=!c;}
    return c;
  }
  return {nearest,inside};
}
// ---------- evaluate: area, min signed clearance, valid ----------
function evaluate(curves, pts, margin, per){
  const poly=curvePolygon(curves,per);
  const area=polyArea(poly);
  const acc=makeAccel(poly, Math.max(8,margin));
  let mn=Infinity, allIn=true;
  for(const q of pts){
    const d=acc.nearest(q);
    const inside=acc.inside(q);
    if(!inside)allIn=false;
    const s=inside?d:-d;
    if(s<mn)mn=s;
  }
  const valid=allIn && mn>=margin-1e-3;
  return {area, mn, valid};
}
function exactMinClear(curves, pts, per){
  const samp=curvePolygon(curves,per);
  let mn=Infinity;
  for(const q of pts){let b=Infinity;for(const s of samp){const d=Math.hypot(s[0]-q[0],s[1]-q[1]);if(d<b)b=d;}if(b<mn)mn=b;}
  return mn;
}

// ---------- convex hull (Andrew), CCW ----------
function hull(pts){
  const p=pts.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  const cr=(o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);
  const lo=[];for(const q of p){while(lo.length>=2&&cr(lo[lo.length-2],lo[lo.length-1],q)<=0)lo.pop();lo.push(q);}
  const up=[];for(let i=p.length-1;i>=0;i--){const q=p[i];while(up.length>=2&&cr(up[up.length-2],up[up.length-1],q)<=0)up.pop();up.push(q);}
  return lo.slice(0,-1).concat(up.slice(0,-1));
}
// outward offset of a convex CCW polygon by r (parallel edges + corner arcs)
function offsetConvex(H,r){
  const n=H.length,out=[];
  for(let i=0;i<n;i++){
    const a=H[i],b=H[(i+1)%n],prev=H[(i-1+n)%n];
    const e=norm(sub(b,a)),nx=e[1],ny=-e[0];
    const pe=norm(sub(a,prev)),pnx=pe[1],pny=-pe[0];
    let a0=Math.atan2(pny,pnx),a1=Math.atan2(ny,nx);while(a1<a0)a1+=2*Math.PI;
    const steps=Math.max(2,Math.ceil((a1-a0)/0.2));
    for(let k=0;k<=steps;k++){const t=a0+(a1-a0)*k/steps;out.push([a[0]+r*Math.cos(t),a[1]+r*Math.sin(t)]);}
    out.push([a[0]+nx*r,a[1]+ny*r],[b[0]+nx*r,b[1]+ny*r]);
  }
  return out;
}
function resampleClosed(P,m){
  const seg=[];let total=0;
  for(let i=0;i<P.length;i++){const d=len(sub(P[(i+1)%P.length],P[i]));seg.push(d);total+=d;}
  const out=[];let k=0,acc=0;
  for(let j=0;j<m;j++){const target=total*j/m;while(k<P.length&&acc+seg[k]<target){acc+=seg[k];k++;}
    const a=P[k%P.length],b=P[(k+1)%P.length],f=seg[k%P.length]?(target-acc)/seg[k%P.length]:0;
    out.push([a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f]);}
  return out;
}
// closed Catmull-Rom -> cubic bezier seed
function closedBezierSeed(K){
  const n=K.length,segs=[];
  for(let i=0;i<n;i++){const p0=K[(i-1+n)%n],p1=K[i],p2=K[(i+1)%n],p3=K[(i+2)%n];
    segs.push([p1,[p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6],
                  [p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6],p2]);}
  return segs;
}

// ---------- curvature-weighted seed (port of closed_fit + Schneider _generate_bezier) ----------
const _b0=u=>{const t=1-u;return t*t*t;}, _b1=u=>{const t=1-u;return 3*u*t*t;},
      _b2=u=>{const t=1-u;return 3*u*u*t;}, _b3=u=>u*u*u;
function chordParam(pts){const u=[0];for(let i=1;i<pts.length;i++)u.push(u[i-1]+len(sub(pts[i],pts[i-1])));
  const tot=u[u.length-1];return tot?u.map(x=>x/tot):u.map(()=>0);}
// least-squares cubic with fixed endpoints + fixed end-tangent directions (Graphics Gems 1990)
function genBezier(pts,prm,lt,rt){
  const p0=pts[0],pN=pts[pts.length-1];
  let C00=0,C01=0,C11=0,X0=0,X1=0;
  for(let i=0;i<pts.length;i++){const u=prm[i];
    const A0=mul(lt,_b1(u)),A1=mul(rt,_b2(u));
    C00+=A0[0]*A0[0]+A0[1]*A0[1];C01+=A0[0]*A1[0]+A0[1]*A1[1];C11+=A1[0]*A1[0]+A1[1]*A1[1];
    const base=[_b0(u)*p0[0]+_b1(u)*p0[0]+_b2(u)*pN[0]+_b3(u)*pN[0],
                _b0(u)*p0[1]+_b1(u)*p0[1]+_b2(u)*pN[1]+_b3(u)*pN[1]];
    const tmp=sub(pts[i],base);X0+=A0[0]*tmp[0]+A0[1]*tmp[1];X1+=A1[0]*tmp[0]+A1[1]*tmp[1];}
  const detC=C00*C11-C01*C01, al=detC?(X0*C11-X1*C01)/detC:0, ar=detC?(C00*X1-C01*X0)/detC:0;
  const segLen=len(sub(p0,pN)),eps=1e-6*segLen;
  let h1,h2;
  if(al<eps||ar<eps){h1=add(p0,mul(lt,segLen/3));h2=add(pN,mul(rt,segLen/3));}
  else{h1=add(p0,mul(lt,al));h2=add(pN,mul(rt,ar));}
  return [p0.slice(),h1,h2,pN.slice()];
}
function tangentAt(D,i,delta=3){const nd=D.length;const v=sub(D[(i+delta)%nd],D[(i-delta+nd)%nd]);
  const l=len(v);return l>0?[v[0]/l,v[1]/l]:[1,0];}
// pick n anchors on closed polyline D by an (arclen + K*|turning|) metric so caps/corners attract nodes
function anchorIndices(D,n,K){
  const nd=D.length,seglen=[],dth=[];
  for(let i=0;i<nd;i++){const nxt=D[(i+1)%nd],prv=D[(i-1+nd)%nd];
    seglen.push(len(sub(nxt,D[i])));
    const a1=Math.atan2(D[i][1]-prv[1],D[i][0]-prv[0]),a2=Math.atan2(nxt[1]-D[i][1],nxt[0]-D[i][0]);
    dth.push(Math.abs(((a2-a1+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI));}
  const cum=[0];for(let i=0;i<nd;i++)cum.push(cum[i]+seglen[i]+K*dth[i]);
  const tot=cum[nd];const set=new Set();
  for(let j=0;j<n;j++){const t=tot*j/n;let lo=0,hi=cum.length;
    while(lo<hi){const m=(lo+hi)>>1;if(cum[m]<t)lo=m+1;else hi=m;}set.add(lo%nd);}
  let idx=[...set].sort((a,b)=>a-b);
  while(idx.length<n){let g=-1,kk=0;
    for(let k=0;k<idx.length;k++){const gap=((idx[(k+1)%idx.length]-idx[k])%nd+nd)%nd;if(gap>g){g=gap;kk=k;}}
    const ins=(idx[kk]+Math.floor(g/2))%nd;if(set.has(ins))break;set.add(ins);idx=[...set].sort((a,b)=>a-b);}
  return idx.slice(0,n);
}
function closedFit(boundary,n,K){
  const D=resampleClosed(boundary,Math.max(400,n*40));
  const idx=anchorIndices(D,n,K),nd=D.length,curves=[];
  for(let k=0;k<n;k++){const i0=idx[k],i1=idx[(k+1)%n];
    let seg=i1>i0?D.slice(i0,i1+1):D.slice(i0).concat(D.slice(0,i1+1));
    if(seg.length<2)seg=[D[i0],D[i1]];
    const left=tangentAt(D,i0),right=mul(tangentAt(D,i1),-1);
    const bez=genBezier(seg,chordParam(seg),left,right);
    bez[0]=D[i0].slice();bez[3]=D[i1].slice();curves.push(bez);}
  return curves;
}
function symmetrize(cv){const {A,phi,lin,lout}=toParams(cv);const L=A.map((_,k)=>0.5*(lin[k]+lout[k]));return build(A,phi,L);}
// smallest outward offset d>=margin giving a valid n-node fit, for a fixed curvature weight K
function fitMinOffset(ribbonDense,pts,margin,n,K,per){
  const fitAt=d=>{let cv=symmetrize(closedFit(offsetClosed(ribbonDense,d),n,K));const e=evaluate(cv,pts,margin,per);return {cv,a:e.area,ok:e.valid};};
  let lo=margin,hi=margin,r=fitAt(hi);
  while(!r.ok){hi*=1.18;r=fitAt(hi);if(hi>margin*8)break;}
  for(let i=0;i<16;i++){const mid=0.5*(lo+hi);if(fitAt(mid).ok)hi=mid;else lo=mid;}
  return fitAt(hi);
}
// sweep curvature weights, keep the smallest-area valid fit
function bestInitialFit(ribbonDense,pts,margin,n,per){
  let best=null;
  for(const K of [4,8,12,16,22,30,45,70]){const r=fitMinOffset(ribbonDense,pts,margin,n,K,per);
    if(r.ok && (!best||r.a<best.a))best={cv:r.cv,a:r.a};}
  return best;
}

// ---------- params <-> curves ----------
function toParams(curves){
  const n=curves.length, A=[],phi=[],lin=[],lout=[];
  for(let k=0;k<n;k++){
    const outDir=sub(curves[k][1],curves[k][0]);
    const inDir=sub(curves[k][0],curves[(k-1+n)%n][2]);
    const t=add(norm(outDir),norm(inDir));
    A.push(curves[k][0].slice());
    phi.push(Math.atan2(t[1],t[0]));
    lout.push(len(outDir)); lin.push(len(inDir));
  }
  return {A,phi,lin,lout};
}
function build(A,phi,L,hcap=0.95){
  const n=A.length,u=phi.map(p=>[Math.cos(p),Math.sin(p)]),curves=[];
  for(let k=0;k<n;k++){const kn=(k+1)%n;const chord=len(sub(A[kn],A[k]));
    const lo=Math.min(L[k],hcap*chord),li=Math.min(L[kn],hcap*chord);
    curves.push([A[k].slice(),add(A[k],mul(u[k],lo)),sub(A[kn],mul(u[kn],li)),A[kn].slice()]);}
  return curves;
}

// ---------- greedy area-min polish (symmetric handles) ----------
function polish(curves, pts, centroid, margin, opts){
  opts=opts||{};
  const fixed=new Set(opts.fixed||[]);
  const circle=opts.circle||{};                 // {idx:[cx,cy,R]}
  const fixedAngles=opts.fixedAngles||{};       // {idx:radians}
  const per=opts.per||140, maxIters=opts.maxIters||80;
  const n=curves.length;
  let {A,phi,lin,lout}=toParams(curves);
  let L=A.map((_,k)=>0.5*(lin[k]+lout[k]));
  for(const k in fixedAngles) phi[+k]=fixedAngles[+k];
  const th={};for(const k in circle){const[cx,cy]=circle[k];th[k]=Math.atan2(A[k][1]-cy,A[k][0]-cx);}
  const placeCircle=()=>{for(const k in circle){const[cx,cy,R]=circle[k];A[+k]=[cx+R*Math.cos(th[k]),cy+R*Math.sin(th[k])];}};
  const buildNow=()=>{placeCircle();return build(A,phi,L);};
  const score=()=>{const e=evaluate(buildNow(),pts,margin,per);return [Math.min(e.mn,margin),-e.area];};
  const better=(a,b)=>a[0]>b[0]||(a[0]===b[0]&&a[1]>b[1]);
  let best=score();
  const steps=[[6,.10,8],[3,.05,4],[1.5,.025,2],[.6,.01,1]];
  for(let it=0;it<maxIters;it++){
    let improved=false;
    for(const[ds,as,ls] of steps){
      for(let k=0;k<n;k++){
        if(fixed.has(k))continue;
        if(k in circle){const dth=ds/circle[k][2];
          for(const s of[dth,-dth]){const old=th[k];th[k]+=s;const sc=score();if(better(sc,best)){best=sc;improved=true;}else th[k]=old;}
          continue;}
        const d=norm(sub(centroid,A[k]));
        let old=A[k].slice();A[k]=add(A[k],mul(d,ds));let sc=score();if(better(sc,best)){best=sc;improved=true;}else A[k]=old;
        for(let ax=0;ax<2;ax++)for(const s of[ds,-ds]){old=A[k].slice();A[k][ax]+=s;sc=score();if(better(sc,best)){best=sc;improved=true;}else A[k]=old;}
      }
      for(let k=0;k<n;k++){if(k in fixedAngles)continue;
        for(const s of[as,-as]){const old=phi[k];phi[k]+=s;const sc=score();if(better(sc,best)){best=sc;improved=true;}else phi[k]=old;}}
      for(let k=0;k<n;k++){const cap=1.2*Math.max(len(sub(A[(k+1)%n],A[k])),len(sub(A[k],A[(k-1+n)%n])));
        for(const s of[ls,-ls]){const old=L[k];L[k]=Math.min(cap,Math.max(1,L[k]+s));const sc=score();if(better(sc,best)){best=sc;improved=true;}else L[k]=old;}}
    }
    if(!improved)break;
  }
  return buildNow();
}

// outward offset of a closed (possibly concave) polygon by d: each vertex moves along the
// average of its two adjacent right-hand edge normals; flip if that shrinks the area.
function offsetClosed(pts,d){
  const n=pts.length;
  const off=s=>{const r=[];for(let i=0;i<n;i++){const a=pts[(i-1+n)%n],b=pts[i],c=pts[(i+1)%n];
    const e1=norm(sub(b,a)),e2=norm(sub(c,b));
    const nrm=norm(add([e1[1],-e1[0]],[e2[1],-e2[0]]));r.push(add(b,mul(nrm,s*d)));}return r;};
  const a=off(1);return polyArea(a)>=polyArea(pts)?a:off(-1);
}

// ---------- solve ----------
function solve(allp, pins, sharps, opts){
  const margin=opts.margin, eff=margin+(opts.safety||0.05), N=opts.nodes||8;
  // ribbon base = pins(asc) + sharps(desc): preserves the bass->treble->bass traversal so node
  // numbering walks the upper (pin) edge then the lower (sharp) edge. Seed = ribbon densified,
  // offset outward by eff, resampled to N anchors, closed Catmull-Rom bezier.
  const per=opts.per||96;
  const ribbon=pins.concat(sharps.slice().reverse());
  const dense=resampleClosed(ribbon,Math.max(160,N*20));
  let knots=resampleClosed(offsetClosed(dense,opts.seedOff||eff),N);
  let cv=opts.seedCurves || closedBezierSeed(knots);
  // rotate so node 0 = anchor nearest start
  if(opts.start){const s=opts.start;let bi=0,bd=Infinity;
    cv.forEach((c,i)=>{const d=len(sub(c[0],s));if(d<bd){bd=d;bi=i;}});cv=cv.slice(bi).concat(cv.slice(0,bi));}
  const centroid=(()=>{const p=curvePolygon(cv,200);let x=0,y=0;for(const q of p){x+=q[0];y+=q[1];}return [x/p.length,y/p.length];})();
  const fa={};for(const k in (opts.angles||{}))fa[k]=opts.angles[k]*Math.PI/180;
  const maxIters=opts.maxIters||80;
  // 1) unconstrained polish
  cv=polish(cv,allp,centroid,eff,{fixedAngles:fa,per,maxIters});
  // 2) circle / perimeter homes
  const free=new Set(opts.free||[]);
  const fixedCenters=opts.oncircle||{};         // {idx:[cx,cy]}
  let {A,phi,lin,lout}=toParams(cv);let L=A.map((_,k)=>0.5*(lin[k]+lout[k]));
  const circle={};
  for(let i=0;i<N;i++){
    if(free.has(i))continue;
    let c;
    if(i in fixedCenters)c=fixedCenters[i];
    else if(opts.perimeter){let bj=0,bd=Infinity;allp.forEach((p,j)=>{const d=len(sub(p,A[i]));if(d<bd){bd=d;bj=j;}});c=allp[bj];}
    else continue;
    const v=norm(sub(A[i],c));A[i]=add(c,mul(v,eff));circle[i]=[c[0],c[1],eff];
  }
  cv=build(A,phi,L);
  cv=polish(cv,allp,centroid,eff,{circle,fixedAngles:fa,per,maxIters});
  return cv;
}

// ---------- I/O (test harness only) ----------
function pathD(curves){let s=`M ${curves[0][0][0].toFixed(3)} ${curves[0][0][1].toFixed(3)}`;
  for(const c of curves)s+=` C ${c[1][0].toFixed(3)} ${c[1][1].toFixed(3)} ${c[2][0].toFixed(3)} ${c[2][1].toFixed(3)} ${c[3][0].toFixed(3)} ${c[3][1].toFixed(3)}`;
  return s+" Z";}

if(require.main===module){
  const rows=fs.readFileSync(process.argv[2]||"border.csv","utf8").trim().split(/\r?\n/);
  const h=rows[0].split(","),ri=h.indexOf("role"),ni=h.indexOf("num"),xi=h.indexOf("x"),zi=h.indexOf("z"),noti=h.indexOf("note");
  const dots=rows.slice(1).map(r=>{const c=r.split(",");return {role:c[ri],num:+c[ni],note:c[noti],p:[+c[xi],+c[zi]]};});
  const pins=dots.filter(d=>d.role==="pin").sort((a,b)=>a.num-b.num);
  const sharps=dots.filter(d=>d.role==="sharp").sort((a,b)=>a.num-b.num);
  const allp=dots.map(d=>d.p);
  const byNote=(role,note)=>dots.find(d=>d.role===role&&d.note.toUpperCase()===note).p;
  const C1p=byNote("pin","C1"),C2p=byNote("pin","C2"),D7p=byNote("pin","D7"),A1s=byNote("sharp","A1");
  const cv=solve(allp,pins.map(d=>d.p),sharps.map(d=>d.p),{
    margin:13,safety:0.05,nodes:8,start:C1p,perimeter:true,free:[4],
    oncircle:{0:C1p,1:C2p,3:D7p,7:A1s},angles:{1:-45,5:142},
  });
  const area=polyArea(curvePolygon(cv,400));
  const mc=exactMinClear(cv,allp,1500);
  let allIn=true;{const poly=curvePolygon(cv,400);for(const q of allp)if(!pointInPoly(q,poly))allIn=false;}
  console.log("nodes:",cv.length,"area:",Math.round(area),"exact min clear:",mc.toFixed(2),"allInside:",allIn);
  console.log(pathD(cv));
}
module.exports={solve,curvePolygon,polyArea,exactMinClear,pointInPoly,pathD};
