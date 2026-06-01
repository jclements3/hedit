# rebuild from v5 source, replace the side panel with an axle/crank/rod mechanism + add rotate arrows
import numpy as np
src=open('assembly.py').read()
# --- swap output name & title ---
src=src.replace('disc_assembly_v5.svg','disc_assembly_v6.svg')
src=src.replace('capsule disc conforms to round pin prongs · engage = rotate','disc pivots on an axle — crank + action rod rotate it to engage')
# --- add a curved rotate arrow on the engaged panel (after its disc) ---
src=src.replace("out.append(disc(0,0,rot,X2,Z2,fill=\"url(#steel)\",stroke=\"#eef0f4\",stroke_width=\"1\"))",
"out.append(disc(0,0,rot,X2,Z2,fill=\"url(#steel)\",stroke=\"#eef0f4\",stroke_width=\"1\"))\n"
"out.append(f'<path d=\"M {X2(0)+44},{Z2(0)-30} A 52 52 0 0 1 {X2(0)+30},{Z2(0)-46}\" fill=\"none\" stroke=\"#e0b86e\" stroke-width=\"1.4\" marker-end=\"url(#arr)\"/>')")
# --- arrowhead marker in defs ---
src=src.replace('</defs>',
'<marker id="arr" markerWidth="7" markerHeight="7" refX="3" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#e0b86e"/></marker></defs>')
# --- replace the entire side panel block ---
import re
start=src.index('# panel3 side')
end=src.index("out.append('</svg>')")
mech='''# panel3 side (axle + crank + rod)
SCs=9.0; sy0=270; Y=lambda y:632+(y+9)*SCs; ZZ=lambda z:sy0-z*SCs
out.append('<text x="800" y="64" fill="#cdd2da" font-size="13" text-anchor="middle">side — axle / crank / rod (13 gap)</text>')
# plates
out.append(f'<rect x="{Y(-6.35):.1f}" y="{ZZ(6):.1f}" width="{6.35*SCs:.1f}" height="{12*SCs:.1f}" fill="url(#plate)" stroke="#33363b"/>')
out.append(f'<rect x="{Y(13):.1f}" y="{ZZ(6):.1f}" width="{6.35*SCs:.1f}" height="{12*SCs:.1f}" fill="url(#plate)" stroke="#33363b"/>')
out.append(f'<text x="{Y(-3.2):.1f}" y="{ZZ(-6)+15:.1f}" fill="#aeb3bd" font-size="9" text-anchor="middle">neck plate</text>')
out.append(f'<text x="{Y(16.2):.1f}" y="{ZZ(-6)+15:.1f}" fill="#aeb3bd" font-size="9" text-anchor="middle">eyelet plate</text>')
# string at mid-depth
out.append(f'<line x1="{Y(6.5):.1f}" y1="{ZZ(6):.1f}" x2="{Y(6.5):.1f}" y2="{ZZ(-6):.1f}" stroke="#b8924a" stroke-width="2.6" stroke-linecap="round"/>')
# disc edge-on on the string-side face of the neck plate
out.append(f'<rect x="{Y(0):.1f}" y="{ZZ(2.0):.1f}" width="{3*SCs:.1f}" height="{4*SCs:.1f}" rx="6" fill="url(#steel)" stroke="#eef0f4" stroke-width="1"/>')
# prongs project to mid-depth
for pz in (1.9,-1.9):
    out.append(f'<rect x="{Y(3):.1f}" y="{ZZ(pz+rp):.1f}" width="{7*SCs:.1f}" height="{2*rp*SCs:.1f}" rx="{rp*SCs:.1f}" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>')
# axle: through the neck plate (along depth), journaled
out.append(f'<line x1="{Y(1.5):.1f}" y1="{ZZ(0):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(0):.1f}" stroke="#cfd4da" stroke-width="3"/>')
out.append(f'<circle cx="{Y(1.5):.1f}" cy="{ZZ(0):.1f}" r="2.4" fill="#2a2d31" stroke="#cfd4da" stroke-width="1"/>')
out.append(f'<text x="{Y(-2.0):.1f}" y="{ZZ(0)-6:.1f}" fill="#9aa0a8" font-size="9" text-anchor="middle">axle</text>')
out.append(f'<text x="{Y(-3.2):.1f}" y="{ZZ(3.0):.1f}" fill="#9aa0a8" font-size="8" text-anchor="middle">journal</text>')
# crank arm on the back end of the axle
out.append(f'<line x1="{Y(-9):.1f}" y1="{ZZ(0):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(2.6):.1f}" stroke="#cfd4da" stroke-width="2.6"/>')
out.append(f'<circle cx="{Y(-9):.1f}" cy="{ZZ(2.6):.1f}" r="2.0" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>')
out.append(f'<text x="{Y(-9)-4:.1f}" y="{ZZ(1.3):.1f}" fill="#9aa0a8" font-size="9" text-anchor="end">crank</text>')
# action rod (vertical, behind neck) + pull arrow
out.append(f'<line x1="{Y(-9):.1f}" y1="{ZZ(2.6):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(-6):.1f}" stroke="#8aa0c0" stroke-width="2.6"/>')
out.append(f'<line x1="{Y(-9):.1f}" y1="{ZZ(-3.5):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(-5.6):.1f}" stroke="#8aa0c0" stroke-width="1.4" marker-end="url(#arr)"/>')
out.append(f'<text x="{Y(-9)+4:.1f}" y="{ZZ(-4.6):.1f}" fill="#8aa0c0" font-size="9">rod ↓ from pedal</text>')
out.append(f'<text x="{Y(6.5):.1f}" y="{ZZ(-6)+15:.1f}" fill="#8a8f98" font-size="9" text-anchor="middle">disc rotates on axle → prongs sweep in</text>')
'''
src=src[:start]+mech+src[end:]
src=src.replace('round Ø2.4 pins · disc = capsule (round tips r=1.2 conform to pins) · c-c 4.9 ≪ neighbour 14',
'disc on string-side face · axle journaled thru neck plate · crank+rod (in 13 gap) driven from pillar pedal')
open('assembly.py','w').write(src)
exec(open('assembly.py').read())
print('built v6')
