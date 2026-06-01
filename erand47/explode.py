import numpy as np
W,H=980,470
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a8f97"/><stop offset="1" stop-color="#4c5158"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#6a6f78"/></linearGradient>
<radialGradient id="pin" cx=".4" cy=".4" r=".7"><stop offset="0" stop-color="#e2e6ec"/><stop offset="1" stop-color="#6a6f78"/></radialGradient></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="490" y="32" fill="#eef0f4" font-size="16" text-anchor="middle">one disc, exploded along the axle — what touches what</text>')
cz=230
# the axle runs left→right through everything
out.append(f'<line x1="150" y1="{cz}" x2="820" y2="{cz}" stroke="#cfd4da" stroke-width="6" stroke-linecap="round"/>')
out.append(f'<text x="485" y="{cz-92}" fill="#cfd4da" font-size="12" text-anchor="middle">AXLE (one rigid shaft) — carries the turning force</text>')
out.append(f'<line x1="485" y1="{cz-86}" x2="485" y2="{cz-8}" stroke="#cfd4da" stroke-width="0.8" stroke-dasharray="3 3"/>')

# 1) string (front, far left)
out.append(f'<line x1="120" y1="{cz-70}" x2="120" y2="{cz+70}" stroke="#b8924a" stroke-width="6" stroke-linecap="round"/>')
out.append(f'<text x="120" y="{cz+92}" fill="#b8924a" font-size="11" text-anchor="middle">string</text>')

# 2) disc plate + prongs (fixed to axle) at x=230
dx=230
out.append(f'<rect x="{dx-9}" y="{cz-58}" width="18" height="116" rx="9" fill="url(#steel)" stroke="#eef0f4" stroke-width="1"/>')   # disc edge-on
out.append(f'<circle cx="{dx}" cy="{cz}" r="6" fill="#23262b"/>')                                                                    # axle through disc (fixed)
# prongs from disc tips toward the string (front)
for sgn in (1,-1):
    out.append(f'<rect x="{120}" y="{cz+sgn*30-5}" width="{dx-120}" height="10" rx="5" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.6"/>')
out.append(f'<text x="{dx}" y="{cz-70}" fill="#cdd2da" font-size="11" text-anchor="middle">disc plate</text>')
out.append(f'<text x="{(120+dx)/2:.0f}" y="{cz+sgn*0-78}" fill="#9aa0a8" font-size="10" text-anchor="middle">prongs</text>')
out.append(f'<text x="{dx}" y="{cz+92}" fill="#9ad8b0" font-size="10" text-anchor="middle">fixed to axle</text>')
# contact note: prong↔string
out.append(f'<text x="{(120+dx)/2:.0f}" y="{cz+108}" fill="#b8924a" font-size="10" text-anchor="middle">prongs grip string (engaged)</text>')
# disc edge free note
out.append(f'<text x="{dx+2}" y="{cz-58-6}" fill="#ff8c5a" font-size="9" text-anchor="middle">edge: free — nothing touches</text>')

# 3) bar (the journal/bearing) at x=430
bxp=430
out.append(f'<rect x="{bxp-22}" y="{cz-95}" width="44" height="190" fill="url(#bar)" stroke="#2d3036"/>')
out.append(f'<circle cx="{bxp}" cy="{cz}" r="9" fill="#13110d" stroke="#9aa0a8" stroke-width="1"/>')   # hole
out.append(f'<text x="{bxp}" y="{cz-104}" fill="#aeb3bd" font-size="11" text-anchor="middle">bar ¼″</text>')
out.append(f'<text x="{bxp}" y="{cz+112}" fill="#9ad8b0" font-size="10" text-anchor="middle">axle turns in this hole = the ONLY bearing</text>')

# 4) crank arm (fixed to axle, back side) at x=600
cxp=600
out.append(f'<line x1="{cxp}" y1="{cz}" x2="{cxp}" y2="{cz-46}" stroke="#2a2d31" stroke-width="6"/>')
out.append(f'<circle cx="{cxp}" cy="{cz}" r="6" fill="#23262b"/>')                                   # axle through crank (fixed)
out.append(f'<circle cx="{cxp}" cy="{cz-46}" r="4.5" fill="#e0b86e"/>')                              # crank pin
out.append(f'<text x="{cxp}" y="{cz+92}" fill="#9ad8b0" font-size="10" text-anchor="middle">crank — fixed to axle</text>')
out.append(f'<text x="{cxp+30}" y="{cz-46}" fill="#e0b86e" font-size="10">crank pin</text>')

# 5) link + action rod (push the crank pin) at x=720
out.append(f'<line x1="{cxp}" y1="{cz-46}" x2="{720}" y2="{cz-58}" stroke="#cfd4da" stroke-width="3"/>')   # link
out.append(f'<text x="{(cxp+720)/2:.0f}" y="{cz-64}" fill="#cfd4da" font-size="10" text-anchor="middle">link</text>')
out.append(f'<rect x="{720}" y="{cz-90}" width="120" height="9" rx="4" fill="url(#steel)" stroke="#9aa0a8" stroke-width="0.6" transform="rotate(8 720 {cz-58})"/>')
out.append(f'<circle cx="720" cy="{cz-58}" r="4" fill="#9aa0a8"/>')
out.append(f'<text x="790" y="{cz-86}" fill="#9aa0a8" font-size="10" text-anchor="middle">action rod (slides)</text>')
out.append(f'<text x="780" y="{cz+92}" fill="#cdd2da" font-size="10" text-anchor="middle">link pushes the crank pin</text>')

# force path footer
out.append('<text x="490" y="440" fill="#8a8f98" font-size="12" text-anchor="middle">force path:  rod → link → crank pin → crank → AXLE → disc → prongs → string   (nothing drives the disc by its edge)</text>')
out.append('</svg>')
open('one_disc_exploded_v1.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('one_disc_exploded_v1.svg')
import cairosvg; cairosvg.svg2png(url='one_disc_exploded_v1.svg',write_to='/tmp/chk.png',output_width=980)
print('built')
