import numpy as np
# D4 mid-string section, to scale
L=819.4; nat=0.0561*L; shp=0.1091*L          # 46.0, 89.4 mm below tip
dpr=2.1; rp=dpr/2; tdisc=2.0; daxle=3.0; pc=rp+0.635+0.8; Lh=pc+rp
S=4.4                                          # px/mm
z0=28; cx=470; topy=86
Y=lambda y:cx-y*S                              # +y to the LEFT
Z=lambda z:topy+(z-z0)*S
W,H=940,560
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a8f97"/><stop offset="1" stop-color="#4c5158"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset=".5" stop-color="#a6abb3"/><stop offset="1" stop-color="#565b63"/></linearGradient>
<radialGradient id="pin" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#e2e6ec"/><stop offset=".6" stop-color="#9aa0a8"/><stop offset="1" stop-color="#5e636b"/></radialGradient>
<marker id="arr" markerWidth="7" markerHeight="7" refX="3" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8aa0c0"/></marker></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="470" y="30" fill="#eef0f4" font-size="16" text-anchor="middle">yz section (depth × string) — D4, to scale · +y left, −y right</text>')
zt=z0; zb=104
# bars: inner faces y=+-6.5, 6.35 thick
out.append(f'<rect x="{Y(12.85):.1f}" y="{Z(zt):.1f}" width="{6.35*S:.1f}" height="{(zb-zt)*S:.1f}" fill="url(#bar)" stroke="#2d3036"/>')   # +y (left)
out.append(f'<rect x="{Y(-6.5):.1f}" y="{Z(zt):.1f}" width="{6.35*S:.1f}" height="{(zb-zt)*S:.1f}" fill="url(#bar)" stroke="#2d3036"/>')   # -y (right)
out.append(f'<text x="{Y(9.7):.1f}" y="{Z(zt)-8:.1f}" fill="#aeb3bd" font-size="11" text-anchor="middle">+y bar (left)</text>')
out.append(f'<text x="{Y(-9.7):.1f}" y="{Z(zt)-8:.1f}" fill="#aeb3bd" font-size="11" text-anchor="middle">−y bar (right)</text>')
# string at y=0
out.append(f'<line x1="{Y(0):.1f}" y1="{Z(zt):.1f}" x2="{Y(0):.1f}" y2="{Z(zb):.1f}" stroke="#b8924a" stroke-width="{1.27*S:.1f}" stroke-linecap="round"/>')
out.append(f'<text x="{Y(0)+8:.1f}" y="{Z(zb)-4:.1f}" fill="#b8924a" font-size="10">string y=0</text>')
def unit(zc,label,col):
    # disc edge-on on +y inner face: y [6.5-tdisc,6.5], z-extent = 2*Lh (engaged tips shown), prongs at +-Lh*0.8
    out.append(f'<rect x="{Y(6.5):.1f}" y="{Z(zc-Lh):.1f}" width="{tdisc*S:.1f}" height="{2*Lh*S:.1f}" rx="3" fill="url(#steel)" stroke="#eef0f4" stroke-width="1"/>')
    # two prongs reach from disc inner face (y=6.5-tdisc) to string (y=0), at +-(Lh*0.7) in z
    yroot=6.5-tdisc
    for sgn in (1,-1):
        pzc=zc+sgn*Lh*0.62
        out.append(f'<rect x="{Y(yroot):.1f}" y="{Z(pzc-rp):.1f}" width="{yroot*S:.1f}" height="{2*rp*S:.1f}" rx="{rp*S:.1f}" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>')
    # axle through +y bar
    out.append(f'<line x1="{Y(6.5-tdisc/2):.1f}" y1="{Z(zc):.1f}" x2="{Y(16):.1f}" y2="{Z(zc):.1f}" stroke="#cfd4da" stroke-width="{daxle*S:.1f}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{Y(6.5-tdisc/2):.1f}" cy="{Z(zc):.1f}" r="2.2" fill="#2a2d31"/>')
    # crank + rod (left/outer)
    out.append(f'<line x1="{Y(16):.1f}" y1="{Z(zc):.1f}" x2="{Y(16):.1f}" y2="{Z(zc-5):.1f}" stroke="#cfd4da" stroke-width="2.4"/>')
    out.append(f'<line x1="{Y(16):.1f}" y1="{Z(zc-5):.1f}" x2="{Y(16):.1f}" y2="{Z(zt):.1f}" stroke="#8aa0c0" stroke-width="2.4"/>')
    out.append(f'<text x="{Y(-14):.1f}" y="{Z(zc)+3:.1f}" fill="{col}" font-size="11">{label} (z={zc:.0f})</text>')
unit(nat,'natural','#c0a0ff')
unit(shp,'sharp','#ff8c5a')
# rod label
out.append(f'<text x="{Y(16)-6:.1f}" y="{Z(zt)+2:.1f}" fill="#8aa0c0" font-size="10" text-anchor="end">action rods ↑ pedal</text>')
# dims
def dim(y1,y2,zc,txt):
    out.append(f'<line x1="{Y(y1):.1f}" y1="{Z(zc):.1f}" x2="{Y(y2):.1f}" y2="{Z(zc):.1f}" stroke="#8a8f98" stroke-width="0.8"/>')
    out.append(f'<text x="{(Y(y1)+Y(y2))/2:.1f}" y="{Z(zc)-4:.1f}" fill="#8a8f98" font-size="10" text-anchor="middle">{txt}</text>')
dim(6.5,-6.5,zb-1,'gap 13')
out.append(f'<text x="{Y(0):.1f}" y="{Z(zb)+22:.1f}" fill="#8a8f98" font-size="11" text-anchor="middle">bar ¼\u2033(6.35) · disc t 2 · axle Ø3 · prong Ø{dpr} reach 6.5 · nat→sharp {shp-nat:.0f} mm apart</text>')
out.append('</svg>')
open('disc_yz_v9.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('disc_yz_v9.svg')
import cairosvg; cairosvg.svg2png(url='disc_yz_v9.svg',write_to='/tmp/chk.png',output_width=940)
print('built; nat z=%.0f sharp z=%.0f Lh=%.1f'%(nat,shp,Lh))
