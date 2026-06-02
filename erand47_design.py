#!/usr/bin/env python3
"""erand47 — parametric design generator (CF revision; z-x profile, view along depth y).
Pipeline: strings -> air-gap spacing -> rake shear -> tip quintics (N,S)
-> deflection-governed bar heights -> bar-edge quintics (NT,NB,ST,SB)
-> tangent-matched Bezier end caps (pillar + rounded shoulder) -> rungs.
Run:  python3 erand47_design.py  ->  writes erand47.svg
"""
import numpy as np, math
from math import comb, radians, sin, cos

# ============================== DESIGN CONSTRAINTS ==============================
N_STRINGS          = 47          # C1 (bass) .. G7 (treble)
AIR_GAP_MM         = 13.0        # parallel air gap between adjacent string ODs
RAKE_DEG           = 7.0         # string rake, tops toward pillar (0 = none)
PLATE_T_MM         = 6.35        # 1/4" plate thickness (304 stainless)
PLATE_GAP_MM       = 13.0        # gap between the two plates, depth axis y
E_MPA              = 135_000.0   # CF/epoxy UD-dominant laminate, 0deg effective
UTS_MPA            = 1800.0      # CF 0deg tensile (stress check vs UTS)
FPF_MPA            = 900.0       # first-ply-failure (conservative allowable)
ILSS_MPA           = 70.0       # interlaminar/junction shear -> governs rungs & nodes
GAP_CLOSURE_MAX_MM = 1.0         # bar sizing target: max neck<->soundboard closure
INNER_BOW_GAPS     = 3           # NB-ST inner end-cap bow = 3 air gaps (string clearance)
PILLAR_OUTER_BOW   = 63.0        # NT-SB outer cap bow at C1 -> ~24 mm radial pillar depth
SHOULDER_OUTER_BOW = 20.0        # rounded treble shoulder (small bow)
SHOULDER_INNER_BOW = 13.0
PILLAR_RUNGS       = 6           # dedicated pillar cross-ties (no strings)
NECK_RUNG_OD       = 3.0         # CF rod min; string rides on a BRASS WEAR SHOE (not bare CF)
SB_RUNG_OD         = 8.0         # CF rod; BRASS EYELET drilled to string OD; string THROUGH + knot
RHO_CF             = 1.55e-3     # g/mm^3  CF/epoxy (was 8.0e-3 SS)
RHO_BRASS          = 8.5e-3      # wear shoes / eyelets only

# ----- clements47 revision: wooden eyelet (sb, unchanged) PASSES string through; the
# string then runs a dead-tail L_TAIL to a CF ANCHOR where it KNOTS. The CF frame carries
# the full axial tension; the wood carries only the perpendicular break-angle down-bearing.
BREAK_ANGLE_DEG    = 12.0        # constant break angle at every wooden eyelet (tuning knob)
L_TAIL_MM          = 30.0        # wooden eyelet -> CF anchor dead-tail length, mm
CHAMBER_DEPTH_BASS = 95.0        # wooden sound-chamber max depth into +y at the bass, mm
CHAMBER_DEPTH_TREB = 18.0        # ... tapering to a shallow depth at the treble, mm
CHAMBER_WIDTH_BASS = 150.0       # chamber half-width (across the string band) at bass, mm
CHAMBER_WIDTH_TREB = 35.0        # ... tapering narrow at the treble, mm

# ----- string lengths: the ORIGINAL Erard 47-string scale (C1 bass .. G7 treble), mm, data-num 1..47.
# Source: harpcanada.com/harpmaking/erard.htm (Erard lengths in inches x 25.4) -- IDENTICAL to
# strings.svg (verified to 0.0 mm). Monotonic C1=1514.9 .. G7=60.6; shortest two F7=70.7, G7=60.6.
# DO NOT use the "erand47 archive" array (1448.69, 30.30, 15.59, 60.61 ...) or np.linspace(...): BOTH
# are CORRUPT (treble wrong by up to ~279 mm). erand47_profile_v2.svg was built from the bad archive.
L = np.array([
 1514.9,1489.7,1464.4,1439.2,1408.9,1378.6,1348.3,1318.0,
 1282.6,1242.2,1222.0,1186.7,1110.9,1055.4,989.8,924.1,
 863.5,792.8,732.2,666.6,621.1,570.6,525.2,484.8,
 449.4,414.1,383.8,353.5,328.2,303.0,277.7,262.6,
 237.3,222.2,207.0,191.9,176.7,161.6,146.4,131.3,
 121.2,111.1,101.0,90.9,80.8,70.7,60.6])
