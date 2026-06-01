# erand47 actuation parts library — SVG part generators.
# GOLD parts = standard rigid links (fixed shape; scale toward treble).
# GREY parts = connectors whose length + curvature come from the N/S Bezier.
import math

SC = 7.0                      # px per mm (drawing scale)
CRANK_R   = 8.0               # axle -> input/output pin (mm)
LEVER_HALF= 30.0              # half the T opening (deg)
AXLE_D    = 3.0               # spindle/axle hole Ø (mm)
PIN_D     = 1.6               # link-pin hole Ø (mm)
LOBE_PAD  = 2.1               # body lobe radius = hole_r + pad (mm)
LINK_W    = 2.6               # grey connector bar width (mm)

GOLD='#e7c97e'; GOLD_E='#b8973f'; GREY='#c3c7cd'; GREY_E='#7d828a'; HOLE='#f3efe6'

def _T(p, cx, cy, s, rot):
    x,y=p[0]*SC*s, p[1]*SC*s; a=math.radians(rot)
    return (cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a))

def _hole(P, d, s):
    r=d/2*SC*s
    return f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="{r:.1f}" fill="{HOLE}" stroke="{GOLD_E}" stroke-width="1"/>'

def _body(centers, s, fill, edge):
    out=[]
    # filled triangle/poly through hole centres + a lobe at each -> rounded link body
    pts=" ".join(f"{c[0]:.1f},{c[1]:.1f}" for c in centers)
    out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{edge}" stroke-width="2" stroke-linejoin="round"/>')
    for c in centers:
        out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{(PIN_D/2+LOBE_PAD)*SC*s:.1f}" fill="{fill}" stroke="{edge}" stroke-width="2"/>')
    return out

def disc_lever(cx,cy,s=1.0,rot=0,label=None,prefix=''):
    A=(0,0)
    I=(CRANK_R*math.sin(math.radians(LEVER_HALF)),  CRANK_R*math.cos(math.radians(LEVER_HALF)))
    O=(-CRANK_R*math.sin(math.radians(LEVER_HALF)), CRANK_R*math.cos(math.radians(LEVER_HALF)))
    a,i,o=[_T(p,cx,cy,s,rot) for p in (A,I,O)]
    g=_body([a,i,o],s,GOLD,GOLD_E)
    g.append(_hole(a,AXLE_D,s)); g.append(_hole(i,PIN_D,s)); g.append(_hole(o,PIN_D,s))   # axle hole = big spindle
    if label:
        g.append(f'<text x="{a[0]:.0f}" y="{a[1]+ (AXLE_D/2+LOBE_PAD)*SC*s+12:.0f}" fill="#9aa0a8" font-size="9" text-anchor="middle">{label}</text>')
        g.append(f'<text x="{a[0]+5:.0f}" y="{a[1]-2:.0f}" fill="#c0a0ff" font-size="8">{prefix}ta</text>')
        g.append(f'<text x="{i[0]+4:.0f}" y="{i[1]:.0f}" fill="#cfd4da" font-size="8">{prefix}ti</text>')
        g.append(f'<text x="{o[0]-4:.0f}" y="{o[1]:.0f}" fill="#cfd4da" font-size="8" text-anchor="end">{prefix}to</text>')
    return "".join(g)

def relay_lever(cx,cy,s=1.0,rot=0,label=None):
    A=(0,0); I=(CRANK_R*0.9,CRANK_R*0.5); O=(-CRANK_R*0.9,CRANK_R*0.5)
    a,i,o=[_T(p,cx,cy,s,rot) for p in (A,I,O)]
    g=_body([a,i,o],s,GOLD,GOLD_E)
    for P in (a,i,o): g.append(_hole(P,PIN_D,s))   # all pin holes (no disc)
    if label: g.append(f'<text x="{a[0]:.0f}" y="{a[1]+22:.0f}" fill="#9aa0a8" font-size="9" text-anchor="middle">{label}</text>')
    return "".join(g)

