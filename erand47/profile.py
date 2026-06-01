import numpy as np
g={}; exec(open('gen.py').read(), g)
Ro=g['Ro']; Ri=g['Ri']; neck=g['neck']; eb=g['eb']; natpts=g['natpts']; shppts=g['shppts']; N=g['N_STRINGS']
C1o=g['C1o']                                   # pillar outer cap (pre-rake)
rake=g['rake']; C1o_r=rake(C1o)                # raked pillar edge (bass end)
allp=np.vstack([Ro,Ri]); x0,x1=allp[:,0].min(),allp[:,0].max(); z0,z1=allp[:,1].min(),allp[:,1].max()
S=0.34; MX=150; MTOP=64; BASE=210
W=max(int((x1-x0)*S)+2*MX, 680)
Hframe=int((z1-z0)*S); H=Hframe+MTOP+BASE
X=lambda x:(x-x0)*S+MX; Z=lambda z:(z1-z)*S+MTOP
def poly(P): return " ".join("%.1f,%.1f"%(X(p[0]),Z(p[1])) for p in P)
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="frame" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8ccd3"/><stop offset=".5" stop-color="#9094a0"/><stop offset="1" stop-color="#54585f"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#6a6f78"/></linearGradient>
<marker id="rot" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L7,4 L0,8 Z" fill="#e0b86e"/></marker></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append(f'<text x="{W/2:.0f}" y="32" fill="#eef0f4" font-size="15" text-anchor="middle">erand47 profile — pedals → control rods → bell-crank → discs</text>')
out.append(f'<path d="M {poly(Ro)} Z M {poly(Ri)} Z" fill="url(#frame)" fill-rule="evenodd" stroke="#ff9e6b" stroke-width="1.1"/>')
for i in range(N):
    out.append(f'<line x1="{X(neck[i,0]):.1f}" y1="{Z(neck[i,1]):.1f}" x2="{X(eb[i,0]):.1f}" y2="{Z(eb[i,1]):.1f}" stroke="#7d7762" stroke-width="0.5"/>')
out.append(f'<polyline points="{poly(natpts)}" fill="none" stroke="#c0a0ff" stroke-width="2.2" opacity="0.9"/>')
out.append(f'<polyline points="{poly(shppts)}" fill="none" stroke="#ff8c5a" stroke-width="2.2" opacity="0.9"/>')
for i in range(0,N,6):
    p=natpts[i]; out.append(f'<circle cx="{X(p[0]):.1f}" cy="{Z(p[1]):.1f}" r="2.3" fill="url(#steel)" stroke="#eef0f4" stroke-width="0.5"/>')
# bell-crank at pillar top (bass neck tip)
bx,bzt=X(neck[0,0]),Z(neck[0,1]); bcx,bcy=bx-4,bzt-2
out.append(f'<circle cx="{bcx:.0f}" cy="{bcy:.0f}" r="12" fill="#2a2d31" stroke="#e0b86e" stroke-width="2"/>')
out.append(f'<line x1="{bcx:.0f}" y1="{bcy:.0f}" x2="{bcx+36:.0f}" y2="{bcy+2:.0f}" stroke="#e0b86e" stroke-width="3"/>')
out.append(f'<path d="M {bcx+12},{bcy-9} A 15 15 0 0 1 {bcx+15},{bcy+6}" fill="none" stroke="#e0b86e" stroke-width="1.5" marker-end="url(#rot)"/>')
out.append(f'<text x="{bcx:.0f}" y="{bcy-16:.0f}" fill="#e0b86e" font-size="12" text-anchor="middle">bell-crank (vert→rotary)</text>')
# neck distribution rods along disc band
out.append(f'<line x1="{bcx+36:.0f}" y1="{bcy+2:.0f}" x2="{X(natpts[-1,0]):.0f}" y2="{Z(natpts[-1,1]):.0f}" stroke="#9ad8b0" stroke-width="1.2" stroke-dasharray="6 5" opacity="0.75"/>')
out.append(f'<text x="{X(natpts[len(natpts)//2,0]):.0f}" y="{Z(natpts[len(natpts)//2,1])-8:.0f}" fill="#9ad8b0" font-size="10" text-anchor="middle">neck rods → class discs</text>')
# control rods follow the pillar edge down, then to base
pil=C1o_r.copy()
if Z(pil[-1,1])<Z(pil[0,1]): pil=pil[::-1]   # order top(bell-crank)->bottom(base)
rod=[(bcx,bcy)]+[(X(p[0])-3,Z(p[1])) for p in pil]
base_cx=rod[-1][0]; base_top=rod[-1][1]
pedy=base_top+90
out.append('<polyline points="%s" fill="none" stroke="#7fb0ff" stroke-width="2.4"/>'%" ".join("%.1f,%.1f"%(a,b) for a,b in rod))
out.append('<polyline points="%s" fill="none" stroke="#7fb0ff" stroke-width="2.4" opacity="0.6"/>'%" ".join("%.1f,%.1f"%(a+5,b) for a,b in rod))
out.append(f'<line x1="{base_cx:.0f}" y1="{base_top:.0f}" x2="{base_cx:.0f}" y2="{pedy:.0f}" stroke="#7fb0ff" stroke-width="2.4"/>')
mid=rod[len(rod)//2]
out.append(f'<text x="{mid[0]-12:.0f}" y="{mid[1]:.0f}" fill="#7fb0ff" font-size="11" transform="rotate(-90 {mid[0]-12:.0f} {mid[1]:.0f})" text-anchor="middle">control rods up pillar (×7)</text>')
# pedal base
boxw=300; boxh=64; boxx=base_cx-boxw*0.28; boxy=pedy
out.append(f'<rect x="{boxx:.0f}" y="{boxy:.0f}" width="{boxw}" height="{boxh}" rx="8" fill="#23262b" stroke="#5a5f66"/>')
peds=['D','C','B','E','F','G','A']
for k,p in enumerate(peds):
    px=boxx+28+k*(boxw-56)/6; col='#c8d0ff' if p in 'DCB' else '#ffd0a0'
    out.append(f'<line x1="{px:.0f}" y1="{boxy+18:.0f}" x2="{px:.0f}" y2="{boxy+boxh-9:.0f}" stroke="{col}" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<text x="{px:.0f}" y="{boxy+13:.0f}" fill="{col}" font-size="11" text-anchor="middle">{p}</text>')
out.append(f'<text x="{boxx+boxw/2:.0f}" y="{boxy+boxh+20:.0f}" fill="#cdd2da" font-size="11" text-anchor="middle">pedal base · Left foot D C B · Right foot E F G A · 3 notches ♭/♮/♯</text>')
out.append(f'<text x="{bcx-16:.0f}" y="{(bcy+base_top)/2:.0f}" fill="#aeb3bd" font-size="11" transform="rotate(-90 {bcx-16:.0f} {(bcy+base_top)/2:.0f})" text-anchor="middle">pillar (bass / C1)</text>')
out.append('</svg>')
open('harp_profile_v3.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('harp_profile_v3.svg')
import cairosvg; cairosvg.svg2png(url='harp_profile_v3.svg',write_to='/tmp/chk.png',output_width=760)
print('v2 W,H=',W,H)
