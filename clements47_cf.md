# erand47 — 47-String Solid-Body Electric Pedal Harp · **carbon-fiber frame**

### Twin curved-ladder string frame · design record (CF revision)

Identical geometry to the stainless record; **material swapped from ¼″ 304 SS plate to a UD-dominant CF/epoxy laminate.** Two laminate plates, 13 mm apart, cut/laid to one continuous loop — **neck** (N) top, **soundboard** (S) bottom, a **pillar** strut at the bass (C1) end and a **rounded shoulder** strut at the treble (G7) end — laced with rungs. 47 strings span the gap, raked 7°, pinned at both ends.

Geometry, string band, rake, and end-cap construction are **unchanged** (see §3 / §8). Only the material, sizing logic, and connections change.

-----

## 1. Design constraints (parameters)

|Parameter          |Value                       |Notes                                     |
|-------------------|----------------------------|------------------------------------------|
|Strings            |47                          |C1 (bass) → G7 (treble)                   |
|String air gap     |13 mm                       |unchanged                                 |
|String rake        |7°                          |unchanged                                 |
|**Plate laminate** |**UD-dominant CF/epoxy, ~58% Vf**|replaces ¼″ 304 SS                   |
|Plate E (0°)       |**135 GPa**                 |laminate effective, rail/warp aligned     |
|Plate tensile UTS  |**~1800 MPa** (0°)          |first-ply-failure ~900 MPa                |
|Interlaminar (ILSS)|**~70 MPa**                 |governs rungs + junctions                 |
|Density            |**1.55 g/cm³**              |vs 8.0 for SS                             |
|Plate thickness    |**6.35 mm**                 |unchanged; CF stiffness recovered via taller bars, not thicker plate|
|Plate-to-plate gap |13 mm                       |depth axis *y*                            |
|Bar-sizing target  |gap closure ≤ 1 mm          |deflection-governed; bar heights ×1.127 vs SS (§4)|
|Inner end-cap bow  |39 mm                       |unchanged                                 |
|Pillar radial depth|24 mm                       |unchanged; lacing still essential         |
|Shoulder bow       |20 mm                       |unchanged                                 |
|**Neck rung**      |**CF rod ≥3 mm + brass/bronze wear shoe**|string rides on the shoe, not bare CF|
|**Soundboard rung**|**CF rod, drilled, brass eyelet**|string through + knot; brass at the hole|

**Why CF, vs the rejected metals:** zinc/cast alloys creep under permanent string tension and were dropped; at this section every castable metal also failed bending (FoS ≤ 1.1). CF is the only candidate that passes the slender section, does **not creep**, and runs ~5× lighter.

-----

## 2. String specifications (erand47 archive)

L = grommet_y − pin_y · tension schedule linear C1→G7 · ΣT = **1496 lbf = 6655 N** per ladder.

|# |Note|L (mm)|T (lbf)|T (N)|Ø (mm)|c-c (mm)|
|--|----|------|-------|-----|------|--------|
|1 |C1  |1514.9|52.69  |234.4|1.676 |14.6    |
|2 |D1  |1489.7|51.79  |230.4|1.549 |14.6    |
|3 |E1  |1464.4|50.88  |226.3|1.448 |14.5    |
|4 |F1  |1439.2|49.97  |222.3|1.270 |14.4    |
|5 |G1  |1408.9|49.07  |218.3|1.219 |14.2    |
|6 |A1  |1378.6|48.16  |214.2|1.219 |14.2    |
|7 |B1  |1348.3|47.25  |210.2|1.016 |14.1    |
|8 |C2  |1318.0|46.34  |206.2|1.016 |14.0    |
|9 |D2  |1282.6|45.44  |202.1|0.914 |14.0    |
|10|E2  |1242.2|44.53  |198.1|2.642 |14.8    |
|11|F2  |1222.0|43.62  |194.0|2.489 |15.6    |
|12|G2  |1186.7|42.72  |190.0|2.337 |15.4    |
|13|A2  |1110.9|41.81  |186.0|2.184 |15.3    |
|14|B2  |1055.4|40.90  |181.9|2.057 |15.1    |
|15|C3  |989.8 |40.00  |177.9|2.057 |15.1    |
|16|D3  |924.1 |39.09  |173.9|1.930 |15.0    |
|17|E3  |863.5 |38.18  |169.8|1.676 |14.8    |
|18|F3  |792.8 |37.28  |165.8|1.676 |14.7    |
|19|G3  |732.2 |36.37  |161.8|1.549 |14.6    |
|20|A3  |666.6 |35.46  |157.7|1.549 |14.5    |
|21|B3  |621.1 |34.56  |153.7|1.270 |14.4    |
|22|C4  |570.6 |33.65  |149.7|1.270 |14.3    |
|23|D4  |525.2 |32.74  |145.6|1.270 |14.3    |
|24|E4  |484.8 |31.83  |141.6|1.143 |14.2    |
|25|F4  |449.4 |30.93  |137.6|1.143 |14.1    |
|26|G4  |414.1 |30.02  |133.5|1.143 |14.1    |
|27|A4  |383.8 |29.11  |129.5|1.016 |14.1    |
|28|B4  |353.5 |28.21  |125.5|1.016 |14.0    |
|29|C5  |328.2 |27.30  |121.4|1.016 |14.0    |
|30|D5  |303.0 |26.39  |117.4|0.914 |14.0    |
|31|E5  |277.7 |25.49  |113.4|0.914 |13.9    |
|32|F5  |262.6 |24.58  |109.3|0.914 |13.9    |
|33|G5  |237.3 |23.67  |105.3|0.813 |13.9    |
|34|A5  |222.2 |22.77  |101.3|0.813 |13.8    |
|35|B5  |207.0 |21.86  |97.2 |0.813 |13.8    |
|36|C6  |191.9 |20.95  |93.2 |0.813 |13.8    |
|37|D6  |176.7 |20.04  |89.2 |0.762 |13.8    |
|38|E6  |161.6 |19.14  |85.1 |0.762 |13.8    |
|39|F6  |146.4 |18.23  |81.1 |0.762 |13.8    |
|40|G6  |131.3 |17.32  |77.1 |0.711 |13.7    |
|41|A6  |121.2 |16.42  |73.0 |0.711 |13.7    |
|42|B6  |111.1 |15.51  |69.0 |0.660 |13.7    |
|43|C7  |101.0 |14.60  |65.0 |0.635 |13.6    |
|44|D7  |90.9  |13.70  |60.9 |0.635 |13.6    |
|45|E7  |80.8  |12.79  |56.9 |0.635 |13.6    |
|46|F7  |70.7  |11.88  |52.9 |0.635 |13.6    |
|47|G7  |60.6  |10.98  |48.8 |0.635 |13.6    |

-----

## 3. Geometry pipeline — curves unchanged, heights re-solved for CF

String band → tip quintics (N,S) → **CF-re-solved** deflection-governed bar heights (×1.127 vs SS, §4) → bar-edge quintics (NT,NB,ST,SB) → tangent-matched Bézier end caps (pillar + rounded shoulder) → rungs → 7° area-preserving rake. The CF revision changes only the material constants in the sizing solve (§7), not the curve construction.

-----

## 4. Structural analysis (CF) — reduced

Loads are material-independent; only stiffness changes with the swap to CF. The frame is **deflection-governed** (stress is trivial), so the entire CF re-size follows from one ratio — no separate FE solve is required here.

**The one move:** elastic closure ∝ 1/E, so at fixed geometry CF closes 193/135 = **1.43× more** than 304 SS. Restore the stainless gap-closure budget by scaling bar height **×1.127** (= 1.43^⅓, since I ∝ H³). So CF bars **grow ~13%, they do not shrink** — ends 16.7 → **18.8 mm**, peak 81.1 → **91.4 mm** (applied in the §7 generator). CF's payoff is mass and no-creep, not a smaller frame.

