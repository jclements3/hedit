import numpy as np
W,H=980,520
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a8f97"/><stop offset="1" stop-color="#4c5158"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#6a6f78"/></linearGradient>
<marker id="rot" markerWidth="9" markerHeight="9" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#e0b86e"/></marker></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="490" y="30" fill="#eef0f4" font-size="16" text-anchor="middle">one disc — what connects to it, and where</text>')

# ---------- Panel A: depth section (y across) ----------
S=11; cz=270
Y=lambda y:150+y*S          # +y to the right (string at y=0 on left)
out.append('<text x="250" y="62" fill="#cdd2da" font-size="13" text-anchor="middle">depth section — disc on string side, crank on back, axle through bar</text>')
# string at y=0
out.append(f'<line x1="{Y(0):.0f}" y1="{cz-70}" x2="{Y(0):.0f}" y2="{cz+70}" stroke="#b8924a" stroke-width="5" stroke-linecap="round"/>')
out.append(f'<text x="{Y(0):.0f}" y="{cz+90}" fill="#b8924a" font-size="10" text-anchor="middle">string y=0</text>')
# disc on inner face (capsule edge-on) at y=6.5, thickness 2 inward
out.append(f'<rect x="{Y(4.5):.0f}" y="{cz-26}" width="{2*S:.0f}" height="52" rx="4" fill="url(#steel)" stroke="#eef0f4" stroke-width="1"/>')
out.append(f'<text x="{Y(5.5):.0f}" y="{cz-34}" fill="#cdd2da" font-size="10" text-anchor="middle">disc</text>')
# prongs reach from disc to string
for sgn in (1,-1):
    out.append(f'<rect x="{Y(0):.0f}" y="{cz+sgn*14-4:.0f}" width="{4.5*S:.0f}" height="8" rx="4" fill="url(#steel)" stroke="#eef0f4" stroke-width="0.6"/>')
out.append(f'<text x="{Y(2.2):.0f}" y="{cz-2}" fill="#9aa0a8" font-size="9" text-anchor="middle">prongs</text>')
# the bar (wall), inner face at y=6.5, 6.35 thick
out.append(f'<rect x="{Y(6.5):.0f}" y="{cz-95}" width="{6.35*S:.0f}" height="190" fill="url(#bar)" stroke="#2d3036"/>')
out.append(f'<text x="{Y(9.7):.0f}" y="{cz-104}" fill="#aeb3bd" font-size="10" text-anchor="middle">bar ¼″ (journal)</text>')
# axle through bar
out.append(f'<line x1="{Y(5.5):.0f}" y1="{cz}" x2="{Y(17):.0f}" y2="{cz}" stroke="#cfd4da" stroke-width="6" stroke-linecap="round"/>')
out.append(f'<text x="{Y(8):.0f}" y="{cz+16}" fill="#cfd4da" font-size="10" text-anchor="middle">axle</text>')
# back side: crank + link + action rod (end-on) + spring
out.append(f'<line x1="{Y(15):.0f}" y1="{cz}" x2="{Y(15):.0f}" y2="{cz-34}" stroke="#2a2d31" stroke-width="5"/>')   # crank (edge-on)
out.append(f'<circle cx="{Y(15):.0f}" cy="{cz-34}" r="3.5" fill="#e0b86e"/>')                                      # crank pin
out.append(f'<line x1="{Y(15):.0f}" y1="{cz-34}" x2="{Y(20):.0f}" y2="{cz-44}" stroke="#cfd4da" stroke-width="3"/>')# link
out.append(f'<circle cx="{Y(20):.0f}" cy="{cz-44}" r="6" fill="url(#steel)" stroke="#9aa0a8"/>')                   # rod (end-on)
out.append(f'<text x="{Y(20):.0f}" y="{cz-54}" fill="#9aa0a8" font-size="9" text-anchor="middle">action rod</text>')
out.append(f'<text x="{Y(16):.0f}" y="{cz+34}" fill="#cdd2da" font-size="10" text-anchor="middle">crank + link (back side)</text>')
out.append(f'<text x="{Y(8):.0f}" y="{cz+118}" fill="#8a8f98" font-size="10" text-anchor="middle">string side ← | bar | → back (mechanism)</text>')