assert L.size==N_STRINGS, "L must have N_STRINGS entries"
TENSION_LBF = np.linspace(52.693,10.976,N_STRINGS)              # linear tension schedule
DIA = np.array([1.676,1.549,1.448,1.270,1.219,1.219,1.016,1.016,0.914,2.642,2.489,2.337,
 2.184,2.057,2.057,1.930,1.676,1.676,1.549,1.549,1.270,1.270,1.270,1.143,1.143,1.143,
 1.016,1.016,1.016,0.914,0.914,0.914,0.813,0.813,0.813,0.813,0.762,0.762,0.762,0.711,
 0.711,0.660,0.635,0.635,0.635,0.635,0.635])
LB2N = 4.448222

# ============================== 1. STRING BAND (air gap) =======================
c2c = np.array([AIR_GAP_MM + (DIA[i]+DIA[i+1])/2 for i in range(N_STRINGS-1)])
xc  = np.concatenate([[0.0], np.cumsum(c2c)])      # station x of each string
ztip = L/2.0                                       # tips at +-L/2 about bisector

# ============================== 2. STRUCTURAL: bar heights =====================
# 2D frame FE (Euler-Bernoulli) sized so gap closure <= GAP_CLOSURE_MAX_MM.
# Result is the deflection-governed height profile H(station): ~17 mm at the
# ends rising to ~81 mm at the tension resultant (~290 mm from bass).
def bar_height_profile():
    # Deflection-governed heights from the 2D frame FE solve (gap closure <= 1 mm),
    # peaking at the tension resultant (~B3/C4) and tapering to the ends.
    return np.array([18.8,29.4,41.0,49.3,56.1,61.6,66.5,70.5,74.1,77.2,79.9,82.2,84.2,86.0,87.4,88.5,89.6,90.3,90.8,91.1,91.4,91.4,91.1,90.7,90.1,89.4,88.5,87.4,86.2,84.7,83.1,81.4,79.4,77.3,74.9,72.4,69.6,66.6,63.2,59.5,55.4,50.9,45.8,39.9,32.8,23.3,18.8])  # CF deflection-parity heights
H = bar_height_profile()
half = H/2.0

# ============================== 3-4. tip & bar-edge quintics ===================
def fit_quintic(xv, zv):
    u = (xv-xv[0])/(xv[-1]-xv[0])
    B = np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in u])
    A = B[:,1:5]; rhs = zv - B[:,0]*zv[0] - B[:,5]*zv[-1]
    c = np.array([zv[0], *np.linalg.lstsq(A,rhs,rcond=None)[0], zv[-1]])
    return c
def bezier(c, m=300):
    u = np.linspace(0,1,m)
    B = np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in u])
    return B@c
cz   = fit_quintic(xc, ztip)            # N/S tip curve (single quintic)
zfit = bezier(cz, len(xc) if False else 300)
# evaluate fitted tip at each station for the +-H/2 dots, then fit edges
Bx = np.array([[comb(5,k)*(1-(x:=(xx-xc[0])/(xc[-1]-xc[0])))**(5-k)*x**k
                for k in range(6)] for xx in xc])
zfit_at = Bx@cz
c_out = fit_quintic(xc, zfit_at+half)   # NT / SB (outer edges)
c_in  = fit_quintic(xc, zfit_at-half)   # NB / ST (inner edges)

