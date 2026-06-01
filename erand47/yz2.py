import numpy as np
S=4.2; W,H=940,560
def panel(ox, title, side, Lstr, nat, shp, dpr, col):
    rp=dpr/2; tdisc=2.0; daxle=3.0; pc=rp+0.635+0.8; Lh=pc+rp
    z0=24; topy=92; cx=ox
    Y=lambda y:cx - (y if side=='+y' else -y)*S      # mount bar drawn on the LEFT of each panel
    Z=lambda z:topy+(z-z0)*S
    o=[]
    o.append(f'<text x="{ox}" y="64" fill="{col}" font-size="13" text-anchor="middle">{title}</text>')
    zt,zb=z0,108
    # bars: mount bar (inner face at +6.5 in local) on left, far bar on right
    o.append(f'<rect x="{Y(12.85):.1f}" y="{Z(zt):.1f}" width="{6.35*S:.1f}" height="{(zb-zt)*S:.1f}" fill="url(#bar)" stroke="#2d3036"/>')
    o.append(f'<rect x="{Y(-6.5):.1f}" y="{Z(zt):.1f}" width="{6.35*S:.1f}" height="{(zb-zt)*S:.1f}" fill="url(#bar)" stroke="#2d3036"/>')
    o.append(f'<text x="{Y(9.7):.1f}" y="{Z(zt)-8:.1f}" fill="#aeb3bd" font-size="10" text-anchor="middle">{side} bar (mount)</text>')
    far='−y' if side=='+y' else '+y'
    o.append(f'<text x="{Y(-9.7):.1f}" y="{Z(zt)-8:.1f}" fill="#7f858d" font-size="10" text-anchor="middle">{far} bar</text>')
    o.append(f'<line x1="{Y(0):.1f}" y1="{Z(zt):.1f}" x2="{Y(0):.1f}" y2="{Z(zb):.1f}" stroke="#b8924a" stroke-width="{1.3*S:.1f}" stroke-linecap="round"/>')
    o.append(f'<text x="{Y(0)+7:.1f}" y="{Z(zb)-4:.1f}" fill="#b8924a" font-size="9">y=0</text>')
    def unit(zc,lab,c):
        o.append(f'<rect x="{Y(6.5):.1f}" y="{Z(zc-Lh):.1f}" width="{tdisc*S:.1f}" height="{2*Lh*S:.1f}" rx="3" fill="url(#steel)" stroke="#eef0f4" stroke-width="1"/>')
        yroot=6.5-tdisc
        for sgn in (1,-1):
            pzc=zc+sgn*Lh*0.62
            o.append(f'<rect x="{Y(yroot):.1f}" y="{Z(pzc-rp):.1f}" width="{yroot*S:.1f}" height="{2*rp*S:.1f}" rx="{rp*S:.1f}" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>')
        o.append(f'<line x1="{Y(6.5-tdisc/2):.1f}" y1="{Z(zc):.1f}" x2="{Y(16):.1f}" y2="{Z(zc):.1f}" stroke="#cfd4da" stroke-width="{daxle*S:.1f}" stroke-linecap="round"/>')
        o.append(f'<circle cx="{Y(6.5-tdisc/2):.1f}" cy="{Z(zc):.1f}" r="2" fill="#2a2d31"/>')
        o.append(f'<text x="{Y(-13):.1f}" y="{Z(zc)+3:.1f}" fill="{c}" font-size="10">{lab}</text>')
    unit(nat,'♮ nat','#c0a0ff'); unit(shp,'♯ sharp','#ff8c5a')
    # prong-direction arrow
    o.append(f'<text x="{ox}" y="{Z(zb)+20:.1f}" fill="#8a8f98" font-size="10" text-anchor="middle">prongs → y=0 (reach 6.5)</text>')
    return o
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a8f97"/><stop offset="1" stop-color="#4c5158"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset=".5" stop-color="#a6abb3"/><stop offset="1" stop-color="#565b63"/></linearGradient>
<radialGradient id="pin" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#e2e6ec"/><stop offset=".6" stop-color="#9aa0a8"/><stop offset="1" stop-color="#5e636b"/></radialGradient></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="470" y="30" fill="#eef0f4" font-size="16" text-anchor="middle">yz mounting by class — each disc on its pedal-side bar, prongs toward y=0</text>')
out+=panel(255,'E,F,G,A class → +y bar (e.g. F4)','+y',724.5,40.6,79.0,2.0,'#9ad8b0')
out+=panel(690,'D,C,B class → −y bar (e.g. C4)','−y',851.0,47.7,92.8,2.0,'#e0b86e')
out.append('<text x="470" y="544" fill="#8a8f98" font-size="11" text-anchor="middle">both discs of a string share its class bar · opposite-class neighbours sit in different depth planes</text>')
out.append('</svg>')
open('disc_yz_v10.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('disc_yz_v10.svg')
import cairosvg; cairosvg.svg2png(url='disc_yz_v10.svg',write_to='/tmp/chk.png',output_width=940)
print('yz v10 built')