def bell_crank(cx,cy,s=1.0,rot=0,label=None,prefix=''):
    P=(0,0); IN=(-2,-11); OUT=(11,2)                # bent ~100deg (pivot, in arm, out arm)
    p,inn,out=[_T(q,cx,cy,s,rot) for q in (P,IN,OUT)]
    g=_body([p,inn,out],s,GOLD,GOLD_E)
    g.append(_hole(p,AXLE_D,s)); g.append(_hole(inn,PIN_D,s)); g.append(_hole(out,PIN_D,s))
    if label:
        g.append(f'<text x="{p[0]:.0f}" y="{p[1]-(AXLE_D/2+LOBE_PAD)*SC*s-6:.0f}" fill="#9aa0a8" font-size="9" text-anchor="middle">{label}</text>')
        g.append(f'<text x="{p[0]+5:.0f}" y="{p[1]:.0f}" fill="#9ad8b0" font-size="8">{prefix}BCa</text>')
        g.append(f'<text x="{inn[0]:.0f}" y="{inn[1]-3:.0f}" fill="#7fb0ff" font-size="8" text-anchor="middle">{prefix}BCi</text>')
        g.append(f'<text x="{out[0]+4:.0f}" y="{out[1]:.0f}" fill="#cfd4da" font-size="8">{prefix}BCo</text>')
    return "".join(g)

def grey_link(p0,p1,bow=0.0,label=None):
    # variable connector: capsule following a quadratic with mid bow (= local N/S curvature)
    mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; ln=math.hypot(dx,dy) or 1
    nx,ny=-dy/ln,dx/ln; cxp,cyp=mx+nx*bow,my+ny*bow
    g=[f'<path d="M {p0[0]:.1f},{p0[1]:.1f} Q {cxp:.1f},{cyp:.1f} {p1[0]:.1f},{p1[1]:.1f}" fill="none" stroke="{GREY_E}" stroke-width="{LINK_W*SC+3:.1f}" stroke-linecap="round"/>',
       f'<path d="M {p0[0]:.1f},{p0[1]:.1f} Q {cxp:.1f},{cyp:.1f} {p1[0]:.1f},{p1[1]:.1f}" fill="none" stroke="{GREY}" stroke-width="{LINK_W*SC:.1f}" stroke-linecap="round"/>']
    for P in (p0,p1): g.append(f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="{PIN_D/2*SC:.1f}" fill="{HOLE}" stroke="{GREY_E}" stroke-width="1"/>')
    if label: g.append(f'<text x="{cxp:.0f}" y="{cyp - (8 if bow>=0 else -16):.0f}" fill="#9aa0a8" font-size="9" text-anchor="middle">{label}</text>')
    return "".join(g)

if __name__=='__main__':
    W,Hh=940,640
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}" font-family="Georgia,serif">',
       f'<rect width="{W}" height="{Hh}" fill="#13110d"/>',
       f'<text x="{W/2}" y="34" fill="#eef0f4" font-size="16" text-anchor="middle">erand47 actuation parts</text>',
       '<text x="60" y="70" fill="#e7c97e" font-size="13">GOLD — standard rigid links (fixed shape; smaller toward treble)</text>']
    o.append(disc_lever(170,180,1.0,0,'disc lever (bass)','c?n'))
    o.append(disc_lever(340,180,0.72,0,'disc lever (treble)','c?n'))
    o.append(relay_lever(500,175,1.0,0,'relay lever'))
    o.append(bell_crank(700,185,1.0,0,'L bell-crank','c'))
    o.append('<text x="60" y="360" fill="#c3c7cd" font-size="13">GREY — connectors (length + curvature from the N/S Bézier)</text>')
    o.append(grey_link((120,430),(300,430),0,'short / straight'))
    o.append(grey_link((360,440),(600,410),28,'medium / slight bow'))
    o.append(grey_link((660,460),(900,400),60,'long / more bow'))
    o.append('<text x="60" y="560" fill="#8a8f98" font-size="11">disc lever: big axle hole = disc spindle (Ø3), two pin holes (Ø1.6), arm 8 mm @ ±30°.</text>')
    o.append('<text x="60" y="582" fill="#8a8f98" font-size="11">bell-crank: bent ternary at the pillar top. relay lever: 3 pin holes, no disc.</text>')
    o.append('<text x="60" y="604" fill="#8a8f98" font-size="11">grey links are the only parts that change per string — everything gold is standard, just scaled.</text>')
    o.append('</svg>')
    open('parts.svg','w').write("\n".join(o))
    import xml.dom.minidom as m; m.parse('parts.svg')
    import cairosvg; cairosvg.svg2png(url='parts.svg',write_to='/tmp/chk.png',output_width=940)
    print('parts.svg built')
