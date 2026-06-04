#!/usr/bin/env python3
"""
harp_sweep.py - Build a harp frame as a single closed sweep.

WHAT IT TAKES (the three inputs you supply):
  1. INNER_PATH_XZ : the inner XZ loop (the dimple line of the limacon runs
                     and the inner side of the superellipse runs). Comes from
                     the XZ-plane chat; a FAKE harp outline is built in below.
  2. W_KNOTS       : the Y half-width law (the "minor-axis control curve"),
                     given as (u, half_width) knots, u = fraction around loop.
  3. region starts : transition points (sound_chamber -> rear_shoulder ->
                     neck -> front_shoulder -> pillar -> back to sound_chamber),
                     tagged on the path control points.

WHAT IT DOES:
  At every station u around the loop it places a cross-section in the plane
  spanned by  Nout(u) (outward path normal, in XZ)  x  Y (world up/width):
    * sound_chamber / shoulders / neck  -> limacon  (a = 2b), dimple on the path
    * pillar                            -> superellipse (n=4), inner side on path
    * front_shoulder & pillar-foot       -> smooth morph between the two
  The section is uniformly scaled so its +/-Y half-breadth = W(u). The
  soundchamber is symmetric about Y; through the neck the +Y half is clipped
  to 0 (a half-section), ramped out across the rear shoulder and back across
  the front shoulder.

OUTPUTS:
  harp_3d.html         orbitable Three.js sweep (animated section)
  harp_side.svg/.png   XZ side elevation (inner path + outer bulge, regions)
  harp_width.svg/.png  the Y-width development (the minor-axis curve unrolled)
"""

import json
import numpy as np
from scipy.interpolate import CubicSpline
import cairosvg

# ===========================================================================
# INPUT 1 - INNER XZ PATH  (fake harp outline; replace with the real path)
#   Each row: (x, z, region_tag_or_None). A tag marks where a region STARTS.
#   Loop order: soundboard up -> rear shoulder -> neck -> front shoulder ->
#               pillar down -> base -> (closes to soundboard start).
# ===========================================================================
INNER_PATH_XZ = [
    (2.60, 0.30, 'sound_chamber'),
    (3.15, 2.40, None), (3.70, 4.60, None), (4.10, 6.20, None),
    (4.25, 6.90, 'rear_shoulder'),
    (4.00, 7.25, None),
    (3.40, 7.55, 'neck'),
    (2.50, 7.75, None), (1.60, 7.70, None),
    (1.00, 7.45, 'front_shoulder'),
    (0.65, 7.05, None),
    (0.50, 6.60, 'pillar'),
    (0.40, 4.50, None), (0.38, 2.20, None), (0.50, 0.70, None),
    (1.30, 0.25, None),
]

# ===========================================================================
# INPUT 2 - Y HALF-WIDTH LAW (minor-axis control curve), periodic in u
# ===========================================================================
W_KNOTS = [(0.00, 1.20), (0.30, 0.78), (0.55, 0.46), (0.66, 0.34),
           (0.74, 0.46), (0.88, 0.66), (1.00, 1.20)]

# ===========================================================================
# INPUT 3 - region morph / clip behaviour
#   shape: limacon everywhere except pillar; morph across front_shoulder and
#   across the pillar-foot (closing). +Y clip: ramps off across rear_shoulder,
#   stays off through neck, ramps on across front_shoulder.
# ===========================================================================
SE_N = 4.0          # superellipse exponent for the pillar
N_SEC = 84          # points per cross-section
M_STA = 320         # stations around the loop

# ---------------------------------------------------------------------------
# Build the closed path spline + arc-length param + region boundaries
# ---------------------------------------------------------------------------
pts = np.array([(x, z) for x, z, _ in INNER_PATH_XZ], float)
tags = [t for _, _, t in INNER_PATH_XZ]
closed = np.vstack([pts, pts[0]])
seg = np.hypot(*np.diff(closed, axis=0).T)
tcum = np.concatenate([[0], np.cumsum(seg)])
L = tcum[-1]
csx = CubicSpline(tcum, closed[:, 0], bc_type='periodic')
csz = CubicSpline(tcum, closed[:, 1], bc_type='periodic')

