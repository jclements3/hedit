import numpy as np
W,H=980,560
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="tan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1d79a"/><stop offset="1" stop-color="#d8b56a"/></linearGradient>
<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d7dade"/><stop offset="1" stop-color="#9aa0a8"/></linearGradient></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="490" y="32" fill="#eef0f4" font-size="16" text-anchor="middle">C-natural relay (one class, one y-plane) — ternary disc levers + binary links</text>')
yline=330; ytop=250
def ground(x,y):
    o=[f'<line x1="{x-16}" y1="{y+12}" x2="{x+16}" y2="{y+12}" stroke="#8a8f98" stroke-width="2"/>']
    for k in range(-2,3):
        o.append(f'<line x1="{x+k*7}" y1="{y+12}" x2="{x+k*7-6}" y2="{y+20}" stroke="#8a8f98" stroke-width="1.5"/>')
    return o
def hole(x,y,r=6): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="#7a6a3a" stroke-width="1.5"/>'
def lever(xa, lab):
    xi,yi=xa-46,ytop; xo,yo=xa+46,ytop
    o=[f'<path d="M {xa},{yline} L {xi},{yi} Q {xa},{ytop-26} {xo},{yo} Z" fill="url(#tan)" stroke="#9a7d3e" stroke-width="2"/>']
    o.append(hole(xa,yline)); o.append(hole(xi,yi)); o.append(hole(xo,yo))
    o+=ground(xa,yline)
    o.append(f'<text x="{xa}" y="{yline+44}" fill="#9ad8b0" font-size="11" text-anchor="middle">{lab}ta (axle)</text>')
    o.append(f'<text x="{xa}" y="{yline+58}" fill="#7d7762" font-size="9" text-anchor="middle">→ disc, y=0</text>')
    o.append(f'<text x="{xi}" y="{yi-12}" fill="#c0a0ff" font-size="10" text-anchor="middle">{lab}ti</text>')
    o.append(f'<text x="{xo}" y="{yo-12}" fill="#e0b86e" font-size="10" text-anchor="middle">{lab}to</text>')
    return o, (xi,yi),(xo,yo)
def binary(p,q):
    ang=np.degrees(np.arctan2(q[1]-p[1],q[0]-p[0])); L=np.hypot(q[0]-p[0],q[1]-p[1])
    return f'<rect x="{p[0]}" y="{p[1]-5}" width="{L:.1f}" height="10" rx="5" fill="url(#bar)" stroke="#6a6f78" stroke-width="0.6" transform="rotate({ang:.1f} {p[0]} {p[1]})"/>'

# bell crank (L) at left
bx=140
out.append(f'<path d="M {bx},{yline} L {bx-30},{yline-2} Q {bx-40},{yline+40} {bx-20},{yline+70} L {bx+4},{yline+66} Q {bx+30},{ytop+30} {bx+40},{ytop} Z" fill="url(#tan)" stroke="#9a7d3e" stroke-width="2"/>')
out.append(hole(bx,yline)); out+=ground(bx,yline)
out.append(hole(bx-22,yline+62)); out.append(hole(bx+40,ytop))
out.append(f'<text x="{bx}" y="{yline+44}" fill="#9ad8b0" font-size="10" text-anchor="middle">cBCa (pivot)</text>')
out.append(f'<text x="{bx-22}" y="{yline+82}" fill="#7fb0ff" font-size="10" text-anchor="middle">cBCi</text>')
out.append(f'<text x="{bx+44}" y="{ytop-10}" fill="#e0b86e" font-size="10">cBCo</text>')
out.append('<text x="90" y="100" fill="#e0b86e" font-size="12">L bell-crank</text>')
# control rod down from cBCi
out.append(f'<line x1="{bx-22}" y1="{yline+62}" x2="{bx-22}" y2="{H-20}" stroke="#7fb0ff" stroke-width="4"/>')
out.append(f'<text x="{bx-16}" y="{H-30}" fill="#7fb0ff" font-size="11">control rod ↓ to pillar / pedal</text>')

# three disc levers C1n, C2n, C3n
prevout=(bx+40,ytop)
labels=[('c1n',360),('c2n',560),('c3n',760)]
for lab,xa in labels:
    o,pi,po=lever(xa,lab)
    out.append(binary(prevout,pi))     # link from previous output to this input
    out+=o
    prevout=po
# return spring at last output
sx=prevout[0]
pts=" ".join("%d,%d"%(sx+i*8,(ytop-7 if i%2 else ytop+7)) for i in range(7))
out.append(f'<polyline points="{sx},{ytop} {pts} {sx+58},{ytop}" fill="none" stroke="#9ad8b0" stroke-width="2"/>')
out.append(f'<line x1="{sx+58}" y1="{ytop-12}" x2="{sx+58}" y2="{ytop+12}" stroke="#8a8f98" stroke-width="3"/>')
out.append(f'<text x="{sx+30}" y="{ytop-18}" fill="#9ad8b0" font-size="10" text-anchor="middle">return spring</text>')
# legend
out.append('<text x="490" y="500" fill="#8a8f98" font-size="11" text-anchor="middle">axle hole = grounded pivot (pinned in the bar, carries the disc) · input/output holes take the binary links</text>')
out.append('<text x="490" y="520" fill="#8a8f98" font-size="11" text-anchor="middle">equal …ta→…ti and …ta→…to arms + equal bars → every disc rotates the same ~60° (parallelogram relay)</text>')
out.append('</svg>')
open('relay_labeled_v1.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('relay_labeled_v1.svg')
import cairosvg; cairosvg.svg2png(url='relay_labeled_v1.svg',write_to='/tmp/chk.png',output_width=980)
print('built')
