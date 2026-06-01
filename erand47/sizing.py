import numpy as np
N=47
notes=['C1','D1','E1','F1','G1','A1','B1','C2','D2','E2','F2','G2','A2','B2','C3','D3','E3','F3','G3','A3','B3','C4','D4','E4','F4','G4','A4','B4','C5','D5','E5','F5','G5','A5','B5','C6','D6','E6','F6','G6','A6','B6','C7','D7','E7','F7','G7']
L=np.linspace(1514.93,60.61,N)
T=np.linspace(52.693,10.976,N)*4.448222          # N
DIA=np.array([1.676,1.549,1.448,1.270,1.219,1.219,1.016,1.016,0.914,2.642,2.489,2.337,2.184,2.057,2.057,1.930,1.676,1.676,1.549,1.549,1.270,1.270,1.270,1.143,1.143,1.143,1.016,1.016,1.016,0.914,0.914,0.914,0.813,0.813,0.813,0.813,0.762,0.762,0.762,0.711,0.711,0.660,0.635,0.635,0.635,0.635,0.635])
c2c=np.array([13.0+(DIA[i]+DIA[i+1])/2 for i in range(N-1)]); c2c=np.append(c2c,c2c[-1])

# ---- assumptions ----
WRAP=np.radians(15)          # engaged total wrap at the prong
Fside=2*T*np.sin(WRAP/2)     # lateral load per prong contact (N)
GAP=13.0; ell=GAP/2          # prong reach: inner face (y=+6.5) to string centre (y=0) = 6.5 mm
SIG=300.0; TAU=180.0; E=193e3
AIRn=0.5; AIRs=0.8           # disengaged air clearance / side (vibration): natural / sharp rows

# ---- prong: cantilever bending ----
dprong=(32*Fside*ell/(np.pi*SIG))**(1/3)
rp=np.ceil(dprong*2)/2/... if False else np.maximum(dprong/2,0.0)
# round prong dia up to 0.1
dprong_r=np.ceil(dprong*10)/10
rp=dprong_r/2
I=np.pi*dprong_r**4/64; defl=Fside*ell**3/(3*E*I)   # prong tip deflection (mm)

# ---- prong-centre radius from disengaged clearance (use sharp row, worst) ----
pc=rp+DIA/2+AIRs
Lh=pc+rp                    # disc half length (tip)
swept=2*Lh                  # swept circle dia when rotating about axle

# ---- disc thickness: disc as cantilever axle->prong, len pc, width w ----
w=2*(rp+0.3)
tdisc=np.sqrt(6*Fside*pc/(w*SIG))

# ---- axle: torsion (both prongs at radius pc, opposite -> couple) ----
Q=2*Fside*pc                # N*mm torque the rod must hold / axle transmits
daxle=(16*Q/(np.pi*TAU))**(1/3)

# ---- collisions ----
neigh_clear=c2c-swept                       # same-row neighbour
zsep=(2**(-1/12.) , )  # placeholder
Fnat=1-2**(-1/12); Fshp=1-2**(-1/6)
zsep=(Fshp-Fnat)*L                          # nat<->sharp z separation on same string
same_clear=zsep-swept                       # >0 => the two discs' swept circles clear

def row(i):
    return (notes[i],DIA[i],T[i],Fside[i],dprong_r[i],defl[i]*1000,tdisc[i],daxle[i],swept[i],c2c[i],neigh_clear[i],zsep[i],same_clear[i])
hdr="note  OD    T(N)  Fpr  prong defl(um) tdisc axle swept c-c nClr zsep sClr"
print(hdr)
for i in [0,9,15,22,29,36,42,46]:
    n,od,t,f,dp,df,td,ax,sw,cc,nc,zs,sc=row(i)
    print(f"{n:3s} {od:5.2f} {t:5.0f} {f:4.0f} {dp:4.1f} {df:7.1f} {td:5.2f} {ax:4.2f} {sw:4.1f} {cc:4.1f} {nc:5.1f} {zs:5.1f} {sc:5.1f}")
print()
print("prong dia range  %.1f .. %.1f mm"%(dprong_r.min(),dprong_r.max()))
print("disc thick range %.2f .. %.2f mm"%(tdisc.min(),tdisc.max()))
print("axle dia range   %.2f .. %.2f mm  (stress-min)"%(daxle.min(),daxle.max()))
print("swept dia range  %.1f .. %.1f mm"%(swept.min(),swept.max()))
print("min same-row neighbour clearance %.1f mm (string %s)"%(neigh_clear.min(),notes[neigh_clear.argmin()]))
# same-string nat/sharp collision: where zsep < swept
bad=np.where(same_clear<0)[0]
print("nat/sharp discs COLLIDE (zsep<swept) for:",[notes[i] for i in bad])
ok=np.where(same_clear>=0)[0]
print("highest string that still fits BOTH discs:",notes[ok.max()], "(sClr %.1f)"%same_clear[ok.max()])