REG_ORDER = ['sound_chamber', 'rear_shoulder', 'neck', 'front_shoulder', 'pillar']
Tf = {}
for i, tg in enumerate(tags):
    if tg in REG_ORDER:
        Tf[tg] = tcum[i] / L
Tsc, Trs, Tne, Tfs, Tpi = (Tf[r] for r in REG_ORDER)
Tclose = Tpi + 0.72*(1.0 - Tpi)        # SE->limacon morph window (pillar foot)
print("region fractions:", {k: round(v, 3) for k, v in Tf.items()},
      " Tclose=", round(Tclose, 3))

u = np.linspace(0, 1, M_STA, endpoint=False)
Px, Pz = csx(u*L), csz(u*L)
Tx, Tz = csx(u*L, 1), csz(u*L, 1)
Tn = np.hypot(Tx, Tz)
nx, nz = -Tz/Tn, Tx/Tn                  # left normal
cx_, cz_ = pts[:, 0].mean(), pts[:, 1].mean()
flip = ((Px - cx_)*nx + (Pz - cz_)*nz) < 0     # orient outward (away from centroid)
nx = np.where(flip, -nx, nx); nz = np.where(flip, -nz, nz)

# ---------------------------------------------------------------------------
# Control scalars along the loop
# ---------------------------------------------------------------------------
def smooth(x): x = np.clip(x, 0, 1); return x*x*(3 - 2*x)

def Wlaw():
    uk = [k[0] for k in W_KNOTS]; wk = [k[1] for k in W_KNOTS]
    cs = CubicSpline(uk, wk, bc_type='periodic')
    return cs(u)

def morph_law():
    m = np.zeros_like(u)
    fs = (u >= Tfs) & (u < Tpi)                       # front shoulder: lim->SE
    m[fs] = smooth((u[fs] - Tfs)/(Tpi - Tfs))
    m[(u >= Tpi) & (u < Tclose)] = 1.0                # pillar: SE
    cl = u >= Tclose                                  # foot: SE->lim
    m[cl] = 1.0 - smooth((u[cl] - Tclose)/(1.0 - Tclose))
    return m

def yplus_law():
    yp = np.ones_like(u)
    rs = (u >= Trs) & (u < Tne)                        # rear shoulder: clip off
    yp[rs] = 1.0 - smooth((u[rs] - Trs)/(Tne - Trs))
    yp[(u >= Tne) & (u < Tfs)] = 0.0                   # neck: -Y only
    fs = (u >= Tfs) & (u < Tpi)                        # front shoulder: clip on
    yp[fs] = smooth((u[fs] - Tfs)/(Tpi - Tfs))
    return yp

W, MO, YP = Wlaw(), morph_law(), yplus_law()

# ---------------------------------------------------------------------------
# Unit cross-section rings (half-breadth = 1), matched point-for-point by angle
#   local coords: (n along outward normal, y along width); inner point at n=0
# ---------------------------------------------------------------------------
def unit_limacon(m=2000):
    th = np.linspace(0, 2*np.pi, m, endpoint=False)
    r = 2 + np.cos(th)
    xr = r*np.cos(th) + 1; yr = r*np.sin(th)
    s = 1.0/yr.max()                                   # half-breadth -> 1
    return xr*s, yr*s                                  # n in [0,1.816], y in [-1,1]

def unit_super(m=2000):
    t = np.linspace(0, 2*np.pi, m, endpoint=False)
    e = 2.0/SE_N
    A = 0.90817                                        # = 1.816/2 to match limacon depth
    n = A + np.sign(np.cos(t))*np.abs(np.cos(t))**e * A
    y = np.sign(np.sin(t))*np.abs(np.sin(t))**e
    return n, y

