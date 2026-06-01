import numpy as np
N=47
DIA=np.array([1.676,1.549,1.448,1.270,1.219,1.219,1.016,1.016,0.914,2.642,2.489,2.337,2.184,2.057,2.057,1.930,1.676,1.676,1.549,1.549,1.270,1.270,1.270,1.143,1.143,1.143,1.016,1.016,1.016,0.914,0.914,0.914,0.813,0.813,0.813,0.813,0.762,0.762,0.762,0.711,0.711,0.660,0.635,0.635,0.635,0.635,0.635])
T=np.linspace(52.693,10.976,N)*4.448222   # tension N
AIR=13.0
c2c=np.array([AIR+(DIA[i]+DIA[i+1])/2 for i in range(N-1)])
notes=['C1','D1','E1','F1','G1','A1','B1','C2','D2','E2','F2','G2','A2','B2','C3','D3','E3','F3','G3','A3','B3','C4','D4','E4','F4','G4','A4','B4','C5','D5','E5','F5','G5','A5','B5','C6','D6','E6','F6','G6','A6','B6','C7','D7','E7','F7','G7']
clr=0.4               # diametral clearance string-to-prong
wrap=np.radians(8)    # half-kink each prong contact
def line(i):
    cc=c2c[i] if i<N-1 else c2c[-1]
    fork=DIA[i]+clr
    lat=2*T[i]*np.sin(wrap)         # lateral pinch load on a prong (both contacts ~equal)
    # min prong dia so cantilever (proj=7mm) stays under 250 MPa hardened-steel allowable
    proj=7.0; allow=250.0
    dpin=(32*lat*proj/(np.pi*allow))**(1/3)
    discmax=cc-0.6                  # must clear same-row neighbour (0.6 gap)
    return notes[i],DIA[i],fork,lat,dpin,cc,discmax
print('note  OD    fork  latN  pin>  c-c   discMax')
for i in [0,9,15,22,29,36,46]:
    nm,od,fk,lt,dp,cc,dm=line(i)
    print(f'{nm:3s} {od:5.3f} {fk:5.2f} {lt:5.0f} {dp:5.2f} {cc:5.1f} {dm:5.1f}')
print()
print('fork opening range: %.2f .. %.2f mm'%(min(DIA)+clr,max(DIA)+clr))
print('disc-OD ceiling (min c-c - 0.6): %.1f mm'%(c2c.min()-0.6))