# ============================== 5. tangent-matched end caps ====================
M=300; Px=np.array([k*xc[-1]/5 for k in range(6)])
uu=np.linspace(0,1,M); Bc=np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in uu])
xv=Bc@Px; co=Bc@c_out; ci=Bc@c_in
NT=co; NB=ci; ST=-ci; SB=-co
def slope(a,b,e): return (b[-1]-b[-4])/(a[-1]-a[-4]) if e=='hi' else (b[3]-b[0])/(a[3]-a[0])
def cubic(P0,P1,P2,P3,m=90):
    t=np.linspace(0,1,m)[:,None]; return (1-t)**3*P0+3*(1-t)**2*t*P1+3*(1-t)*t**2*P2+t**3*P3
def cap(xe,z0,z3,m0,m3,sg,bow):
    P0=np.array([xe,z0]);P3=np.array([xe,z3]);d0=np.array([sg,sg*m0]);d0/=np.hypot(*d0)
    d3=np.array([sg,sg*m3]);d3/=np.hypot(*d3)
    for h in np.linspace(8,320,260):
        p=cubic(P0,P0+h*d0,P3+h*d3,P3); ex=(p[:,0].max()-xe) if sg>0 else (xe-p[:,0].min())
        if ex>=bow: break
    return cubic(P0,P0+h*d0,P3+h*d3,P3)
INNER_BOW = INNER_BOW_GAPS*AIR_GAP_MM

# --- clements47: RELOCATE the lower (soundboard) CF ladder down to the ANCHOR curve.
# In UNRAKED coords the speaking strings are vertical: s_hat=(0,-1) points from neck to
# the wooden eyelet (down, away from the neck). The anchor sits L_TAIL*cos(b) further
# down in z (the in-profile drop) and is kicked L_TAIL*sin(b) into +y depth (depth view
# only). Dropping the SB/ST edges by that same dz opens room for the wooden chamber and
# moves the whole lower CF bar onto the anchor curve.
def break_angle(i):  return BREAK_ANGLE_DEG                       # deg, per-string (taperable)
_b = radians(BREAK_ANGLE_DEG)
def anchor_offset(i):                                            # (along s_hat, perp n_hat) mm
    bi = radians(break_angle(i)); return (L_TAIL_MM*cos(bi), L_TAIL_MM*sin(bi))
DZ_DROP = L_TAIL_MM*cos(_b)        # in-profile z drop (eyelet -> anchor), mm
# depth kick is into -y (the string/playing side), OPPOSITE the +y wooden chamber, so the CF
# anchor/ladder never enters the chamber cavity. The break-angle still drives the board toward +y.
D_KICK  = -L_TAIL_MM*sin(_b)       # depth kick into -y, mm (anchor clears the chamber)
SB = SB - DZ_DROP                  # relocate outer soundboard edge onto anchor curve
ST = ST - DZ_DROP                  # relocate inner soundboard edge onto anchor curve

g7={k:slope(xv,v,'hi') for k,v in dict(NT=NT,NB=NB,ST=ST,SB=SB).items()}
c1={k:slope(xv,v,'lo') for k,v in dict(NT=NT,NB=NB,ST=ST,SB=SB).items()}
G7o=cap(xc[-1],NT[-1],SB[-1],g7['NT'],g7['SB'],1,SHOULDER_OUTER_BOW)
G7i=cap(xc[-1],NB[-1],ST[-1],g7['NB'],g7['ST'],1,SHOULDER_INNER_BOW)
C1o=cap(0,SB[0],NT[0],c1['SB'],c1['NT'],-1,PILLAR_OUTER_BOW)
C1i=cap(0,ST[0],NB[0],c1['ST'],c1['NB'],-1,INNER_BOW)
outer=np.vstack([np.column_stack([xv,NT]),G7o,np.column_stack([xv,SB])[::-1],C1o])
inner=np.vstack([np.column_stack([xv,NB]),G7i,np.column_stack([xv,ST])[::-1],C1i])