def match(n, y, phis):
    cn, cy = n.mean(), y.mean(); ang = np.arctan2(y - cy, n - cn)
    on, oy = [], []
    for p in phis:
        k = np.abs(np.arctan2(np.sin(ang - p), np.cos(ang - p))).argmin()
        on.append(n[k]); oy.append(y[k])
    return np.array(on), np.array(oy)

phis = -np.pi + 2*np.pi*(np.arange(N_SEC) + 0.5)/N_SEC
LN, LY = match(*unit_limacon(), phis)
SN, SY = match(*unit_super(), phis)

# ---------------------------------------------------------------------------
# Assemble the swept surface
# ---------------------------------------------------------------------------
verts = np.zeros((M_STA, N_SEC, 3))
for i in range(M_STA):
    rn = (1 - MO[i])*LN + MO[i]*SN
    ry = (1 - MO[i])*LY + MO[i]*SY
    rn = rn*W[i]; ry = ry*W[i]
    ry = np.where(ry > 0, ry*YP[i], ry)                # clip +Y in the neck
    verts[i, :, 0] = Px[i] + rn*nx[i]                  # X
    verts[i, :, 1] = ry                                # Y (width / up)
    verts[i, :, 2] = Pz[i] + rn*nz[i]                  # Z

# region id per station (for colouring side view)
def region_of(uu):
    if uu < Trs: return 0          # sound_chamber
    if uu < Tne: return 1          # rear_shoulder
    if uu < Tfs: return 2          # neck
    if uu < Tpi: return 3          # front_shoulder
    return 4                       # pillar
RID = np.array([region_of(x) for x in u])

# ===========================================================================
# 2D OUTPUT A - XZ side elevation (inner path + outer bulge edge), by region
# ===========================================================================
REG_COL = ['#f0c660', '#caa24a', '#d8f0a0', '#9fd0d8', '#8fc6f0']  # sc,rs,neck,fs,pillar
def write_side(path):
    depth = 1.81634*W                                   # bulge tip distance along N
    outx, outz = Px + depth*nx, Pz + depth*nz
    allx = np.concatenate([Px, outx]); allz = np.concatenate([Pz, outz])
    S, pad = 70.0, 70.0
    xlo, xhi = allx.min(), allx.max(); zlo, zhi = allz.min(), allz.max()
    W_ = pad + (xhi - xlo)*S + pad; H_ = pad + (zhi - zlo)*S + pad
    px = lambda x: pad + (x - xlo)*S
    pz = lambda z: H_ - pad - (z - zlo)*S
    P = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f" width="%.0f" '
         'height="%.0f" font-family="Georgia, serif">' % (W_, H_, W_, H_),
         '<rect width="%.1f" height="%.1f" fill="#14110d"/>' % (W_, H_)]
    # body fill: outer edge forward + inner path back
    d = "M %.2f %.2f " % (px(outx[0]), pz(outz[0]))
    for x, z in zip(outx[1:], outz[1:]): d += "L %.2f %.2f " % (px(x), pz(z))
    for x, z in zip(Px[::-1], Pz[::-1]): d += "L %.2f %.2f " % (px(x), pz(z))
    P.append('<path d="%s Z" fill="#caa24a" fill-opacity="0.10"/>' % d)
    # inner path + outer edge, coloured by region
    for arr_x, arr_z, wd in [(Px, Pz, 3.4), (outx, outz, 2.0)]:
        for i in range(M_STA):
            j = (i + 1) % M_STA
            P.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                     'stroke-width="%s"/>' % (px(arr_x[i]), pz(arr_z[i]),
                     px(arr_x[j]), pz(arr_z[j]), REG_COL[RID[i]], wd))
    P.append('<g font-size="20" fill="#e8c46a"><text x="%.1f" y="30">'
             'Harp side elevation (XZ) · inner path + outer bulge · by region</text></g>'
             % (pad - 4))
    # legend
    names = ['sound chamber', 'rear shoulder', 'neck', 'front shoulder', 'pillar']
    for k, (nm, c) in enumerate(zip(names, REG_COL)):
        yy = H_ - pad - 18*(len(names) - k)
        P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>'
                 % (W_ - 220, yy, W_ - 188, yy, c))
        P.append('<text x="%.1f" y="%.1f" font-size="15" fill="#9c9170">%s</text>'
                 % (W_ - 180, yy + 5, nm))
    P.append('</svg>')
    svg = "\n".join(P); open(path, 'w').write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path.replace('.svg', '.png'),
                     output_width=1100)

