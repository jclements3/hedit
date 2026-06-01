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

# ----- string data from the erand47 archive (StringSpec: L = grommet_y - pin_y), data-num 1..47 = C1..G7
# This is the AUTHORITATIVE length scale (confirmed against erand47_profile_v2.svg). Two earlier
# regressions to avoid: (a) np.linspace(1514.93,60.61,N) -- a straight ramp; (b) substituting
# strings.svg lengths (1514.9,1489.7,...) -- those are the *Paraguayan* harp, a different instrument.
# NB: the treble tail is non-monotonic (F7=15.59 then G7=60.61); preserved verbatim from the archive
# (15.59 mm looks unphysical -- flagged as an open data-check item, not silently "fixed").
L = np.array([
 1514.93,1448.69,1384.93,1323.57,1264.50,1207.63,1152.87,1100.13,
 1049.33,1000.39,953.23,907.78,863.97,821.73,781.00,741.71,
 703.81,667.24,631.95,597.88,564.99,533.23,502.55,472.91,
 444.27,416.59,389.82,363.94,338.90,314.68,291.24,268.55,
 246.58,225.31,204.70,184.74,165.39,146.64,128.46,110.83,
 93.74,77.15,61.06,45.45,30.30,15.59,60.61])
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

# ============================== 7. SVG =========================================
S=0.5; MX=MY=80
allp=np.vstack([Ro,Ri,neck,sb]); x0,x1=allp[:,0].min(),allp[:,0].max(); z0,z1=allp[:,1].min(),allp[:,1].max()
WD=int((x1-x0)*S)+2*MX; HT=int((z1-z0)*S)+2*MY
X=lambda x:(x-x0)*S+MX; Z=lambda z:(z1-z)*S+MY
dof=lambda p:" ".join("%.2f,%.2f"%(X(q[0]),Z(q[1])) for q in p)
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{WD}" height="{HT}" viewBox="0 0 {WD} {HT}">']
out.append('<defs><linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8ccd3"/><stop offset=".5" stop-color="#9094a0"/><stop offset="1" stop-color="#54585f"/></linearGradient></defs>')
out.append(f'<rect width="{WD}" height="{HT}" fill="#13110d"/>')
for i in range(N_STRINGS):
    w=max(DIA[i]*S*4,1.0)
    out.append(f'<line x1="{X(neck[i,0]):.2f}" y1="{Z(neck[i,1]):.2f}" x2="{X(sb[i,0]):.2f}" y2="{Z(sb[i,1]):.2f}" stroke="#7d7762" stroke-width="{w:.2f}" stroke-linecap="round"/>')
out.append(f'<path d="M {dof(Ro)} Z M {dof(Ri)} Z" fill="url(#st)" fill-rule="evenodd" stroke="#ff9e6b" stroke-width="1.6"/>')
rN=NECK_RUNG_OD/2
for i in range(N_STRINGS):
    nk=neck[i]+np.array([(DIA[i]/2+rN)*Cs,(DIA[i]/2+rN)*Sn])      # tangent @9 o'clock
    out.append(f'<circle cx="{X(nk[0]):.2f}" cy="{Z(nk[1]):.2f}" r="{rN*S:.2f}" fill="#6ee0a0"/>')
    out.append(f'<circle cx="{X(sb[i,0]):.2f}" cy="{Z(sb[i,1]):.2f}" r="{SB_RUNG_OD/2*S:.2f}" fill="#e0b86e"/>')
    out.append(f'<circle cx="{X(sb[i,0]):.2f}" cy="{Z(sb[i,1]):.2f}" r="{max(DIA[i]/2*S,.6):.2f}" fill="#13110d"/>')
out.append('</svg>')
open("erand47.svg","w").write("\n".join(out))

# ============================== BOM / report ===================================
def shoelace(P): x,y=P[:,0],P[:,1]; return .5*abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
band=shoelace(Ro)-shoelace(Ri); plate=band*PLATE_T_MM*RHO_CF/1000
rung=(47*math.pi/4*NECK_RUNG_OD**2+47*math.pi/4*SB_RUNG_OD**2+PILLAR_RUNGS*math.pi/4*SB_RUNG_OD**2)*PLATE_GAP_MM*RHO_CF/1000
print(f"closing load/ladder = {TENSION_LBF.sum()*LB2N*Cs:.0f} N  | lateral shear = {TENSION_LBF.sum()*LB2N*Sn:.0f} N")
print(f"band area = {band:.0f} mm^2/plate (rake area-preserving, det=1)")
print(f"2 plates = {2*plate:.2f} kg | {PILLAR_RUNGS+94} rungs = {rung:.2f} kg")
print(f"bare frame = {2*plate+rung:.2f} kg = {(2*plate+rung)*2.205:.1f} lb")
print(f"rigged (+tuners 1.2 +pickups 0.7 +strings 0.5) = {2*plate+rung+2.4:.1f} kg = {(2*plate+rung+2.4)*2.205:.0f} lb")