# ============================== 6. RAKE (area-preserving shear) ================
# x' = x/cos - z*sin ;  z' = z*cos  (group rotate CCW + slide midpoints to horizontal)
th=radians(RAKE_DEG); Cs=cos(th); Sn=sin(th)
def rake(P): P=np.atleast_2d(P); return np.column_stack([P[:,0]/Cs-P[:,1]*Sn, P[:,1]*Cs])
Ro=rake(outer); Ri=rake(inner)
neck=rake(np.column_stack([xc,ztip])); sb=rake(np.column_stack([xc,-ztip]))

# ============================== 6b. clements47 CF ANCHORS ======================
# T per string (Newtons): the CF frame takes the FULL axial tension; the wood takes
# only the perpendicular break-angle down-bearing F_db = 2*T*sin(b/2).
T = TENSION_LBF*LB2N
def down_bearing(i):                                            # Newtons onto the wood at eyelet i
    return 2.0*T[i]*sin(radians(break_angle(i))/2.0)
def place_cf_anchors():
    # Build the CF anchor curve from the (unchanged) wooden eyelet curve `sb`.
    # In-profile (z-x): drop each eyelet by DZ_DROP along the straight string continuation
    # (s_hat=(0,-1) in unraked coords -> after rake the strings tilt, so follow neck->sb).
    # Depth (y): kick by D_KICK into +y. Returns (anchor_profile[47,2], depth_y[47]).
    s = sb - neck                                               # neck->eyelet (string) vectors
    shat = s/np.hypot(s[:,0],s[:,1])[:,None]                    # unit straight-through dirs
    along = anchor_offset(0)[0]                                 # L_TAIL*cos(b), same for all (constant b)
    anc = sb + shat*along                                       # in-profile anchor (z-x) on CF
    depth = np.full(N_STRINGS, D_KICK)                          # +y kick, depth-view only
    return anc, depth
anchor, anchor_y = place_cf_anchors()
# CF backing rib: a thin band hugging the wooden eyelet line (spreads point loads into CF).
RIB_T = 6.0                                                     # rib thickness in z, mm
rib_dir = (sb-neck); rib_dir = rib_dir/np.hypot(rib_dir[:,0],rib_dir[:,1])[:,None]
rib_in  = sb - rib_dir*1.0                                      # just behind eyelet (toward anchor)
rib_out = sb - rib_dir*(1.0+RIB_T)

# ============================== 7. SVG (profile + depth/iso) ===================
S=0.5; MX=MY=80
# --- bounds over the PROFILE (z-x) geometry, now including the dropped anchor/tails.
allp=np.vstack([Ro,Ri,neck,sb,anchor]); x0,x1=allp[:,0].min(),allp[:,0].max(); z0,z1=allp[:,1].min(),allp[:,1].max()
PW=int((x1-x0)*S)+2*MX; PH=int((z1-z0)*S)+2*MY
X=lambda x:(x-x0)*S+MX; Z=lambda z:(z1-z)*S+MY
dof=lambda p:" ".join("%.2f,%.2f"%(X(q[0]),Z(q[1])) for q in p)

out=[]   # PROFILE panel content (translated into the combined SVG below)
out.append('<text x="%.1f" y="28" fill="#cdd2da" font-family="sans-serif" font-size="20">clements47 - PROFILE (z-x): wooden eyelets unchanged; lower CF ladder relocated to the anchor curve</text>'%MX)
# tail strings: from each wooden eyelet to its CF anchor knot (red) -- carries the axial T
for i in range(N_STRINGS):
    out.append(f'<line x1="{X(sb[i,0]):.2f}" y1="{Z(sb[i,1]):.2f}" x2="{X(anchor[i,0]):.2f}" y2="{Z(anchor[i,1]):.2f}" stroke="#ff5a4d" stroke-width="1.1"/>')
# speaking strings: neck -> wooden eyelet (UNCHANGED -> pitch unchanged)
for i in range(N_STRINGS):
    w=max(DIA[i]*S*4,1.0)
    out.append(f'<line x1="{X(neck[i,0]):.2f}" y1="{Z(neck[i,1]):.2f}" x2="{X(sb[i,0]):.2f}" y2="{Z(sb[i,1]):.2f}" stroke="#7d7762" stroke-width="{w:.2f}" stroke-linecap="round"/>')