# ===========================================================================
# 2D OUTPUT B - Y-width development (the minor-axis control curve unrolled)
# ===========================================================================
def write_width(path):
    S, pad = 900.0, 70.0
    ymax = 1.4
    W_ = pad + 1.0*S + pad; H_ = pad + 2*ymax*60 + pad
    px = lambda uu: pad + uu*S
    py = lambda yy: pad + ymax*60 - yy*60
    yplus = np.where(YP > 0, W*YP, 0.0)
    P = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f" width="%.0f" '
         'height="%.0f" font-family="Georgia, serif">' % (W_, H_, W_, H_),
         '<rect width="%.1f" height="%.1f" fill="#14110d"/>' % (W_, H_)]
    for r, c in zip([Tsc, Trs, Tne, Tfs, Tpi], REG_COL):
        P.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                 'stroke-width="1" stroke-dasharray="3,4"/>' % (px(r), py(-ymax), px(r), py(ymax), c))
    P.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#6b6048"/>'
             % (px(0), py(0), px(1), py(0)))
    def poly(uu, yy, col):
        d = "M %.2f %.2f " % (px(uu[0]), py(yy[0]))
        for a, b in zip(uu[1:], yy[1:]): d += "L %.2f %.2f " % (px(a), py(b))
        return '<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, col)
    P.append(poly(u, W, "#d8f0a0"))                    # -Y edge (full breadth)
    P.append(poly(u, -W, "#d8f0a0"))
    P.append(poly(u, np.where(YP > 0, W*YP, 0.0), "#8fc6f0"))   # +Y edge (clipped in neck)
    P.append('<g font-size="19" fill="#e8c46a"><text x="%.1f" y="28">'
             'Y-width development · -Y full (green), +Y clipped through neck (blue)</text></g>'
             % (pad - 4))
    P.append('</svg>')
    svg = "\n".join(P); open(path, 'w').write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path.replace('.svg', '.png'),
                     output_width=1100)

# ===========================================================================
# 3D OUTPUT - Three.js sweep
# ===========================================================================
def write_3d(path):
    pos = [round(float(v), 3) for v in verts.reshape(-1)]
    idx = []
    for i in range(M_STA):
        ii = (i + 1) % M_STA
        for j in range(N_SEC):
            jj = (j + 1) % N_SEC
            a = i*N_SEC + j; b = i*N_SEC + jj; c = ii*N_SEC + j; d = ii*N_SEC + jj
            idx += [a, c, b, b, c, d]
    spine = [[round(float(Px[i]), 3), 0.0, round(float(Pz[i]), 3)] for i in range(M_STA)]
    data = {'N': N_SEC, 'M': M_STA, 'pos': pos, 'idx': idx, 'spine': spine,
            'center': [float(Px.mean()), float(verts[:, :, 1].mean()), float(Pz.mean())]}
    open(path, 'w').write(TEMPLATE.replace('__DATA__', json.dumps(data, separators=(',', ':'))))

