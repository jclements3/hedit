import numpy as np, math
W,H=940,600; ENG=55.0; PR=30; rp=9
yN=95; yB=520; yNAT=180; ySHP=270           # neck, board, natural disc, sharp disc
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="cap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#737983"/></linearGradient>
<radialGradient id="pin" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#eef1f5"/><stop offset=".6" stop-color="#9aa0a8"/><stop offset="1" stop-color="#565b63"/></radialGradient></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
cols=[('FLAT',200,None),('NATURAL',470,'nat'),('SHARP',740,'shp')]
for name,cx,act in cols:
    out.append(f'<text x="{cx}" y="46" fill="#eef0f4" font-size="15" text-anchor="middle">pedal in {name.lower()}</text>')
    # active node = where the live length starts
    node_y = yN if act is None else (yNAT if act=='nat' else ySHP)
    # string: damped (dim) above node, live (bright) below
    out.append(f'<line x1="{cx}" y1="{yN}" x2="{cx}" y2="{node_y}" stroke="#5a5440" stroke-width="4"/>')
    out.append(f'<line x1="{cx}" y1="{node_y}" x2="{cx}" y2="{yB}" stroke="#f0c46a" stroke-width="5"/>')
    out.append(f'<text x="{cx-90}" y="{yN+4}" fill="#8a8f98" font-size="10">neck</text>')
    out.append(f'<text x="{cx-90}" y="{yB}" fill="#8a8f98" font-size="10">board</text>')
    out.append(f'<text x="{cx+12}" y="{(node_y+yB)/2}" fill="#f0c46a" font-size="10" transform="rotate(90 {cx+12} {(node_y+yB)/2})" text-anchor="middle">vibrating length</text>')

def disc(cx,cy,engaged,color,arrow,label):
    ang=-ENG if engaged else 0.0
    o=[f'<g transform="rotate({ang} {cx} {cy})">']
    o.append(f'<rect x="{cx-PR}" y="{cy-rp}" width="{2*PR}" height="{2*rp}" rx="{rp}" fill="url(#cap)" stroke="{color}" stroke-width="2"/>')
    for sgn in (1,-1): o.append(f'<circle cx="{cx+sgn*PR}" cy="{cy}" r="{rp-2.5}" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#23262b" stroke="#cfd4da" stroke-width="0.7"/></g>')
    o.append(f'<text x="{cx+PR+14}" y="{cy-PR-4}" fill="{color}" font-size="10">{label}</text>')
    if engaged:
        a=math.radians(ang)
        def rot(dx,dy): return (cx+dx*math.cos(a)-dy*math.sin(a), cy+dx*math.sin(a)+dy*math.cos(a))
        L=rot(-PR,0); R=rot(PR,0); lo=L if L[1]>R[1] else R
        o.append(f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="#9ad8b0"/>')
        o.append(f'<text x="{cx-PR-6}" y="{cy+16}" fill="#9ad8b0" font-size="9" text-anchor="end">pitch node</text>')
    if arrow:
        RA=PR+rp+10; aa=np.radians(np.linspace(40,150,18)); pts=" ".join("%.1f,%.1f"%(cx+RA*np.cos(t),cy-RA*np.sin(t)) for t in aa)
        o.append(f'<polyline points="{pts}" fill="none" stroke="#e0b86e" stroke-width="1.6"/>')
        ae=aa[-1]; tx,ty=-np.sin(ae),-np.cos(ae); ex,ey=cx+RA*np.cos(ae),cy-RA*np.sin(ae); nx,ny=-ty,tx
        o.append(f'<path d="M {ex+tx*8:.1f},{ey+ty*8:.1f} L {ex+nx*4.5:.1f},{ey+ny*4.5:.1f} L {ex-nx*4.5:.1f},{ey-ny*4.5:.1f} Z" fill="#e0b86e"/>')
        o.append(f'<text x="{cx}" y="{cy-RA-6}" fill="#e0b86e" font-size="9" text-anchor="middle">CCW</text>')
    return o

for name,cx,act in cols:
    neng = act in ('nat','shp'); seng = act=='shp'
    out+=disc(cx,yNAT,neng,'#c0a0ff', act=='nat', 'natural disc')
    out+=disc(cx,ySHP,seng,'#ff8c5a', act=='shp', 'sharp disc')
out.append('<text x="470" y="565" fill="#8a8f98" font-size="11" text-anchor="middle">one string, both discs · flat: free (full length) · natural: upper disc CCW · sharp: + lower disc CCW (natural stays)</text>')
out.append('<text x="470" y="585" fill="#8a8f98" font-size="11" text-anchor="middle">each engaged disc grips with its lower prong at the pitch node; the bright segment below is what vibrates</text>')
out.append('</svg>')
open('disc_state_v1.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('disc_state_v1.svg')
import cairosvg; cairosvg.svg2png(url='disc_state_v1.svg',write_to='/tmp/chk.png',output_width=940)
print('built')