|Quantity                |Value                              |Note                                   |
|------------------------|-----------------------------------|---------------------------------------|
|Closing load / ladder   |6655 N (6606 N after 7° rake)      |from ΣT; material-independent          |
|Lateral shear (rake)    |811 N toward pillar                |geometry only                          |
|Bar max stress σ        |~40 MPa                            |FoS ~22 vs first-ply 900, ~45 vs UTS 1800 — negligible|
|**Bar-height scale**    |**×1.127** (193/135 = 1.43, ∛)     |deflection parity with the SS design   |
|**Bar heights ends→peak**|**18.8 → 91.4 mm**                |= SS 16.7 → 81.1 ×1.127                 |
|Pillar (24 mm + 6 rungs)|**lacing/stability-governed**      |stress trivial; lower E ⇒ rungs even more essential|
|Rungs / rung↔rail nodes |**ILSS-governed, target FoS ≥ 3** vs 70 MPa|woven/wrapped node; rail axial strength never appears at a transverse rung|

**Conclusions:** deflection sets the bar (stress carries ~20–45× margin); the pillar fails by **stability**, not strength, so the 6 cross-rungs are non-negotiable; rung↔rail junctions are interlaminar-shear limited (size to ILSS, not the 1800 MPa axial number); and unlike the rejected cast metals, CF **does not creep** under permanent tension.

**Caveat (why this is *reduced*, not a full solve):** the ×1.127 re-size is purely the E-ratio and is solver-independent. The *absolute* gap closure depends on pillar/shoulder lacing stiffness; the original frame-FE solver is not in this repo (§7 hardcodes the SS height profile, scaled ×1.127 for CF). Confirm a standalone closure value against a lacing-resolved model before fabrication.

## 5. String connections (CF)

- **Neck:** string rides over the neck rung, but on a **partial brass/bronze wear shoe** (C-saddle
on the contact arc), not bare CF — a tensioned string saws resin/fibers. Shoe oriented so the string seating force seats it; epoxy-bonded (the bondline also isolates the cathodic CF from the brass). Rung tow ideally **wraps/interleaves** the rail bundle at this node.
- **Soundboard:** string passes through the rung, seated in a **brass eyelet/grommet** drilled to
the string Ø, with a knot (2× Ø) below. Brass takes the bearing; CF is not loaded transversely across a cut hole.
- 13 mm string air gap maintained.

### 5b. Lower-ladder split: wooden eyelet (pitch) vs CF anchor (load)

The lower termination is split so the **CF frame carries the full axial string tension** and the
**wood carries only a small, tunable, perpendicular down-bearing** (so a wooden sound chamber can
be fitted without taking string load):

- **Wooden eyelet curve** = the old soundboard-tip (`sb`) curve, **unchanged** — it still sets the
  speaking length, so **pitch and the whole tension schedule are unchanged** (verified: speaking
  length matches the original to 0.0000 mm). Strings **pass through** these wooden eyelets (no knot).
- **CF anchor curve** (`place_cf_anchors`): from each eyelet, a dead-tail `L_TAIL = 30 mm` runs along
  the straight string continuation, then kicks `d = L_TAIL·sin(β) ≈ 6.24 mm` along the soundboard
  outward normal (the chamber/depth +y). The string **knots on the CF here**; the lower CF ladder
  relocates to this curve (drops ~`L_TAIL·cos β` = 29.3 mm back), opening room for the wood.
- The **break-angle kink** `β = BREAK_ANGLE_DEG = 12°` at the eyelet is what drives the wood; the CF
  anchor takes the axial pull. Helpers `break_angle(i)/down_bearing(i)/anchor_offset(i)` are left
  per-string so β can be **tapered smaller at the bass** to protect the bass wood.
- A **CF backing rib** along the eyelet line spreads the per-eyelet point loads into the frame.
- **Wooden chamber**: bulges into depth off the eyelet curve, tapered (deep+wide bass → shallow
  treble: ~95 → 18 mm), soundhole in the back. Carries **no** axial tension.

**Load split (β = 12°):** axial tension → CF frame **6655 N**; down-bearing → wood **≈ 1391 N (~21%)**.
Per-eyelet F_db = 2·T·sin(β/2) (N): C1 49.0 · C2 43.1 · C3 37.2 · C4 31.3 · C5 25.4 · C6 19.5 · C7 13.6 · G7 10.2.
Tuning knob (total wood load): 10°→1160 N · 12°→1390 N · 15°→1740 N · 20°→2310 N (~115 N per +1°).
Generator: `erand47_design.py` (PROFILE + DEPTH/ISO panels → `clements47_cf_anchor.svg`).

-----

## 6. Bill of materials (CF)

|Item                                   |Qty|Mass                  |
|---------------------------------------|---|----------------------|
|Closed-frame plate, CF/epoxy 6.35 mm (CF-sized bars)|2 |**≈ 2.50 kg**|
|Rungs — CF rod (neck/soundboard/pillar)|100|≈ 0.1 kg              |
|Brass/bronze wear shoes + eyelets      |~94|≈ 0.05 kg             |
|**Bare frame**                         |   |**≈ 2.56 kg (5.7 lb)**|
|+ tuners (1.2) + pickups (0.7) + strings (0.5)| | |
|**Rigged**                             |   |**≈ 5.0 kg (11 lb)**  |

vs the stainless record: bare frame **11.7 kg → ~2.4 kg (~5× lighter)**; rigged 14.5 kg → ~4.8 kg. (Stiffness-parity 9.1 mm plates → bare ~3.4 kg, still ~3.5× lighter.) The earlier "~6 kg CF" estimate assumed much thicker plates; at deflection-governed thickness it lands far lighter.

-----

## 7. Parametric generator (CF) — full, runnable

Complete generator with CF material constants baked in. Curve construction is identical to the stainless record; only material/sizing/mass differ. Run: `python3 erand47_design.py` → writes `erand47.svg` and prints the BOM.

```python
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
```

-----

## 8. Final geometry (SVG)