TEMPLATE = r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Harp sweep</title>
<style>html,body{margin:0;height:100%;background:#14110d;overflow:hidden;font-family:Georgia,serif;color:#e8c46a;}
#c{display:block;width:100%;height:100%;}#t{position:fixed;left:18px;top:14px;font-size:19px;pointer-events:none;}
#t small{display:block;font-size:13px;color:#9c9170;}#h{position:fixed;right:18px;bottom:16px;font-size:13px;color:#6b6048;}</style>
</head><body><canvas id="c"></canvas>
<div id="t">Harp sweep · limaçon soundchamber &#8594; superellipse pillar<small>inner XZ path · Y-width law · neck clipped to &#8722;Y</small></div>
<div id="h">drag to orbit · scroll to zoom</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const D=__DATA__, N=D.N, M=D.M;
const cv=document.getElementById('c');
const rnd=new THREE.WebGLRenderer({canvas:cv,antialias:true}); rnd.setPixelRatio(Math.min(devicePixelRatio,2));
const sc=new THREE.Scene(); sc.background=new THREE.Color(0x14110d);
const cam=new THREE.PerspectiveCamera(45,1,0.1,500);
const tg=new THREE.Vector3(D.center[0],D.center[1],D.center[2]);
sc.add(new THREE.AmbientLight(0x6b5a36,0.8));
const l1=new THREE.DirectionalLight(0xffe9b0,1.05); l1.position.set(6,12,10); sc.add(l1);
const l2=new THREE.DirectionalLight(0x4a6a8a,0.5); l2.position.set(-8,-4,-7); sc.add(l2);
const g=new THREE.BufferGeometry();
g.setAttribute('position',new THREE.Float32BufferAttribute(D.pos,3));
g.setIndex(D.idx); g.computeVertexNormals();
sc.add(new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0xb8893a,metalness:0.5,roughness:0.45,transparent:true,opacity:0.55,side:THREE.DoubleSide})));
const sp=new THREE.BufferGeometry().setFromPoints(D.spine.map(p=>new THREE.Vector3(p[0],p[1],p[2])).concat([new THREE.Vector3(D.spine[0][0],0,D.spine[0][2])]));
sc.add(new THREE.Line(sp,new THREE.LineBasicMaterial({color:0xe0894a})));
// sweeping section ring
const P=D.pos; const sg=new THREE.BufferGeometry();
sg.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(N*3),3));
sc.add(new THREE.LineLoop(sg,new THREE.LineBasicMaterial({color:0xf4e3b0})));
function sweep(f){const i=Math.floor(f*M)%M, a=sg.attributes.position.array;
  for(let j=0;j<N;j++){const k=(i*N+j)*3; a[j*3]=P[k];a[j*3+1]=P[k+1];a[j*3+2]=P[k+2];}
  sg.attributes.position.needsUpdate=true;}
let th=0.7,ph=1.2,rad=18,drag=false,mx=0,my=0,idle=0;
function place(){cam.position.set(tg.x+rad*Math.sin(ph)*Math.cos(th),tg.y+rad*Math.cos(ph),tg.z+rad*Math.sin(ph)*Math.sin(th));cam.lookAt(tg);}
cv.addEventListener('pointerdown',e=>{drag=true;mx=e.clientX;my=e.clientY;idle=0;});
addEventListener('pointerup',()=>drag=false);
addEventListener('pointermove',e=>{if(!drag)return;idle=0;th-=(e.clientX-mx)*0.008;ph-=(e.clientY-my)*0.008;ph=Math.max(0.15,Math.min(Math.PI-0.15,ph));mx=e.clientX;my=e.clientY;});
cv.addEventListener('wheel',e=>{e.preventDefault();rad=Math.max(8,Math.min(60,rad*(1+Math.sign(e.deltaY)*0.08)));},{passive:false});
function rz(){const w=innerWidth,h=innerHeight;rnd.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();}
addEventListener('resize',rz);rz();
let f=0;function tick(){idle++; if(!drag&&idle>90)th+=0.0014; f=(f+0.004)%1; sweep(f); place(); rnd.render(sc,cam); requestAnimationFrame(tick);} tick();
</script></body></html>'''

if __name__ == '__main__':
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    write_side(os.path.join(base, 'harp_side.svg'))
    write_width(os.path.join(base, 'harp_width.svg'))
    write_3d(os.path.join(base, 'harp_3d.html'))
    print('wrote harp_side.svg/.png, harp_width.svg/.png, harp_3d.html  (%d verts)'
          % (M_STA*N_SEC))
