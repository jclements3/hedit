import numpy as np
W,H=940,560; ENG=55.0; RD=58; PR=40
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('<defs><marker id="ccw" markerWidth="9" markerHeight="9" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#e0b86e"/></marker></defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
cols=[('pedal in flat',False,False),('pedal in natural',True,False),('pedal in sharp',True,True)]
cx0=[200,470,740]
for c,(title,_,_2) in enumerate(cols):
    out.append(f'<text x="{cx0[c]}" y="40" fill="#eef0f4" font-size="14" text-anchor="middle">{title}</text>')
out.append('<text x="60" y="180" fill="#c0a0ff" font-size="12" transform="rotate(-90 60 180)" text-anchor="middle">NATURAL disc</text>')
out.append('<text x="60" y="430" fill="#ff8c5a" font-size="12" transform="rotate(-90 60 430)" text-anchor="middle">SHARP disc</text>')

def disc(cx,cy,engaged,color,arrow):
    o=[f'<line x1="{cx}" y1="{cy-RD-22}" x2="{cx}" y2="{cy+RD+22}" stroke="#b8924a" stroke-width="5"/>']  # string
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{RD}" fill="none" stroke="#cfd4da" stroke-width="2"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#23262b" stroke="#9aa0a8"/>')                       # axle
    base=ENG if engaged else 0.0
    for t,role in [(0+base,'up'),(180+base,'lo')]:
        a=np.radians(t); px,py=cx+PR*np.cos(a), cy-PR*np.sin(a)
        o.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="7" fill="none" stroke="{color}" stroke-width="3"/>')
    if engaged:
        # lower prong = pitch point (node); upper prong grabs above
        a=np.radians(180+base); lx,ly=cx+PR*np.cos(a),cy-np.sin(a)*PR
        au=np.radians(0+base); ux,uy=cx+PR*np.cos(au),cy-np.sin(au)*PR
        o.append(f'<circle cx="{cx}" cy="{ly:.0f}" r="3.2" fill="#9ad8b0"/>')                              # node on string
        o.append(f'<text x="{cx-PR-6}" y="{ly+16:.0f}" fill="#9ad8b0" font-size="9" text-anchor="end">pitch pt</text>')
        o.append(f'<text x="{ux+10:.0f}" y="{uy-6:.0f}" fill="#cfd4da" font-size="9">grabs above</text>')
    if arrow:
        RA=RD+12; aa=np.radians(np.linspace(38,150,24))      # over-the-top, right->left = CCW
        pts=" ".join("%.1f,%.1f"%(cx+RA*np.cos(a),cy-RA*np.sin(a)) for a in aa)
        o.append(f'<polyline points="{pts}" fill="none" stroke="#e0b86e" stroke-width="1.8"/>')
        ae=aa[-1]; tx,ty=-np.sin(ae),-np.cos(ae)             # CCW screen tangent at end
        ex,ey=cx+RA*np.cos(ae),cy-RA*np.sin(ae); nx,ny=-ty,tx
        o.append(f'<path d="M {ex+tx*9:.1f},{ey+ty*9:.1f} L {ex+nx*5:.1f},{ey+ny*5:.1f} L {ex-nx*5:.1f},{ey-ny*5:.1f} Z" fill="#e0b86e"/>')
        o.append(f'<text x="{cx}" y="{cy-RD-16}" fill="#e0b86e" font-size="10" text-anchor="middle">CCW</text>')
    return o

# rows: natural disc (cy=170), sharp disc (cy=420)
# flat: none engaged | natural: nat engaged | sharp: nat+sharp engaged
states=[(False,False),(True,False),(True,True)]
for c,(neng,seng) in enumerate(states):
    out+=disc(cx0[c],170,neng,'#c0a0ff', neng and not (c==2))   # arrow when it's the one just moved
    out+=disc(cx0[c],420,seng,'#ff8c5a', seng)
# fix arrows: show CCW on the disc that engages in that column
out.append('<text x="470" y="540" fill="#8a8f98" font-size="11" text-anchor="middle">flat: prongs horizontal, string free · natural: natural disc CCW · sharp: + sharp disc CCW (natural stays)</text>')
out.append('</svg>')
open('engage_v2.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('engage_v2.svg')
import cairosvg; cairosvg.svg2png(url='engage_v2.svg',write_to='/tmp/chk.png',output_width=940)
print('built')
