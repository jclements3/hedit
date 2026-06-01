import numpy as np, math
W,H=940,560; ENG=55.0; PR=36; rp=11; EXT=PR+rp
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="cap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#737983"/></linearGradient>
<radialGradient id="pin" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#eef1f5"/><stop offset=".6" stop-color="#9aa0a8"/><stop offset="1" stop-color="#565b63"/></radialGradient>
</defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
for c,(title,x) in enumerate([('pedal in flat',200),('pedal in natural',470),('pedal in sharp',740)]):
    out.append(f'<text x="{x}" y="40" fill="#eef0f4" font-size="14" text-anchor="middle">{title}</text>')
out.append('<text x="58" y="180" fill="#c0a0ff" font-size="12" transform="rotate(-90 58 180)" text-anchor="middle">NATURAL disc</text>')
out.append('<text x="58" y="420" fill="#ff8c5a" font-size="12" transform="rotate(-90 58 420)" text-anchor="middle">SHARP disc</text>')

def disc(cx,cy,engaged,color,arrow):
    ang = -ENG if engaged else 0.0     # SVG rotate: negative = CCW
    o=[f'<line x1="{cx}" y1="{cy-EXT-20}" x2="{cx}" y2="{cy+EXT+20}" stroke="#b8924a" stroke-width="5"/>']
    o.append(f'<g transform="rotate({ang} {cx} {cy})">')
    o.append(f'<rect x="{cx-PR}" y="{cy-rp}" width="{2*PR}" height="{2*rp}" rx="{rp}" fill="url(#cap)" stroke="{color}" stroke-width="2.2"/>')
    for sgn in (1,-1):
        o.append(f'<circle cx="{cx+sgn*PR}" cy="{cy}" r="{rp-2.5}" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.8"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="#23262b" stroke="#cfd4da" stroke-width="0.8"/>')
    o.append('</g>')
    if engaged:
        a=math.radians(ang)
        def rot(dx,dy): return (cx+dx*math.cos(a)-dy*math.sin(a), cy+dx*math.sin(a)+dy*math.cos(a))
        L=rot(-PR,0); R=rot(PR,0)
        lo,hi=(L,R) if L[1]>R[1] else (R,L)            # lower prong = pitch node
        o.append(f'<circle cx="{cx}" cy="{lo[1]:.0f}" r="3.4" fill="#9ad8b0"/>')
        o.append(f'<text x="{lo[0]-rp-4:.0f}" y="{lo[1]+14:.0f}" fill="#9ad8b0" font-size="9" text-anchor="end">pitch pt</text>')
        o.append(f'<text x="{hi[0]+rp+4:.0f}" y="{hi[1]-4:.0f}" fill="#cfd4da" font-size="9">grabs above</text>')
    if arrow:
        RA=EXT+12; aa=np.radians(np.linspace(38,150,24))
        pts=" ".join("%.1f,%.1f"%(cx+RA*np.cos(t),cy-RA*np.sin(t)) for t in aa)
        o.append(f'<polyline points="{pts}" fill="none" stroke="#e0b86e" stroke-width="1.8"/>')
        ae=aa[-1]; tx,ty=-np.sin(ae),-np.cos(ae); ex,ey=cx+RA*np.cos(ae),cy-RA*np.sin(ae); nx,ny=-ty,tx
        o.append(f'<path d="M {ex+tx*9:.1f},{ey+ty*9:.1f} L {ex+nx*5:.1f},{ey+ny*5:.1f} L {ex-nx*5:.1f},{ey-ny*5:.1f} Z" fill="#e0b86e"/>')
        o.append(f'<text x="{cx}" y="{cy-EXT-16}" fill="#e0b86e" font-size="10" text-anchor="middle">CCW</text>')
    return o

cxs=[200,470,740]
for c,(neng,seng) in enumerate([(False,False),(True,False),(True,True)]):
    out+=disc(cxs[c],170,neng,'#c0a0ff', c==1)     # natural disc engages going flat->natural
    out+=disc(cxs[c],420,seng,'#ff8c5a', c==2)     # sharp disc engages going natural->sharp
out.append('<text x="470" y="540" fill="#8a8f98" font-size="11" text-anchor="middle">capsule disc, round prong-pins at the tips · flat=horizontal · engage = rotate CCW · lower prong = pitch node</text>')
out.append('</svg>')
open('engage_v3.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('engage_v3.svg')
import cairosvg; cairosvg.svg2png(url='engage_v3.svg',write_to='/tmp/chk.png',output_width=940)
print('v3 built')