# CF frame (lower ladder now sits on the relocated anchor curve)
out.append(f'<path d="M {dof(Ro)} Z M {dof(Ri)} Z" fill="url(#st)" fill-rule="evenodd" stroke="#ff9e6b" stroke-width="1.6"/>')
# CF backing rib under the wooden eyelets (spreads per-eyelet loads into the frame)
out.append(f'<path d="M {dof(rib_in)} L {dof(rib_out[::-1])} Z" fill="#3a6a8c" fill-opacity="0.55" stroke="#7fb7da" stroke-width="0.8"/>')
# wooden eyelet curve (the OLD soundboard-tip curve), unchanged, drawn as the wood line
out.append(f'<polyline points="{dof(sb)}" fill="none" stroke="#caa15a" stroke-width="2.2"/>')
rN=NECK_RUNG_OD/2
for i in range(N_STRINGS):
    nk=neck[i]+np.array([(DIA[i]/2+rN)*Cs,(DIA[i]/2+rN)*Sn])      # tangent @9 o'clock
    out.append(f'<circle cx="{X(nk[0]):.2f}" cy="{Z(nk[1]):.2f}" r="{rN*S:.2f}" fill="#6ee0a0"/>')
    # wooden eyelet (string PASSES THROUGH, no knot): brass-colored ring + bore
    out.append(f'<circle cx="{X(sb[i,0]):.2f}" cy="{Z(sb[i,1]):.2f}" r="{SB_RUNG_OD/2*S:.2f}" fill="none" stroke="#e0b86e" stroke-width="1.3"/>')
    out.append(f'<circle cx="{X(sb[i,0]):.2f}" cy="{Z(sb[i,1]):.2f}" r="{max(DIA[i]/2*S,.6):.2f}" fill="#13110d"/>')
    # CF anchor knot (string KNOTS here; CF takes the axial tension)
    out.append(f'<circle cx="{X(anchor[i,0]):.2f}" cy="{Z(anchor[i,1]):.2f}" r="2.0" fill="#ff5a4d"/>')

# ===== DEPTH / ISO panel (string axis vs depth y): eyelet at y=0, tail kicked d into +y,
# tapered wooden chamber bulging into +y (deep+wide bass, shallow treble, soundhole back).
# Use the spacing axis x (station) as horizontal, depth y as vertical (+y = into page, down).
dep=[]
DS=0.6; DMX=80; DMY=80
# along-string profile per string: speaking string is at depth y=0 over its whole length;
# the tail kicks from y=0 (eyelet) to y=D_KICK (anchor). We render depth(y) vs station x.
# chamber depth taper across the band (bass station xc[0] deep -> treble xc[-1] shallow):
def chamber_depth(xstat):
    f=(xstat-xc[0])/(xc[-1]-xc[0])                              # 0 at bass .. 1 at treble
    return CHAMBER_DEPTH_BASS + (CHAMBER_DEPTH_TREB-CHAMBER_DEPTH_BASS)*f
def chamber_halfwidth(xstat):
    f=(xstat-xc[0])/(xc[-1]-xc[0])
    return CHAMBER_WIDTH_BASS + (CHAMBER_WIDTH_TREB-CHAMBER_WIDTH_BASS)*f