# ---------- Panel B: back-face view (how it rotates) ----------
bx,bz=720,270; rc=46; al=np.radians(-118)
out.append('<text x="720" y="62" fill="#cdd2da" font-size="13" text-anchor="middle">back-face view — rod slides → crank → axle → disc turns</text>')
# disc (face, behind) + axle
out.append(f'<circle cx="{bx}" cy="{bz}" r="40" fill="#23262b" stroke="#54585f" stroke-width="1" stroke-dasharray="3 3"/>')
out.append(f'<text x="{bx}" y="{bz+58}" fill="#54585f" font-size="9" text-anchor="middle">disc (behind bar)</text>')
out.append(f'<circle cx="{bx}" cy="{bz}" r="5" fill="#cfd4da"/>')
out.append(f'<text x="{bx+10}" y="{bz+4}" fill="#cfd4da" font-size="10">axle</text>')
# flat crank
px,pz=bx+rc*np.cos(al), bz+rc*np.sin(al)
out.append(f'<line x1="{bx}" y1="{bz}" x2="{px:.0f}" y2="{pz:.0f}" stroke="#2a2d31" stroke-width="5"/>')
out.append(f'<circle cx="{px:.0f}" cy="{pz:.0f}" r="4" fill="#e0b86e"/>')
out.append(f'<text x="{px-6:.0f}" y="{pz-6:.0f}" fill="#2a2d31" font-size="10" text-anchor="end" stroke="#cdd2da" stroke-width="0.2">crank</text>')
# action rod (horizontal) + link
rodz=pz-30
out.append(f'<rect x="{bx-150}" y="{rodz-4:.0f}" width="320" height="8" rx="3" fill="url(#steel)" stroke="#9aa0a8" stroke-width="0.6"/>')
out.append(f'<text x="{bx-150}" y="{rodz-10:.0f}" fill="#9aa0a8" font-size="10">action rod (slides →)</text>')
out.append(f'<line x1="{px:.0f}" y1="{rodz:.0f}" x2="{px:.0f}" y2="{pz:.0f}" stroke="#cfd4da" stroke-width="3"/>')
out.append(f'<circle cx="{px:.0f}" cy="{rodz:.0f}" r="3" fill="#9aa0a8"/>')
out.append(f'<text x="{px+8:.0f}" y="{(rodz+pz)/2:.0f}" fill="#cfd4da" font-size="9">link</text>')
# engaged ghost crank
al2=al+np.radians(58)
px2,pz2=bx+rc*np.cos(al2),bz+rc*np.sin(al2)
out.append(f'<line x1="{bx}" y1="{bz}" x2="{px2:.0f}" y2="{pz2:.0f}" stroke="#e0b86e" stroke-width="3" stroke-dasharray="4 3" opacity="0.8"/>')
out.append(f'<path d="M {bx+18},{bz-42} A 46 46 0 0 1 {px2:.0f},{pz2:.0f}" fill="none" stroke="#e0b86e" stroke-width="1.4" marker-end="url(#rot)"/>')
out.append(f'<text x="{bx+70}" y="{bz-20}" fill="#e0b86e" font-size="10">~60°</text>')
out.append('<text x="490" y="500" fill="#8a8f98" font-size="11" text-anchor="middle">disc + axle + crank are one rigid unit; only the link and rod move it · a return spring (not shown) unwinds it on release</text>')
out.append('</svg>')
open('one_disc_v1.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('one_disc_v1.svg')
import cairosvg; cairosvg.svg2png(url='one_disc_v1.svg',write_to='/tmp/chk.png',output_width=980)
print('built')
