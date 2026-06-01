import numpy as np
W,H=980,640
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b5a3e"/><stop offset="1" stop-color="#3a3026"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#6a6f78"/></linearGradient>
<marker id="rot" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L7,4 L0,8 Z" fill="#e0b86e"/></marker></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="490" y="30" fill="#eef0f4" font-size="16" text-anchor="middle">erand47 pedal mechanism — top (fan) · side (section + bell-crank)</text>')

# ===== TOP VIEW =====
cx,cy=250,150
out.append('<text x="250" y="60" fill="#cdd2da" font-size="13" text-anchor="middle">TOP — 7 pedals fan from centre, cross to opposite rods</text>')
# baseplate fan
out.append(f'<path d="M {cx-205},{cy+250} Q {cx},{cy-40} {cx+205},{cy+250} Z" fill="url(#wood)" stroke="#2d241a" stroke-width="1.5" opacity="0.85"/>')
out.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#23262b" stroke="#9aa0a8" stroke-width="2"/>')
peds=['D','C','B','E','F','G','A']
R=180; tail=46
for k,p in enumerate(peds):
    ang=np.radians(-58 + k*116/6)              # from straight-down
    dx,dy=np.sin(ang),np.cos(ang)
    fx,fy=cx+R*dx, cy+R*dy                      # foot plate
    tx,ty=cx-tail*dx, cy-tail*dy                # crossed tail (opposite side)
    col='#9ec3ff' if p in 'DCB' else '#ffc488'
    out.append(f'<line x1="{tx:.0f}" y1="{ty:.0f}" x2="{fx:.0f}" y2="{fy:.0f}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>')
    out.append(f'<ellipse cx="{fx:.0f}" cy="{fy:.0f}" rx="13" ry="7" transform="rotate({np.degrees(ang):.0f} {fx:.0f} {fy:.0f})" fill="url(#steel)" stroke="#eef0f4" stroke-width="0.6"/>')
    out.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="3.2" fill="#7fb0ff"/>')   # rod take-off (crossed)
    out.append(f'<text x="{cx+(R+18)*dx:.0f}" y="{cy+(R+18)*dy+4:.0f}" fill="{col}" font-size="12" text-anchor="middle">{p}</text>')
out.append(f'<text x="{cx}" y="{cy-26:.0f}" fill="#7fb0ff" font-size="10" text-anchor="middle">rods ↑ column</text>')
out.append(f'<text x="{cx-150}" y="{cy+250}" fill="#9ec3ff" font-size="11">left foot D C B</text>')
out.append(f'<text x="{cx+150}" y="{cy+250}" fill="#ffc488" font-size="11" text-anchor="end">right foot E F G A</text>')

# ===== SIDE VIEW =====
ox=620
out.append('<text x="800" y="60" fill="#cdd2da" font-size="13" text-anchor="middle">SIDE — pedal → notch → rod ↑ column → bell-crank → disc</text>')
# plinth box
out.append(f'<rect x="{ox+40}" y="540" width="300" height="60" fill="url(#wood)" stroke="#2d241a"/>')
# pedal lever + pivot + 3-notch rack
out.append(f'<circle cx="{ox+120}" cy="558" r="4" fill="#2a2d31" stroke="#cfd4da"/>')   # pivot M
out.append(f'<line x1="{ox-10}" y1="566" x2="{ox+170}" y2="552" stroke="url(#steel)" stroke-width="7" stroke-linecap="round"/>')  # pedal
out.append(f'<text x="{ox-12}" y="560" fill="#cdd2da" font-size="11" text-anchor="end">pedal</text>')
# notch rack (flat/natural/sharp)
for j,(lab,c) in enumerate([('♭','#8a8f98'),('♮','#9ad8b0'),('♯','#ff8c5a')]):
    ny=548+j*16
    out.append(f'<line x1="{ox+150}" y1="{ny}" x2="{ox+166}" y2="{ny}" stroke="{c}" stroke-width="2"/>')
    out.append(f'<text x="{ox+172}" y="{ny+4}" fill="{c}" font-size="10">{lab}</text>')
# vertical rod up the column (with break)
rx=ox+150
out.append(f'<line x1="{rx}" y1="548" x2="{rx}" y2="360" stroke="#7fb0ff" stroke-width="3"/>')
out.append(f'<line x1="{rx-6}" y1="360" x2="{rx+6}" y2="350" stroke="#13110d" stroke-width="6"/>')   # break
out.append(f'<line x1="{rx}" y1="340" x2="{rx}" y2="150" stroke="#7fb0ff" stroke-width="3"/>')
out.append(f'<text x="{rx+8}" y="260" fill="#7fb0ff" font-size="11">control rod ↑ pillar</text>')
# column walls
out.append(f'<line x1="{rx-20}" y1="540" x2="{rx-20}" y2="150" stroke="#54585f" stroke-width="2"/>')
out.append(f'<line x1="{rx+24}" y1="430" x2="{rx+24}" y2="150" stroke="#54585f" stroke-width="2"/>')
# bell-crank at top (L lever, pivot P)
px,py=rx,140
out.append(f'<circle cx="{px}" cy="{py}" r="6" fill="#2a2d31" stroke="#e0b86e" stroke-width="2"/>')
out.append(f'<line x1="{px}" y1="{py}" x2="{rx}" y2="150" stroke="#e0b86e" stroke-width="4"/>')      # input arm (down, to rod)
out.append(f'<line x1="{px}" y1="{py}" x2="{px-70}" y2="{py-6}" stroke="#e0b86e" stroke-width="4"/>')# output arm (to neck)
out.append(f'<path d="M {px+12},{py-12} A 17 17 0 0 1 {px+15},{py+8}" fill="none" stroke="#e0b86e" stroke-width="1.5" marker-end="url(#rot)"/>')
out.append(f'<text x="{px+18}" y="{py-14}" fill="#e0b86e" font-size="12">bell-crank</text>')
# neck rod -> disc
out.append(f'<line x1="{px-70}" y1="{py-6}" x2="{px-150}" y2="{py-6}" stroke="#9ad8b0" stroke-width="2" stroke-dasharray="5 4"/>')
dx0=px-170
out.append(f'<rect x="{dx0-14}" y="{py-12}" width="28" height="12" rx="6" fill="url(#steel)" stroke="#eef0f4" stroke-width="0.7"/>')
out.append(f'<circle cx="{dx0}" cy="{py-6}" r="3" fill="#2a2d31"/>')
out.append(f'<path d="M {dx0+10},{py-16} A 13 13 0 0 1 {dx0+13},{py+2}" fill="none" stroke="#c0a0ff" stroke-width="1.4" marker-end="url(#rot)"/>')
out.append(f'<text x="{dx0}" y="{py-18}" fill="#c0a0ff" font-size="11" text-anchor="middle">disc turns</text>')
out.append(f'<text x="{px-40}" y="{py+18}" fill="#9ad8b0" font-size="10" text-anchor="middle">neck rod</text>')
out.append('<text x="490" y="624" fill="#8a8f98" font-size="11" text-anchor="middle">single cross-over at the pedal tips (Fig 1) · double-action adds the ♯ second notch driving the −y/+y sharp discs</text>')
out.append('</svg>')
open('pedal_mech_v2.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('pedal_mech_v2.svg')
import cairosvg; cairosvg.svg2png(url='pedal_mech_v2.svg',write_to='/tmp/chk.png',output_width=980)
print('built')