xs=xc; depth_prof=np.array([chamber_depth(x) for x in xs])
# span both sides of the y=0 soundboard plane: chamber on +y, CF anchor/tails on -y (opposite)
dx0,dx1=xs.min(),xs.max(); dy0,dy1=min(0.0,float(anchor_y.min()))-12, max(CHAMBER_DEPTH_BASS,float(anchor_y.max()))+10
DW=int((dx1-dx0)*DS)+2*DMX; DH=int((dy1-dy0)*DS)+2*DMY
DX=lambda x:(x-dx0)*DS+DMX; DY=lambda y:(y-dy0)*DS+DMY      # +y depth grows DOWNWARD on page
ddof=lambda px,py:" ".join("%.2f,%.2f"%(DX(a),DY(b)) for a,b in zip(px,py))
dep.append('<text x="%.1f" y="28" fill="#cdd2da" font-family="sans-serif" font-size="20">DEPTH/ISO (station x vs depth y): wooden chamber bulges +y; CF anchor/tails kick -y (opposite side, clear of the chamber), |d|=%.1f mm</text>'%(DMX,abs(D_KICK)))
# wooden chamber body (filled): front edge at y=0 (the eyelet plane), back edge = depth taper
chamber_top=[DX(x) for x in xs]; cf=[DY(0.0) for _ in xs]; cb=[DY(d) for d in depth_prof]
poly=" ".join("%.2f,%.2f"%(DX(x),DY(0.0)) for x in xs)
poly+=" "+" ".join("%.2f,%.2f"%(DX(x),DY(d)) for x,d in list(zip(xs,depth_prof))[::-1])
dep.append(f'<polygon points="{poly}" fill="#6b4a23" fill-opacity="0.85" stroke="#caa15a" stroke-width="1.6"/>')
# soundhole in the BACK (deep) wall, near the bass third
sh_x=xs[0]+(xs[-1]-xs[0])*0.22; sh_y=chamber_depth(sh_x)*0.62
dep.append(f'<ellipse cx="{DX(sh_x):.2f}" cy="{DY(sh_y):.2f}" rx="{18*DS:.2f}" ry="{12*DS:.2f}" fill="#13110d" stroke="#caa15a" stroke-width="1.2"/>')
# eyelet plane line at y=0
dep.append(f'<line x1="{DX(dx0):.2f}" y1="{DY(0):.2f}" x2="{DX(dx1):.2f}" y2="{DY(0):.2f}" stroke="#caa15a" stroke-width="2.2"/>')
# per-string straddle: speaking string above the board (y=0), tail kicked to +D_KICK below
for i in range(N_STRINGS):
    px=DX(xs[i])
    dep.append(f'<circle cx="{px:.2f}" cy="{DY(0.0):.2f}" r="1.8" fill="#e0b86e"/>')                 # eyelet @ y=0
    dep.append(f'<line x1="{px:.2f}" y1="{DY(0.0):.2f}" x2="{px:.2f}" y2="{DY(-abs(anchor_y[i])*0.0):.2f}" stroke="#7d7762" stroke-width="1.0"/>')
    dep.append(f'<line x1="{px:.2f}" y1="{DY(0.0):.2f}" x2="{px:.2f}" y2="{DY(anchor_y[i]):.2f}" stroke="#ff5a4d" stroke-width="1.0"/>')  # tail kicks +y
    dep.append(f'<circle cx="{px:.2f}" cy="{DY(anchor_y[i]):.2f}" r="1.6" fill="#ff5a4d"/>')         # CF anchor knot in +y
# CF anchor curve in the depth view (the kicked plane)
dep.append(f'<polyline points="{ddof(xs, anchor_y)}" fill="none" stroke="#ff9e6b" stroke-width="2.0"/>')

# ===== combine the two panels stacked vertically into one SVG =====
WD=max(PW,DW); HT=PH+DH+20
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{WD}" height="{HT}" viewBox="0 0 {WD} {HT}">']
svg.append('<defs><linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8ccd3"/><stop offset=".5" stop-color="#9094a0"/><stop offset="1" stop-color="#54585f"/></linearGradient></defs>')
svg.append(f'<rect width="{WD}" height="{HT}" fill="#13110d"/>')
svg.append(f'<g transform="translate(0,0)">{"".join(out)}</g>')
svg.append(f'<g transform="translate(0,{PH+20})"><rect width="{DW}" height="{DH}" fill="#0e0c09"/>{"".join(dep)}</g>')
svg.append('</svg>')
open("erand47.svg","w").write("\n".join(svg))