Profile, 7° rake, string lines, and the connection loupe — geometry only, identical to the stainless record (material does not change the curves). Regenerate from §7 with the CF constants; colors may be retinted to read as carbon.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="558" height="922" viewBox="0 0 558 922">
<defs><linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8ccd3"/><stop offset=".5" stop-color="#9094a0"/><stop offset="1" stop-color="#54585f"/></linearGradient></defs>
<rect width="558" height="922" fill="#13110d"/>
<line x1="92.49" y1="85.51" x2="184.80" y2="837.33" stroke="#7d7762" stroke-width="3.35" stroke-linecap="round"/>
<line x1="100.82" y1="93.36" x2="191.20" y2="829.49" stroke="#7d7762" stroke-width="3.10" stroke-linecap="round"/>
<line x1="109.08" y1="101.20" x2="197.54" y2="821.64" stroke="#7d7762" stroke-width="2.90" stroke-linecap="round"/>
<line x1="117.28" y1="109.05" x2="203.81" y2="813.80" stroke="#7d7762" stroke-width="2.54" stroke-linecap="round"/>
<line x1="125.42" y1="116.89" x2="210.02" y2="805.95" stroke="#7d7762" stroke-width="2.44" stroke-linecap="round"/>
<line x1="133.54" y1="124.74" x2="216.22" y2="798.11" stroke="#7d7762" stroke-width="2.44" stroke-linecap="round"/>
<line x1="141.62" y1="132.58" x2="222.37" y2="790.26" stroke="#7d7762" stroke-width="2.03" stroke-linecap="round"/>
<line x1="149.64" y1="140.43" x2="228.47" y2="782.42" stroke="#7d7762" stroke-width="2.03" stroke-linecap="round"/>
<line x1="157.64" y1="148.27" x2="234.54" y2="774.57" stroke="#7d7762" stroke-width="1.83" stroke-linecap="round"/>
<line x1="166.05" y1="156.12" x2="241.02" y2="766.73" stroke="#7d7762" stroke-width="5.28" stroke-linecap="round"/>
<line x1="174.85" y1="163.96" x2="247.90" y2="758.88" stroke="#7d7762" stroke-width="4.98" stroke-linecap="round"/>
<line x1="183.58" y1="171.81" x2="254.70" y2="751.04" stroke="#7d7762" stroke-width="4.67" stroke-linecap="round"/>
<line x1="192.23" y1="179.65" x2="261.43" y2="743.19" stroke="#7d7762" stroke-width="4.37" stroke-linecap="round"/>
<line x1="200.81" y1="187.50" x2="268.08" y2="735.35" stroke="#7d7762" stroke-width="4.11" stroke-linecap="round"/>
<line x1="209.36" y1="195.34" x2="274.70" y2="727.50" stroke="#7d7762" stroke-width="4.11" stroke-linecap="round"/>
<line x1="217.88" y1="203.19" x2="281.29" y2="719.66" stroke="#7d7762" stroke-width="3.86" stroke-linecap="round"/>
<line x1="226.30" y1="211.03" x2="287.79" y2="711.81" stroke="#7d7762" stroke-width="3.35" stroke-linecap="round"/>
<line x1="234.65" y1="218.88" x2="294.22" y2="703.97" stroke="#7d7762" stroke-width="3.35" stroke-linecap="round"/>
<line x1="242.98" y1="226.72" x2="300.61" y2="696.12" stroke="#7d7762" stroke-width="3.10" stroke-linecap="round"/>
<line x1="251.27" y1="234.57" x2="306.98" y2="688.28" stroke="#7d7762" stroke-width="3.10" stroke-linecap="round"/>
<line x1="259.49" y1="242.41" x2="313.27" y2="680.43" stroke="#7d7762" stroke-width="2.54" stroke-linecap="round"/>
<line x1="267.64" y1="250.26" x2="319.50" y2="672.59" stroke="#7d7762" stroke-width="2.54" stroke-linecap="round"/>
<line x1="275.80" y1="258.10" x2="325.73" y2="664.74" stroke="#7d7762" stroke-width="2.54" stroke-linecap="round"/>
<line x1="283.92" y1="265.95" x2="331.92" y2="656.90" stroke="#7d7762" stroke-width="2.29" stroke-linecap="round"/>
<line x1="292.00" y1="273.79" x2="338.08" y2="649.05" stroke="#7d7762" stroke-width="2.29" stroke-linecap="round"/>
<line x1="300.09" y1="281.64" x2="344.24" y2="641.21" stroke="#7d7762" stroke-width="2.29" stroke-linecap="round"/>
<line x1="308.15" y1="289.48" x2="350.37" y2="633.36" stroke="#7d7762" stroke-width="2.03" stroke-linecap="round"/>
<line x1="316.17" y1="297.33" x2="356.47" y2="625.52" stroke="#7d7762" stroke-width="2.03" stroke-linecap="round"/>
<line x1="324.20" y1="305.17" x2="362.57" y2="617.67" stroke="#7d7762" stroke-width="2.03" stroke-linecap="round"/>
<line x1="332.19" y1="313.02" x2="368.64" y2="609.83" stroke="#7d7762" stroke-width="1.83" stroke-linecap="round"/>
<line x1="340.17" y1="320.86" x2="374.68" y2="601.98" stroke="#7d7762" stroke-width="1.83" stroke-linecap="round"/>
<line x1="348.14" y1="328.71" x2="380.73" y2="594.14" stroke="#7d7762" stroke-width="1.83" stroke-linecap="round"/>
<line x1="356.09" y1="336.55" x2="386.75" y2="586.29" stroke="#7d7762" stroke-width="1.63" stroke-linecap="round"/>
<line x1="364.01" y1="344.40" x2="392.75" y2="578.45" stroke="#7d7762" stroke-width="1.63" stroke-linecap="round"/>
<line x1="371.93" y1="352.24" x2="398.74" y2="570.60" stroke="#7d7762" stroke-width="1.63" stroke-linecap="round"/>
<line x1="379.85" y1="360.09" x2="404.74" y2="562.76" stroke="#7d7762" stroke-width="1.63" stroke-linecap="round"/>
<line x1="387.76" y1="367.93" x2="410.72" y2="554.91" stroke="#7d7762" stroke-width="1.52" stroke-linecap="round"/>
<line x1="395.66" y1="375.78" x2="416.69" y2="547.07" stroke="#7d7762" stroke-width="1.52" stroke-linecap="round"/>
<line x1="403.55" y1="383.62" x2="422.66" y2="539.22" stroke="#7d7762" stroke-width="1.52" stroke-linecap="round"/>
<line x1="411.43" y1="391.47" x2="428.61" y2="531.38" stroke="#7d7762" stroke-width="1.42" stroke-linecap="round"/>
<line x1="419.30" y1="399.31" x2="434.56" y2="523.53" stroke="#7d7762" stroke-width="1.42" stroke-linecap="round"/>
<line x1="427.16" y1="407.16" x2="440.49" y2="515.69" stroke="#7d7762" stroke-width="1.32" stroke-linecap="round"/>
<line x1="435.00" y1="415.00" x2="446.40" y2="507.84" stroke="#7d7762" stroke-width="1.27" stroke-linecap="round"/>
<line x1="442.83" y1="422.85" x2="452.30" y2="500.00" stroke="#7d7762" stroke-width="1.27" stroke-linecap="round"/>
<line x1="450.66" y1="430.69" x2="458.21" y2="492.15" stroke="#7d7762" stroke-width="1.27" stroke-linecap="round"/>
<line x1="458.50" y1="438.54" x2="464.12" y2="484.31" stroke="#7d7762" stroke-width="1.27" stroke-linecap="round"/>
<line x1="466.33" y1="446.38" x2="470.02" y2="476.46" stroke="#7d7762" stroke-width="1.27" stroke-linecap="round"/>
<path d="M 91.92,80.85 93.12,81.66 94.32,82.48 95.53,83.30 96.73,84.13 97.93,84.96 99.14,85.80 100.34,86.64 101.55,87.49 102.76,88.34 103.96,89.19 105.17,90.06 106.38,90.92 107.59,91.79 108.80,92.67 110.01,93.55 111.22,94.43 112.43,95.32 113.64,96.22 114.86,97.12 116.07,98.02 117.28,98.92 118.50,99.83 119.71,100.75 120.93,101.67 122.14,102.59 123.36,103.52 124.57,104.45 125.79,105.38 127.01,106.32 128.23,107.26 129.44,108.21 130.66,109.16 131.88,110.11 133.10,111.07 134.32,112.03 135.54,113.00 136.76,113.96 137.98,114.94 139.21,115.91 140.43,116.89 141.65,117.87 142.87,118.86 144.10,119.84 145.32,120.84 146.55,121.83 147.77,122.83 149.00,123.83 150.22,124.83 151.45,125.84 152.67,126.85 153.90,127.87 155.13,128.88 156.35,129.90 157.58,130.92 158.81,131.95 160.04,132.98 161.27,134.01 162.49,135.04 163.72,136.08 164.95,137.12 166.18,138.16 167.41,139.20 168.65,140.25 169.88,141.30 171.11,142.35 172.34,143.41 173.57,144.47 174.80,145.53 176.04,146.59 177.27,147.65 178.50,148.72 179.74,149.79 180.97,150.86 182.20,151.94 183.44,153.02 184.67,154.09 185.91,155.18 187.14,156.26 188.38,157.35 189.61,158.43 190.85,159.53 192.09,160.62 193.32,161.71 194.56,162.81 195.80,163.91 197.03,165.01 198.27,166.11 199.51,167.22 200.75,168.33 201.99,169.44 203.22,170.55 204.46,171.66 205.70,172.78 206.94,173.89 208.18,175.01 209.42,176.13 210.66,177.26 211.90,178.38 213.14,179.51 214.38,180.64 215.62,181.77 216.86,182.90 218.11,184.04 219.35,185.17 220.59,186.31 221.83,187.45 223.07,188.59 224.32,189.74 225.56,190.88 226.80,192.03 228.04,193.18 229.29,194.33 230.53,195.48 231.77,196.63 233.02,197.79 234.26,198.95 235.51,200.10 236.75,201.27 238.00,202.43 239.24,203.59 240.49,204.76 241.73,205.92 242.98,207.09 244.22,208.26 245.47,209.44 246.72,210.61 247.96,211.79 249.21,212.96 250.46,214.14 251.70,215.32 252.95,216.50 254.20,217.69 255.45,218.87 256.69,220.06 257.94,221.25 259.19,222.44 260.44,223.63 261.69,224.82 262.93,226.01 264.18,227.21 265.43,228.41 266.68,229.61 267.93,230.81 269.18,232.01 270.43,233.21 271.68,234.42 272.93,235.63 274.18,236.83 275.43,238.04 276.68,239.26 277.93,240.47 279.19,241.68 280.44,242.90 281.69,244.12 282.94,245.34 284.19,246.56 285.45,247.78 286.70,249.01 287.95,250.23 289.20,251.46 290.46,252.69 291.71,253.92 292.96,255.15 294.22,256.39 295.47,257.62 296.72,258.86 297.98,260.10 299.23,261.34 300.49,262.58 301.74,263.82 303.00,265.07 304.25,266.31 305.51,267.56 306.76,268.81 308.02,270.07 309.28,271.32 310.53,272.57 311.79,273.83 313.04,275.09 314.30,276.35 315.56,277.61 316.82,278.87 318.07,280.14 319.33,281.41 320.59,282.68 321.85,283.95 323.10,285.22 324.36,286.49 325.62,287.77 326.88,289.05 328.14,290.33 329.40,291.61 330.66,292.89 331.92,294.18 333.18,295.46 334.44,296.75 335.70,298.04 336.96,299.33 338.22,300.63 339.48,301.92 340.74,303.22 342.01,304.52 343.27,305.82 344.53,307.13 345.79,308.43 347.06,309.74 348.32,311.05 349.58,312.36 350.84,313.67 352.11,314.99 353.37,316.30 354.64,317.62 355.90,318.95 357.17,320.27 358.43,321.59 359.69,322.92 360.96,324.25 362.23,325.58 363.49,326.92 364.76,328.25 366.02,329.59 367.29,330.93 368.56,332.27 369.83,333.62 371.09,334.96 372.36,336.31 373.63,337.66 374.90,339.02 376.17,340.37 377.43,341.73 378.70,343.09 379.97,344.45 381.24,345.82 382.51,347.19 383.78,348.55 385.05,349.93 386.32,351.30 387.59,352.68 388.87,354.06 390.14,355.44 391.41,356.82 392.68,358.21 393.95,359.59 395.23,360.99 396.50,362.38 397.77,363.77 399.05,365.17 400.32,366.57 401.60,367.98 402.87,369.38 404.15,370.79 405.42,372.20 406.70,373.62 407.97,375.03 409.25,376.45 410.53,377.87 411.80,379.30 413.08,380.72 414.36,382.15 415.64,383.59 416.91,385.02 418.19,386.46 419.47,387.90 420.75,389.34 422.03,390.79 423.31,392.24 424.59,393.69 425.87,395.14 427.15,396.60 428.43,398.06 429.72,399.52 431.00,400.99 432.28,402.46 433.56,403.93 434.85,405.40 436.13,406.88 437.41,408.36 438.70,409.85 439.98,411.33 441.27,412.82 442.55,414.31 443.84,415.81 445.12,417.31 446.41,418.81 447.70,420.32 448.99,421.82 450.27,423.33 451.56,424.85 452.85,426.37 454.14,427.89 455.43,429.41 456.72,430.94 458.01,432.47 459.30,434.00 460.59,435.54 461.88,437.08 463.17,438.62 464.46,440.17 465.76,441.72 465.76,441.72 466.28,442.35 466.80,442.97 467.30,443.57 467.79,444.16 468.27,444.75 468.74,445.32 469.19,445.87 469.64,446.42 470.07,446.96 470.49,447.48 470.90,448.00 471.30,448.51 471.69,449.00 472.07,449.49 472.43,449.97 472.79,450.44 473.13,450.90 473.46,451.35 473.78,451.80 474.09,452.23 474.39,452.66 474.67,453.09 474.95,453.50 475.21,453.91 475.47,454.32 475.71,454.72 475.94,455.11 476.16,455.50 476.37,455.88 476.57,456.26 476.76,456.64 476.94,457.01 477.11,457.37 477.26,457.74 477.41,458.10 477.55,458.45 477.67,458.81 477.79,459.16 477.89,459.51 477.98,459.86 478.07,460.21 478.14,460.56 478.20,460.90 478.26,461.25 478.30,461.59 478.33,461.94 478.35,462.29 478.37,462.63 478.37,462.98 478.36,463.33 478.34,463.68 478.31,464.03 478.28,464.39 478.23,464.75 478.17,465.11 478.10,465.47 478.02,465.84 477.94,466.21 477.84,466.58 477.73,466.96 477.62,467.34 477.49,467.73 477.36,468.13 477.21,468.52 477.06,468.93 476.89,469.34 476.72,469.76 476.54,470.18 476.34,470.61 476.14,471.05 475.93,471.49 475.71,471.95 475.48,472.41 475.25,472.88 475.00,473.35 474.74,473.84 474.48,474.34 474.20,474.84 473.92,475.36 473.62,475.89 473.32,476.42 473.01,476.97 472.69,477.53 472.37,478.10 472.03,478.68 471.68,479.27 471.33,479.88 470.97,480.50 470.59,481.13 470.59,481.13 469.68,482.68 468.77,484.22 467.86,485.77 466.94,487.31 466.03,488.84 465.12,490.38 464.20,491.91 463.29,493.43 462.37,494.96 461.46,496.48 460.54,497.99 459.63,499.51 458.71,501.02 457.79,502.53 456.88,504.03 455.96,505.53 455.04,507.03 454.12,508.53 453.20,510.02 452.28,511.51 451.36,513.00 450.44,514.48 449.52,515.96 448.60,517.44 447.68,518.91 446.76,520.39 445.84,521.85 444.92,523.32 443.99,524.78 443.07,526.24 442.15,527.70 441.22,529.16 440.30,530.61 439.38,532.06 438.45,533.50 437.53,534.94 436.60,536.39 435.68,537.82 434.75,539.26 433.82,540.69 432.90,542.12 431.97,543.55 431.04,544.97 430.12,546.39 429.19,547.81 428.26,549.23 427.33,550.64 426.40,552.05 425.47,553.46 424.54,554.87 423.61,556.27 422.68,557.67 421.75,559.07 420.82,560.46 419.89,561.86 418.96,563.25 418.03,564.64 417.10,566.02 416.16,567.41 415.23,568.79 414.30,570.17 413.37,571.54 412.43,572.92 411.50,574.29 410.56,575.66 409.63,577.02 408.70,578.39 407.76,579.75 406.83,581.11 405.89,582.47 404.96,583.83 404.02,585.18 403.08,586.53 402.15,587.88 401.21,589.23 400.27,590.57 399.34,591.91 398.40,593.25 397.46,594.59 396.52,595.93 395.58,597.26 394.65,598.59 393.71,599.92 392.77,601.25 391.83,602.57 390.89,603.90 389.95,605.22 389.01,606.54 388.07,607.86 387.13,609.17 386.19,610.48 385.25,611.80 384.30,613.10 383.36,614.41 382.42,615.72 381.48,617.02 380.54,618.32 379.59,619.62 378.65,620.92 377.71,622.22 376.76,623.51 375.82,624.80 374.88,626.09 373.93,627.38 372.99,628.67 372.05,629.95 371.10,631.24 370.16,632.52 369.21,633.80 368.27,635.07 367.32,636.35 366.37,637.62 365.43,638.90 364.48,640.17 363.54,641.44 362.59,642.70 361.64,643.97 360.70,645.23 359.75,646.49 358.80,647.75 357.85,649.01 356.91,650.27 355.96,651.52 355.01,652.78 354.06,654.03 353.11,655.28 352.16,656.53 351.22,657.78 350.27,659.02 349.32,660.26 348.37,661.51 347.42,662.75 346.47,663.98 345.52,665.22 344.57,666.46 343.62,667.69 342.67,668.92 341.71,670.15 340.76,671.38 339.81,672.61 338.86,673.84 337.91,675.06 336.96,676.28 336.00,677.50 335.05,678.72 334.10,679.94 333.15,681.16 332.19,682.37 331.24,683.59 330.29,684.80 329.33,686.01 328.38,687.22 327.43,688.42 326.47,689.63 325.52,690.83 324.56,692.04 323.61,693.24 322.65,694.44 321.70,695.63 320.74,696.83 319.79,698.02 318.83,699.22 317.88,700.41 316.92,701.60 315.96,702.79 315.01,703.97 314.05,705.16 313.09,706.34 312.14,707.52 311.18,708.70 310.22,709.88 309.27,711.06 308.31,712.23 307.35,713.41 306.39,714.58 305.43,715.75 304.47,716.92 303.52,718.09 302.56,719.25 301.60,720.42 300.64,721.58 299.68,722.74 298.72,723.90 297.76,725.05 296.80,726.21 295.84,727.36 294.88,728.52 293.92,729.67 292.96,730.81 291.99,731.96 291.03,733.11 290.07,734.25 289.11,735.39 288.15,736.53 287.18,737.67 286.22,738.81 285.26,739.94 284.30,741.07 283.33,742.20 282.37,743.33 281.41,744.46 280.44,745.59 279.48,746.71 278.51,747.83 277.55,748.95 276.58,750.07 275.62,751.18 274.65,752.30 273.69,753.41 272.72,754.52 271.76,755.62 270.79,756.73 269.82,757.83 268.86,758.93 267.89,760.03 266.92,761.13 265.95,762.23 264.99,763.32 264.02,764.41 263.05,765.50 262.08,766.58 261.11,767.67 260.14,768.75 259.17,769.83 258.20,770.90 257.23,771.98 256.26,773.05 255.29,774.12 254.32,775.19 253.35,776.25 252.38,777.32 251.41,778.38 250.43,779.43 249.46,780.49 248.49,781.54 247.51,782.59 246.54,783.64 245.57,784.68 244.59,785.73 243.62,786.76 242.64,787.80 241.67,788.83 240.69,789.87 239.72,790.89 238.74,791.92 237.76,792.94 236.79,793.96 235.81,794.98 234.83,795.99 233.85,797.00 232.88,798.01 231.90,799.01 230.92,800.01 229.94,801.01 228.96,802.01 227.98,803.00 227.00,803.99 226.02,804.97 225.03,805.95 224.05,806.93 223.07,807.91 222.09,808.88 221.10,809.85 220.12,810.81 219.14,811.77 218.15,812.73 217.17,813.68 216.18,814.63 215.20,815.58 214.21,816.52 213.22,817.46 212.24,818.40 211.25,819.33 210.26,820.25 209.27,821.18 208.28,822.09 207.29,823.01 206.30,823.92 205.31,824.83 204.32,825.73 203.33,826.63 202.33,827.52 201.34,828.41 200.35,829.29 199.35,830.17 198.36,831.05 197.36,831.92 196.37,832.79 195.37,833.65 194.38,834.51 193.38,835.36 192.38,836.20 191.38,837.05 190.38,837.88 189.38,838.72 188.38,839.54 187.38,840.37 186.38,841.18 185.38,842.00 185.38,842.00 184.05,842.74 182.68,842.84 181.27,842.33 179.81,841.21 178.31,839.51 176.78,837.23 175.20,834.38 173.60,830.99 171.96,827.07 170.28,822.64 168.58,817.70 166.85,812.27 165.10,806.37 163.32,800.01 161.52,793.20 159.70,785.97 157.86,778.32 156.00,770.27 154.13,761.83 152.24,753.03 150.34,743.86 148.44,734.36 146.52,724.52 144.60,714.37 142.67,703.93 140.74,693.20 138.81,682.20 136.88,670.95 134.96,659.45 133.04,647.73 131.12,635.80 129.21,623.67 127.32,611.36 125.43,598.88 123.56,586.25 121.70,573.49 119.86,560.59 118.04,547.59 116.24,534.49 114.46,521.32 112.70,508.08 110.97,494.78 109.27,481.45 107.60,468.10 105.96,454.74 104.35,441.39 102.78,428.06 101.25,414.77 99.75,401.53 98.29,388.35 96.88,375.25 95.51,362.25 94.18,349.36 92.90,336.59 91.67,323.96 90.49,311.48 89.37,299.17 88.30,287.04 87.28,275.11 86.33,263.39 85.43,251.90 84.60,240.64 83.83,229.64 83.12,218.91 82.48,208.47 81.91,198.32 81.41,188.49 80.99,178.98 80.63,169.82 80.36,161.01 80.16,152.57 80.04,144.52 80.00,136.88 80.05,129.64 80.18,122.84 80.39,116.48 80.70,110.58 81.09,105.15 81.58,100.21 82.16,95.77 82.84,91.85 83.62,88.46 84.49,85.62 85.46,83.34 86.54,81.63 87.73,80.51 89.01,80.00 90.41,80.11 91.92,80.85 Z M 93.06,90.18 94.37,91.86 95.68,93.53 96.99,95.18 98.29,96.83 99.59,98.47 100.89,100.09 102.19,101.70 103.49,103.30 104.79,104.90 106.09,106.48 107.38,108.05 108.68,109.61 109.97,111.16 111.26,112.71 112.55,114.24 113.84,115.76 115.13,117.28 116.41,118.78 117.70,120.28 118.99,121.77 120.27,123.25 121.55,124.72 122.83,126.19 124.12,127.64 125.40,129.09 126.67,130.53 127.95,131.97 129.23,133.39 130.51,134.81 131.78,136.23 133.06,137.63 134.33,139.03 135.60,140.42 136.88,141.81 138.15,143.19 139.42,144.56 140.69,145.93 141.96,147.29 143.23,148.65 144.49,150.00 145.76,151.34 147.03,152.68 148.29,154.02 149.56,155.35 150.82,156.67 152.09,157.99 153.35,159.30 154.61,160.61 155.88,161.92 157.14,163.22 158.40,164.52 159.66,165.81 160.92,167.10 162.18,168.38 163.44,169.67 164.70,170.94 165.96,172.22 167.22,173.49 168.47,174.75 169.73,176.02 170.99,177.28 172.24,178.53 173.50,179.79 174.75,181.04 176.01,182.28 177.27,183.53 178.52,184.77 179.77,186.01 181.03,187.25 182.28,188.48 183.53,189.71 184.79,190.94 186.04,192.17 187.29,193.40 188.55,194.62 189.80,195.84 191.05,197.06 192.30,198.28 193.55,199.49 194.80,200.71 196.05,201.92 197.31,203.13 198.56,204.34 199.81,205.54 201.06,206.75 202.31,207.96 203.56,209.16 204.81,210.36 206.06,211.56 207.30,212.76 208.55,213.96 209.80,215.16 211.05,216.35 212.30,217.55 213.55,218.74 214.80,219.94 216.05,221.13 217.30,222.32 218.54,223.51 219.79,224.71 221.04,225.90 222.29,227.09 223.54,228.27 224.78,229.46 226.03,230.65 227.28,231.84 228.53,233.03 229.78,234.21 231.02,235.40 232.27,236.59 233.52,237.77 234.77,238.96 236.01,240.14 237.26,241.33 238.51,242.51 239.76,243.70 241.01,244.88 242.25,246.07 243.50,247.25 244.75,248.44 246.00,249.62 247.24,250.80 248.49,251.99 249.74,253.17 250.99,254.36 252.23,255.54 253.48,256.73 254.73,257.91 255.98,259.10 257.22,260.28 258.47,261.47 259.72,262.65 260.97,263.84 262.21,265.02 263.46,266.21 264.71,267.39 265.96,268.58 267.20,269.76 268.45,270.95 269.70,272.13 270.95,273.32 272.20,274.51 273.44,275.69 274.69,276.88 275.94,278.07 277.19,279.25 278.43,280.44 279.68,281.63 280.93,282.81 282.18,284.00 283.43,285.19 284.67,286.38 285.92,287.57 287.17,288.75 288.42,289.94 289.67,291.13 290.91,292.32 292.16,293.51 293.41,294.69 294.66,295.88 295.91,297.07 297.15,298.26 298.40,299.45 299.65,300.64 300.90,301.82 302.15,303.01 303.39,304.20 304.64,305.39 305.89,306.58 307.14,307.77 308.39,308.95 309.63,310.14 310.88,311.33 312.13,312.52 313.38,313.71 314.63,314.89 315.87,316.08 317.12,317.27 318.37,318.45 319.62,319.64 320.86,320.83 322.11,322.01 323.36,323.20 324.61,324.38 325.85,325.57 327.10,326.75 328.35,327.93 329.60,329.12 330.84,330.30 332.09,331.48 333.34,332.66 334.59,333.84 335.83,335.02 337.08,336.20 338.33,337.38 339.57,338.56 340.82,339.74 342.07,340.92 343.31,342.09 344.56,343.27 345.81,344.44 347.05,345.62 348.30,346.79 349.54,347.96 350.79,349.13 352.04,350.31 353.28,351.47 354.53,352.64 355.77,353.81 357.02,354.98 358.26,356.14 359.51,357.31 360.75,358.47 362.00,359.63 363.24,360.79 364.49,361.95 365.73,363.11 366.98,364.26 368.22,365.42 369.46,366.57 370.71,367.73 371.95,368.88 373.19,370.03 374.44,371.17 375.68,372.32 376.92,373.47 378.16,374.61 379.41,375.75 380.65,376.89 381.89,378.03 383.13,379.17 384.37,380.30 385.62,381.44 386.86,382.57 388.10,383.70 389.34,384.83 390.58,385.95 391.82,387.08 393.06,388.20 394.30,389.32 395.54,390.44 396.78,391.55 398.02,392.67 399.25,393.78 400.49,394.89 401.73,396.00 402.97,397.10 404.21,398.21 405.44,399.31 406.68,400.41 407.92,401.50 409.15,402.60 410.39,403.69 411.63,404.78 412.86,405.87 414.10,406.95 415.33,408.04 416.57,409.12 417.80,410.19 419.03,411.27 420.27,412.34 421.50,413.41 422.74,414.48 423.97,415.54 425.20,416.61 426.43,417.67 427.66,418.72 428.90,419.78 430.13,420.83 431.36,421.88 432.59,422.92 433.82,423.97 435.05,425.01 436.28,426.05 437.51,427.08 438.74,428.11 439.97,429.14 441.19,430.17 442.42,431.19 443.65,432.22 444.88,433.23 446.10,434.25 447.33,435.26 448.55,436.27 449.78,437.28 451.01,438.28 452.23,439.28 453.46,440.28 454.68,441.27 455.90,442.26 457.13,443.25 458.35,444.24 459.57,445.22 460.79,446.20 462.02,447.17 463.24,448.15 464.46,449.12 465.68,450.08 466.90,451.05 466.90,451.05 467.23,451.31 467.55,451.57 467.87,451.83 468.17,452.08 468.48,452.34 468.77,452.59 469.06,452.84 469.34,453.09 469.61,453.34 469.88,453.59 470.13,453.83 470.39,454.07 470.63,454.31 470.87,454.55 471.10,454.79 471.33,455.03 471.55,455.27 471.76,455.50 471.96,455.73 472.16,455.97 472.35,456.20 472.53,456.43 472.71,456.66 472.88,456.89 473.04,457.11 473.20,457.34 473.34,457.56 473.49,457.79 473.62,458.01 473.75,458.24 473.87,458.46 473.99,458.68 474.10,458.90 474.20,459.12 474.29,459.34 474.38,459.56 474.46,459.78 474.53,460.00 474.60,460.22 474.66,460.44 474.72,460.66 474.76,460.88 474.80,461.09 474.84,461.31 474.86,461.53 474.88,461.75 474.90,461.97 474.90,462.19 474.90,462.40 474.90,462.62 474.88,462.84 474.86,463.06 474.83,463.28 474.80,463.50 474.76,463.72 474.71,463.94 474.66,464.16 474.60,464.38 474.53,464.61 474.46,464.83 474.38,465.05 474.29,465.28 474.20,465.50 474.10,465.73 473.99,465.96 473.88,466.19 473.76,466.42 473.63,466.65 473.50,466.88 473.36,467.11 473.21,467.34 473.06,467.58 472.90,467.81 472.73,468.05 472.56,468.29 472.38,468.53 472.19,468.77 472.00,469.01 471.80,469.26 471.59,469.50 471.38,469.75 471.16,470.00 470.94,470.25 470.71,470.50 470.47,470.76 470.22,471.02 469.97,471.27 469.71,471.53 469.45,471.80 469.45,471.80 468.46,472.76 467.48,473.73 466.50,474.70 465.52,475.67 464.53,476.65 463.55,477.63 462.57,478.61 461.59,479.59 460.61,480.58 459.63,481.57 458.65,482.57 457.67,483.56 456.69,484.56 455.71,485.57 454.73,486.57 453.75,487.58 452.78,488.59 451.80,489.61 450.82,490.63 449.84,491.65 448.87,492.67 447.89,493.70 446.92,494.73 445.94,495.76 444.97,496.80 443.99,497.83 443.02,498.87 442.04,499.92 441.07,500.96 440.10,502.01 439.12,503.07 438.15,504.12 437.18,505.18 436.21,506.24 435.23,507.30 434.26,508.36 433.29,509.43 432.32,510.50 431.35,511.57 430.38,512.65 429.41,513.73 428.44,514.81 427.47,515.89 426.50,516.98 425.53,518.06 424.57,519.15 423.60,520.25 422.63,521.34 421.66,522.44 420.70,523.54 419.73,524.64 418.76,525.74 417.80,526.85 416.83,527.95 415.86,529.06 414.90,530.18 413.93,531.29 412.97,532.41 412.00,533.52 411.04,534.65 410.08,535.77 409.11,536.89 408.15,538.02 407.18,539.15 406.22,540.28 405.26,541.41 404.29,542.54 403.33,543.68 402.37,544.81 401.41,545.95 400.44,547.09 399.48,548.23 398.52,549.38 397.56,550.52 396.60,551.67 395.64,552.82 394.68,553.97 393.72,555.12 392.75,556.27 391.79,557.42 390.83,558.58 389.87,559.74 388.91,560.89 387.95,562.05 386.99,563.21 386.04,564.37 385.08,565.54 384.12,566.70 383.16,567.87 382.20,569.03 381.24,570.20 380.28,571.37 379.32,572.54 378.36,573.71 377.41,574.88 376.45,576.05 375.49,577.22 374.53,578.40 373.57,579.57 372.62,580.75 371.66,581.93 370.70,583.10 369.74,584.28 368.79,585.46 367.83,586.64 366.87,587.82 365.91,589.00 364.96,590.18 364.00,591.36 363.04,592.54 362.09,593.73 361.13,594.91 360.17,596.09 359.22,597.28 358.26,598.46 357.30,599.65 356.35,600.83 355.39,602.02 354.43,603.20 353.48,604.39 352.52,605.58 351.56,606.76 350.61,607.95 349.65,609.14 348.70,610.32 347.74,611.51 346.78,612.70 345.83,613.89 344.87,615.08 343.91,616.26 342.96,617.45 342.00,618.64 341.05,619.83 340.09,621.02 339.13,622.21 338.18,623.40 337.22,624.58 336.26,625.77 335.31,626.96 334.35,628.15 333.40,629.34 332.44,630.53 331.48,631.71 330.53,632.90 329.57,634.09 328.62,635.28 327.66,636.47 326.70,637.65 325.75,638.84 324.79,640.03 323.83,641.22 322.88,642.40 321.92,643.59 320.96,644.78 320.01,645.96 319.05,647.15 318.10,648.34 317.14,649.52 316.18,650.71 315.23,651.89 314.27,653.08 313.31,654.27 312.36,655.45 311.40,656.64 310.44,657.82 309.49,659.01 308.53,660.19 307.57,661.38 306.62,662.56 305.66,663.75 304.70,664.93 303.75,666.12 302.79,667.30 301.83,668.49 300.88,669.67 299.92,670.85 298.96,672.04 298.01,673.22 297.05,674.41 296.09,675.59 295.14,676.78 294.18,677.96 293.22,679.15 292.27,680.33 291.31,681.52 290.35,682.70 289.40,683.89 288.44,685.07 287.48,686.26 286.53,687.44 285.57,688.63 284.62,689.82 283.66,691.00 282.70,692.19 281.75,693.38 280.79,694.57 279.83,695.76 278.88,696.95 277.92,698.14 276.97,699.33 276.01,700.52 275.06,701.71 274.10,702.91 273.14,704.10 272.19,705.29 271.23,706.49 270.28,707.69 269.32,708.88 268.37,710.08 267.41,711.28 266.46,712.48 265.50,713.68 264.55,714.89 263.60,716.09 262.64,717.30 261.69,718.51 260.73,719.71 259.78,720.93 258.83,722.14 257.87,723.35 256.92,724.57 255.97,725.78 255.02,727.00 254.06,728.22 253.11,729.45 252.16,730.67 251.21,731.90 250.26,733.13 249.31,734.36 248.36,735.60 247.41,736.83 246.46,738.07 245.51,739.31 244.56,740.56 243.61,741.81 242.66,743.06 241.71,744.31 240.76,745.57 239.82,746.83 238.87,748.09 237.92,749.36 236.98,750.63 236.03,751.90 235.09,753.18 234.14,754.46 233.20,755.74 232.25,757.03 231.31,758.32 230.37,759.62 229.42,760.92 228.48,762.23 227.54,763.54 226.60,764.85 225.66,766.17 224.72,767.50 223.78,768.83 222.84,770.16 221.91,771.50 220.97,772.85 220.03,774.20 219.10,775.55 218.16,776.91 217.23,778.28 216.30,779.66 215.36,781.03 214.43,782.42 213.50,783.81 212.57,785.21 211.64,786.62 210.71,788.03 209.78,789.45 208.86,790.88 207.93,792.31 207.00,793.75 206.08,795.20 205.16,796.66 204.24,798.12 203.31,799.59 202.39,801.07 201.47,802.56 200.56,804.06 199.64,805.57 198.72,807.08 197.81,808.60 196.89,810.14 195.98,811.68 195.07,813.23 194.16,814.79 193.25,816.36 192.34,817.95 191.44,819.54 190.53,821.14 189.63,822.75 188.72,824.38 187.82,826.01 186.92,827.66 186.02,829.32 185.13,830.99 184.23,832.67 184.23,832.67 183.48,833.69 182.67,834.07 181.80,833.83 180.88,832.98 179.90,831.53 178.87,829.51 177.80,826.92 176.67,823.78 175.50,820.11 174.29,815.91 173.03,811.21 171.74,806.01 170.40,800.34 169.03,794.21 167.62,787.63 166.18,780.61 164.71,773.18 163.21,765.34 161.68,757.12 160.13,748.52 158.55,739.56 156.94,730.26 155.32,720.62 153.68,710.67 152.02,700.42 150.35,689.88 148.66,679.08 146.97,668.01 145.26,656.70 143.54,645.17 141.82,633.42 140.10,621.48 138.37,609.35 136.64,597.05 134.91,584.60 133.18,572.00 131.46,559.29 129.75,546.46 128.04,533.54 126.34,520.54 124.66,507.47 122.99,494.35 121.33,481.19 119.70,468.01 118.08,454.83 116.48,441.65 114.90,428.49 113.35,415.37 111.83,402.31 110.33,389.30 108.86,376.38 107.43,363.55 106.03,350.84 104.66,338.25 103.33,325.79 102.04,313.50 100.79,301.37 99.58,289.42 98.42,277.67 97.30,266.14 96.23,254.83 95.22,243.77 94.25,232.96 93.33,222.42 92.47,212.17 91.67,202.22 90.93,192.59 90.24,183.28 89.62,174.32 89.07,165.73 88.58,157.50 88.15,149.66 87.80,142.23 87.52,135.22 87.31,128.64 87.17,122.50 87.12,116.83 87.14,111.64 87.24,106.93 87.42,102.74 87.69,99.06 88.04,95.92 88.48,93.33 89.01,91.31 89.63,89.86 90.35,89.01 91.16,88.77 92.06,89.16 93.06,90.18 Z" fill="url(#st)" fill-rule="evenodd" stroke="#ff9e6b" stroke-width="1.6"/>
<circle cx="93.65" cy="85.37" r="0.75" fill="#6ee0a0"/>
<circle cx="184.80" cy="837.33" r="2.00" fill="#e0b86e"/>
<circle cx="184.80" cy="837.33" r="0.60" fill="#13110d"/>
<circle cx="101.94" cy="93.22" r="0.75" fill="#6ee0a0"/>
<circle cx="191.20" cy="829.49" r="2.00" fill="#e0b86e"/>
<circle cx="191.20" cy="829.49" r="0.60" fill="#13110d"/>
<circle cx="110.19" cy="101.07" r="0.75" fill="#6ee0a0"/>
<circle cx="197.54" cy="821.64" r="2.00" fill="#e0b86e"/>
<circle cx="197.54" cy="821.64" r="0.60" fill="#13110d"/>
<circle cx="118.34" cy="108.92" r="0.75" fill="#6ee0a0"/>
<circle cx="203.81" cy="813.80" r="2.00" fill="#e0b86e"/>
<circle cx="203.81" cy="813.80" r="0.60" fill="#13110d"/>
<circle cx="126.47" cy="116.76" r="0.75" fill="#6ee0a0"/>
<circle cx="210.02" cy="805.95" r="2.00" fill="#e0b86e"/>
<circle cx="210.02" cy="805.95" r="0.60" fill="#13110d"/>
<circle cx="134.59" cy="124.61" r="0.75" fill="#6ee0a0"/>
<circle cx="216.22" cy="798.11" r="2.00" fill="#e0b86e"/>
<circle cx="216.22" cy="798.11" r="0.60" fill="#13110d"/>
<circle cx="142.62" cy="132.46" r="0.75" fill="#6ee0a0"/>
<circle cx="222.37" cy="790.26" r="2.00" fill="#e0b86e"/>
<circle cx="222.37" cy="790.26" r="0.60" fill="#13110d"/>
<circle cx="150.64" cy="140.30" r="0.75" fill="#6ee0a0"/>
<circle cx="228.47" cy="782.42" r="2.00" fill="#e0b86e"/>
<circle cx="228.47" cy="782.42" r="0.60" fill="#13110d"/>
<circle cx="158.61" cy="148.15" r="0.75" fill="#6ee0a0"/>
<circle cx="234.54" cy="774.57" r="2.00" fill="#e0b86e"/>
<circle cx="234.54" cy="774.57" r="0.60" fill="#13110d"/>
<circle cx="167.45" cy="155.95" r="0.75" fill="#6ee0a0"/>
<circle cx="241.02" cy="766.73" r="2.00" fill="#e0b86e"/>
<circle cx="241.02" cy="766.73" r="0.66" fill="#13110d"/>
<circle cx="176.22" cy="163.79" r="0.75" fill="#6ee0a0"/>
<circle cx="247.90" cy="758.88" r="2.00" fill="#e0b86e"/>
<circle cx="247.90" cy="758.88" r="0.62" fill="#13110d"/>
<circle cx="184.91" cy="171.64" r="0.75" fill="#6ee0a0"/>
<circle cx="254.70" cy="751.04" r="2.00" fill="#e0b86e"/>
<circle cx="254.70" cy="751.04" r="0.60" fill="#13110d"/>
<circle cx="193.52" cy="179.49" r="0.75" fill="#6ee0a0"/>
<circle cx="261.43" cy="743.19" r="2.00" fill="#e0b86e"/>
<circle cx="261.43" cy="743.19" r="0.60" fill="#13110d"/>
<circle cx="202.07" cy="187.34" r="0.75" fill="#6ee0a0"/>
<circle cx="268.08" cy="735.35" r="2.00" fill="#e0b86e"/>
<circle cx="268.08" cy="735.35" r="0.60" fill="#13110d"/>
<circle cx="210.62" cy="195.19" r="0.75" fill="#6ee0a0"/>
<circle cx="274.70" cy="727.50" r="2.00" fill="#e0b86e"/>
<circle cx="274.70" cy="727.50" r="0.60" fill="#13110d"/>
<circle cx="219.10" cy="203.04" r="0.75" fill="#6ee0a0"/>
<circle cx="281.29" cy="719.66" r="2.00" fill="#e0b86e"/>
<circle cx="281.29" cy="719.66" r="0.60" fill="#13110d"/>
<circle cx="227.46" cy="210.89" r="0.75" fill="#6ee0a0"/>
<circle cx="287.79" cy="711.81" r="2.00" fill="#e0b86e"/>
<circle cx="287.79" cy="711.81" r="0.60" fill="#13110d"/>
<circle cx="235.81" cy="218.73" r="0.75" fill="#6ee0a0"/>
<circle cx="294.22" cy="703.97" r="2.00" fill="#e0b86e"/>
<circle cx="294.22" cy="703.97" r="0.60" fill="#13110d"/>
<circle cx="244.11" cy="226.58" r="0.75" fill="#6ee0a0"/>
<circle cx="300.61" cy="696.12" r="2.00" fill="#e0b86e"/>
<circle cx="300.61" cy="696.12" r="0.60" fill="#13110d"/>
<circle cx="252.40" cy="234.43" r="0.75" fill="#6ee0a0"/>
<circle cx="306.98" cy="688.28" r="2.00" fill="#e0b86e"/>
<circle cx="306.98" cy="688.28" r="0.60" fill="#13110d"/>
<circle cx="260.55" cy="242.28" r="0.75" fill="#6ee0a0"/>
<circle cx="313.27" cy="680.43" r="2.00" fill="#e0b86e"/>
<circle cx="313.27" cy="680.43" r="0.60" fill="#13110d"/>
<circle cx="268.70" cy="250.13" r="0.75" fill="#6ee0a0"/>
<circle cx="319.50" cy="672.59" r="2.00" fill="#e0b86e"/>
<circle cx="319.50" cy="672.59" r="0.60" fill="#13110d"/>
<circle cx="276.86" cy="257.97" r="0.75" fill="#6ee0a0"/>
<circle cx="325.73" cy="664.74" r="2.00" fill="#e0b86e"/>
<circle cx="325.73" cy="664.74" r="0.60" fill="#13110d"/>
<circle cx="284.94" cy="265.82" r="0.75" fill="#6ee0a0"/>
<circle cx="331.92" cy="656.90" r="2.00" fill="#e0b86e"/>
<circle cx="331.92" cy="656.90" r="0.60" fill="#13110d"/>
<circle cx="293.03" cy="273.67" r="0.75" fill="#6ee0a0"/>
<circle cx="338.08" cy="649.05" r="2.00" fill="#e0b86e"/>
<circle cx="338.08" cy="649.05" r="0.60" fill="#13110d"/>
<circle cx="301.12" cy="281.51" r="0.75" fill="#6ee0a0"/>
<circle cx="344.24" cy="641.21" r="2.00" fill="#e0b86e"/>
<circle cx="344.24" cy="641.21" r="0.60" fill="#13110d"/>
<circle cx="309.14" cy="289.36" r="0.75" fill="#6ee0a0"/>
<circle cx="350.37" cy="633.36" r="2.00" fill="#e0b86e"/>
<circle cx="350.37" cy="633.36" r="0.60" fill="#13110d"/>
<circle cx="317.17" cy="297.20" r="0.75" fill="#6ee0a0"/>
<circle cx="356.47" cy="625.52" r="2.00" fill="#e0b86e"/>
<circle cx="356.47" cy="625.52" r="0.60" fill="#13110d"/>
<circle cx="325.19" cy="305.05" r="0.75" fill="#6ee0a0"/>
<circle cx="362.57" cy="617.67" r="2.00" fill="#e0b86e"/>
<circle cx="362.57" cy="617.67" r="0.60" fill="#13110d"/>
<circle cx="333.17" cy="312.90" r="0.75" fill="#6ee0a0"/>
<circle cx="368.64" cy="609.83" r="2.00" fill="#e0b86e"/>
<circle cx="368.64" cy="609.83" r="0.60" fill="#13110d"/>
<circle cx="341.14" cy="320.74" r="0.75" fill="#6ee0a0"/>
<circle cx="374.68" cy="601.98" r="2.00" fill="#e0b86e"/>
<circle cx="374.68" cy="601.98" r="0.60" fill="#13110d"/>
<circle cx="349.11" cy="328.59" r="0.75" fill="#6ee0a0"/>
<circle cx="380.73" cy="594.14" r="2.00" fill="#e0b86e"/>
<circle cx="380.73" cy="594.14" r="0.60" fill="#13110d"/>
<circle cx="357.03" cy="336.44" r="0.75" fill="#6ee0a0"/>
<circle cx="386.75" cy="586.29" r="2.00" fill="#e0b86e"/>
<circle cx="386.75" cy="586.29" r="0.60" fill="#13110d"/>
<circle cx="364.95" cy="344.28" r="0.75" fill="#6ee0a0"/>
<circle cx="392.75" cy="578.45" r="2.00" fill="#e0b86e"/>
<circle cx="392.75" cy="578.45" r="0.60" fill="#13110d"/>
<circle cx="372.88" cy="352.13" r="0.75" fill="#6ee0a0"/>
<circle cx="398.74" cy="570.60" r="2.00" fill="#e0b86e"/>
<circle cx="398.74" cy="570.60" r="0.60" fill="#13110d"/>
<circle cx="380.80" cy="359.97" r="0.75" fill="#6ee0a0"/>
<circle cx="404.74" cy="562.76" r="2.00" fill="#e0b86e"/>
<circle cx="404.74" cy="562.76" r="0.60" fill="#13110d"/>
<circle cx="388.69" cy="367.82" r="0.75" fill="#6ee0a0"/>
<circle cx="410.72" cy="554.91" r="2.00" fill="#e0b86e"/>
<circle cx="410.72" cy="554.91" r="0.60" fill="#13110d"/>
<circle cx="396.59" cy="375.66" r="0.75" fill="#6ee0a0"/>
<circle cx="416.69" cy="547.07" r="2.00" fill="#e0b86e"/>
<circle cx="416.69" cy="547.07" r="0.60" fill="#13110d"/>
<circle cx="404.48" cy="383.51" r="0.75" fill="#6ee0a0"/>
<circle cx="422.66" cy="539.22" r="2.00" fill="#e0b86e"/>
<circle cx="422.66" cy="539.22" r="0.60" fill="#13110d"/>
<circle cx="412.36" cy="391.35" r="0.75" fill="#6ee0a0"/>
<circle cx="428.61" cy="531.38" r="2.00" fill="#e0b86e"/>
<circle cx="428.61" cy="531.38" r="0.60" fill="#13110d"/>
<circle cx="420.23" cy="399.20" r="0.75" fill="#6ee0a0"/>
<circle cx="434.56" cy="523.53" r="2.00" fill="#e0b86e"/>
<circle cx="434.56" cy="523.53" r="0.60" fill="#13110d"/>
<circle cx="428.07" cy="407.05" r="0.75" fill="#6ee0a0"/>
<circle cx="440.49" cy="515.69" r="2.00" fill="#e0b86e"/>
<circle cx="440.49" cy="515.69" r="0.60" fill="#13110d"/>
<circle cx="435.90" cy="414.89" r="0.75" fill="#6ee0a0"/>
<circle cx="446.40" cy="507.84" r="2.00" fill="#e0b86e"/>
<circle cx="446.40" cy="507.84" r="0.60" fill="#13110d"/>
<circle cx="443.73" cy="422.74" r="0.75" fill="#6ee0a0"/>
<circle cx="452.30" cy="500.00" r="2.00" fill="#e0b86e"/>
<circle cx="452.30" cy="500.00" r="0.60" fill="#13110d"/>
<circle cx="451.57" cy="430.58" r="0.75" fill="#6ee0a0"/>
<circle cx="458.21" cy="492.15" r="2.00" fill="#e0b86e"/>
<circle cx="458.21" cy="492.15" r="0.60" fill="#13110d"/>
<circle cx="459.40" cy="438.43" r="0.75" fill="#6ee0a0"/>
<circle cx="464.12" cy="484.31" r="2.00" fill="#e0b86e"/>
<circle cx="464.12" cy="484.31" r="0.60" fill="#13110d"/>
<circle cx="467.23" cy="446.27" r="0.75" fill="#6ee0a0"/>
<circle cx="470.02" cy="476.46" r="2.00" fill="#e0b86e"/>
<circle cx="470.02" cy="476.46" r="0.60" fill="#13110d"/>
</svg>
```