import numpy as np
# one octave C2..B2 to show all 7 classes -> bars
names=['C2','D2','E2','F2','G2','A2','B2']; cls=['C','D','E','F','G','A','B']
OD=[1.016,0.914,2.642,2.489,2.337,2.184,2.057]   # from table around C2..B2
topbar={'E','F','G','A'}                          # +y (top)
c2c=[13.0+(OD[i]+OD[i+1])/2 for i in range(len(OD)-1)]
x=np.concatenate([[0],np.cumsum(c2c)])
S=7.0; x0=140
X=lambda xx:x0+xx*S
yc=300; yT=yc-6.5*S; yB=yc+6.5*S                  # +y top rail, -y bottom rail, string at yc
W,H=940,520
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#6a6f78"/></linearGradient>
<radialGradient id="pin" cx=".4" cy=".4" r=".7"><stop offset="0" stop-color="#e2e6ec"/><stop offset="1" stop-color="#6a6f78"/></radialGradient></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="470" y="32" fill="#eef0f4" font-size="16" text-anchor="middle">neck plan (looking down the strings) — class → bar assignment</text>')
out.append('<text x="470" y="52" fill="#8a8f98" font-size="11" text-anchor="middle">+y bar = E F G A (right foot)  ·  −y bar = D C B (left foot)  ·  prongs reach the string at y=0</text>')
# bar rails (¼" thick)
out.append(f'<rect x="{X(-6):.0f}" y="{yT-6.35*S/2:.1f}" width="{(x[-1]+12)*S:.0f}" height="{6.35*S:.1f}" fill="#3a3e44" stroke="#2d3036"/>')
out.append(f'<rect x="{X(-6):.0f}" y="{yB-6.35*S/2:.1f}" width="{(x[-1]+12)*S:.0f}" height="{6.35*S:.1f}" fill="#3a3e44" stroke="#2d3036"/>')
out.append(f'<text x="{X(-6)-6:.0f}" y="{yT+4:.0f}" fill="#9ad8b0" font-size="11" text-anchor="end">+y</text>')
out.append(f'<text x="{X(-6)-6:.0f}" y="{yB+4:.0f}" fill="#e0b86e" font-size="11" text-anchor="end">−y</text>')
# control-rod placeholder rails
for yy,c,lab in [(yT-6.35*S/2-9,'#9ad8b0','natural rods (next)'),(yT-6.35*S/2-20,'#7fb0ff','sharp rods (next)'),
                 (yB+6.35*S/2+12,'#e0b86e','natural rods (next)'),(yB+6.35*S/2+23,'#ff9a5a','sharp rods (next)')]:
    out.append(f'<line x1="{X(-6):.0f}" y1="{yy:.0f}" x2="{X(x[-1]+6):.0f}" y2="{yy:.0f}" stroke="{c}" stroke-width="1.2" stroke-dasharray="5 5" opacity="0.55"/>')
out.append(f'<text x="{X(x[-1]+6):.0f}" y="{yT-6.35*S/2-24:.0f}" fill="#8a8f98" font-size="9" text-anchor="end">control rods → up pillar (next)</text>')
# strings + discs
Lh=3.6; tdisc=2.0; rp=1.0
for i,(nm,cl,od) in enumerate(zip(names,cls,OD)):
    xs=X(x[i])
    top = cl in topbar
    col = '#9ad8b0' if top else '#e0b86e'
    bh=6.35*S/2
    out.append(f'<circle cx="{xs:.1f}" cy="{yc:.1f}" r="{max(od/2*S,2):.1f}" fill="#b8924a"/>')
    if top:
        face=yT+bh; dtop=face; dbot=face+tdisc*S; proot=dbot
    else:
        face=yB-bh; dbot=face; dtop=face-tdisc*S; proot=dtop
    # prongs first (under disc), from disc face to string
    for sgn in (1,-1):
        px=xs+sgn*Lh*0.55*S
        out.append(f'<line x1="{px:.1f}" y1="{proot:.1f}" x2="{px:.1f}" y2="{yc:.1f}" stroke="#b6bcc4" stroke-width="{2*rp*S:.1f}" stroke-linecap="round"/>')
    out.append(f'<rect x="{xs-Lh*S:.1f}" y="{dtop:.1f}" width="{2*Lh*S:.1f}" height="{tdisc*S:.1f}" rx="3" fill="url(#steel)" stroke="#eef0f4" stroke-width="0.8"/>')
    out.append(f'<circle cx="{xs:.1f}" cy="{face:.1f}" r="2" fill="#2a2d31"/>')
    out.append(f'<text x="{xs:.1f}" y="{yc + (26 if top else -18):.0f}" fill="{col}" font-size="11" text-anchor="middle">{nm}</text>')
out.append(f'<text x="470" y="500" fill="#8a8f98" font-size="11" text-anchor="middle">neighbours on opposite bars (e.g. D2↓ next to E2↑) lie in different depth planes — no collision</text>')
out.append('</svg>')
open('neck_plan_v2.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('neck_plan_v2.svg')
import cairosvg; cairosvg.svg2png(url='neck_plan_v2.svg',write_to='/tmp/chk.png',output_width=940)
print('plan built')