# ============================== BOM / report ===================================
def shoelace(P): x,y=P[:,0],P[:,1]; return .5*abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
band=shoelace(Ro)-shoelace(Ri); plate=band*PLATE_T_MM*RHO_CF/1000
rung=(47*math.pi/4*NECK_RUNG_OD**2+47*math.pi/4*SB_RUNG_OD**2+PILLAR_RUNGS*math.pi/4*SB_RUNG_OD**2)*PLATE_GAP_MM*RHO_CF/1000
print(f"closing load/ladder = {TENSION_LBF.sum()*LB2N*Cs:.0f} N  | lateral shear = {TENSION_LBF.sum()*LB2N*Sn:.0f} N")
print(f"band area = {band:.0f} mm^2/plate (rake area-preserving, det=1)")
print(f"2 plates = {2*plate:.2f} kg | {PILLAR_RUNGS+94} rungs = {rung:.2f} kg")
print(f"bare frame = {2*plate+rung:.2f} kg = {(2*plate+rung)*2.205:.1f} lb")
print(f"rigged (+tuners 1.2 +pickups 0.7 +strings 0.5) = {2*plate+rung+2.4:.1f} kg = {(2*plate+rung+2.4)*2.205:.0f} lb")

# ============================== clements47 LOAD SUMMARY ========================
Fdb = np.array([down_bearing(i) for i in range(N_STRINGS)])
cf_total   = T.sum()                 # full axial tension -> CF frame
wood_total = Fdb.sum()               # break-angle down-bearing -> wood
print()
print("== clements47 load split (break angle b = %.1f deg) =="%BREAK_ANGLE_DEG)
print(f"Total axial tension -> CF frame : {int(cf_total)} N")
print(f"Total down-bearing  -> wood     : {int(round(wood_total))} N  (~{100*wood_total/cf_total:.0f}% of tension)")
# per-octave stations: C1..C7 every 7 strings, then G7 (last).
oct_idx=[0,7,14,21,28,35,42,N_STRINGS-1]; oct_lbl=["C1","C2","C3","C4","C5","C6","C7","G7"]
print("Per-eyelet down-bearing F_db (N):  " +
      "  ".join(f"{l} {Fdb[i]:.1f}" for l,i in zip(oct_lbl,oct_idx)))
# chamber depth profile (DEPTH view), bass..treble at the octave stations:
print("Chamber depth profile (mm) @ "+" ".join(oct_lbl)+":  " +
      " ".join(f"{chamber_depth(xc[i]):.0f}" for i in oct_idx))

# --- verification: pitch unchanged + measured break angle at a mid station ---
speak_len = np.hypot(sb[:,0]-neck[:,0], sb[:,1]-neck[:,1])
orig_len  = np.hypot((rake(np.column_stack([xc,ztip]))-rake(np.column_stack([xc,-ztip])))[:,0],
                     (rake(np.column_stack([xc,ztip]))-rake(np.column_stack([xc,-ztip])))[:,1])
mid=N_STRINGS//2
# break angle = angle between the (incoming) speaking string and the (outgoing) tail at the
# eyelet, measured in the 3-D station/depth/profile space (depth gives the perpendicular kick).
sp3 = np.array([neck[mid,0]-sb[mid,0], 0.0, neck[mid,1]-sb[mid,1]])              # eyelet->neck (3D: x, y=depth, z)
tl3 = np.array([anchor[mid,0]-sb[mid,0], anchor_y[mid]-0.0, anchor[mid,1]-sb[mid,1]])  # eyelet->anchor (3D)
cosang=np.dot(sp3,tl3)/(np.linalg.norm(sp3)*np.linalg.norm(tl3))
break_meas=180.0-math.degrees(math.acos(max(-1,min(1,cosang))))                 # kink angle off straight
print(f"pitch unchanged: speaking length neck->eyelet matches original to {np.abs(speak_len-orig_len).max():.4f} mm")
print(f"measured break angle @ mid station ({oct_lbl[0] if mid==0 else 'idx %d'%mid}) = {break_meas:.2f} deg (target {BREAK_ANGLE_DEG:.1f})")
