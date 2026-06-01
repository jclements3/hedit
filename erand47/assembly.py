import numpy as np
SC=20.0; rp=1.2; rs=0.635
pc=2.45; bmid=rp*1.30            # prong-centre radius; body half-width (bulge)
def disc_outline(cx,cz,rot,m=60):
    # tip = circular arc radius rp at (+-pc,0) -> conforms to round prong; sides bulge to bmid
    pts=[]
    th=np.linspace(-np.pi/2,np.pi/2,m)                       # right cap
    pts+=[(pc+rp*np.cos(t), rp*np.sin(t)) for t in th]
    xs=np.linspace(pc,-pc,m)                                 # top side, bulged
    pts+=[(x, rp+(bmid-rp)*(1-(x/pc)**2)) for x in xs]
    th=np.linspace(np.pi/2,3*np.pi/2,m)                      # left cap
    pts+=[(-pc+rp*np.cos(t), rp*np.sin(t)) for t in th]
    xs=np.linspace(-pc,pc,m)                                 # bottom side
    pts+=[(x, -(rp+(bmid-rp)*(1-(x/pc)**2))) for x in xs]
    c,s=np.cos(rot),np.sin(rot)
    return [(cx+x*c-z*s, cz+x*s+z*c) for x,z in pts]
def disc(cx,cz,rot,X,Z,**kw):
    d="M "+" L ".join("%.2f,%.2f"%(X(x),Z(z)) for x,z in disc_outline(cx,cz,rot))+" Z"
    at=" ".join('%s="%s"'%(k.replace('_','-'),v) for k,v in kw.items()); return f'<path d="{d}" {at}/>'
def prong(cx,cz,X,Z):
    return f'<circle cx="{X(cx):.2f}" cy="{Z(cz):.2f}" r="{rp*SC:.2f}" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>'
out=['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="500" viewBox="0 0 940 500" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset=".5" stop-color="#a6abb3"/><stop offset="1" stop-color="#565b63"/></linearGradient>
<radialGradient id="pin" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#e2e6ec"/><stop offset=".6" stop-color="#9aa0a8"/><stop offset="1" stop-color="#5e636b"/></radialGradient>
<linearGradient id="plate" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7e838b"/><stop offset="1" stop-color="#474b52"/></linearGradient><marker id="arr" markerWidth="7" markerHeight="7" refX="3" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#e0b86e"/></marker></defs>''')
out.append('<rect width="940" height="500" fill="#13110d"/>')
out.append('<text x="470" y="30" fill="#eef0f4" font-size="16" text-anchor="middle">disc pivots on an axle — crank + action rod rotate it to engage</text>')
# panel1 disengaged
cx,cz=160,270; X=lambda x:cx+x*SC; Z=lambda z:cz-z*SC
out.append('<text x="160" y="64" fill="#9ad8b0" font-size="13" text-anchor="middle">disengaged (horizontal)</text>')
out.append(f'<line x1="{X(0)}" y1="{Z(5.5)}" x2="{X(0)}" y2="{Z(-5.5)}" stroke="#b8924a" stroke-width="3" stroke-linecap="round"/>')
out.append(disc(0,0,0,X,Z,fill="url(#steel)",stroke="#eef0f4",stroke_width="1"))
for sgn in (1,-1): out.append(prong(sgn*pc,0,X,Z))
out.append(f'<circle cx="{X(0)}" cy="{Z(0)}" r="1.4" fill="#2a2d31"/>')
gap=pc-rp-rs
out.append(f'<text x="160" y="{Z(0)-56}" fill="#6ee0a0" font-size="11" text-anchor="middle">air ≈ {gap:.1f} / side</text>')
out.append(f'<text x="160" y="{Z(0)-42}" fill="#8a8f98" font-size="10" text-anchor="middle">string clears, vibrates free</text>')
# panel2 engaged
cx2,cz2=470,270; X2=lambda x:cx2+x*SC; Z2=lambda z:cz2-z*SC; rot=np.radians(62)
out.append('<text x="470" y="64" fill="#e0b86e" font-size="13" text-anchor="middle">engaged (rotated ~60°)</text>')
out.append(disc(0,0,rot,X2,Z2,fill="url(#steel)",stroke="#eef0f4",stroke_width="1"))
out.append(f'<path d="M {X2(0)+58},{Z2(0)+6} A 60 60 0 0 1 {X2(0)+40},{Z2(0)-44}" fill="none" stroke="#e0b86e" stroke-width="1.6" marker-end="url(#arr)"/>')
out.append(f'<text x="{X2(0)+70}" y="{Z2(0)-6}" fill="#e0b86e" font-size="10">rotate</text>')
P1=(pc*np.cos(rot),pc*np.sin(rot)); P2=(-P1[0],-P1[1])
sx=[(-.4,5.5),(-.4,P1[1]+0.4),(P1[0]+rp-0.1,P1[1]),(0,0),(P2[0]-rp+0.1,P2[1]),(.4,P2[1]-0.4),(.4,-5.5)]
out.append('<polyline points="%s" fill="none" stroke="#b8924a" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'%" ".join("%.1f,%.1f"%(X2(x),Z2(z)) for x,z in sx))
for P in (P1,P2): out.append(prong(P[0],P[1],X2,Z2))
out.append(f'<circle cx="{X2(0)}" cy="{Z2(0)}" r="1.4" fill="#2a2d31"/>')
out.append(f'<text x="470" y="{Z2(0)-56}" fill="#e0b86e" font-size="11" text-anchor="middle">prongs close → string pinched</text>')
# panel3 side (axle + crank + rod)
SCs=9.0; sy0=270; Y=lambda y:632+(y+9)*SCs; ZZ=lambda z:sy0-z*SCs
out.append('<text x="800" y="64" fill="#cdd2da" font-size="13" text-anchor="middle">side — both faces are the NECK (13 gap)</text>')
# plates
out.append(f'<rect x="{Y(-6.35):.1f}" y="{ZZ(6):.1f}" width="{6.35*SCs:.1f}" height="{12*SCs:.1f}" fill="url(#plate)" stroke="#33363b"/>')
out.append(f'<rect x="{Y(13):.1f}" y="{ZZ(6):.1f}" width="{6.35*SCs:.1f}" height="{12*SCs:.1f}" fill="url(#plate)" stroke="#33363b"/>')
out.append(f'<text x="{Y(-3.2):.1f}" y="{ZZ(-6)+15:.1f}" fill="#aeb3bd" font-size="9" text-anchor="middle">neck plate (front)</text>')
out.append(f'<text x="{Y(16.2):.1f}" y="{ZZ(-6)+15:.1f}" fill="#aeb3bd" font-size="9" text-anchor="middle">neck plate (back)</text>')
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
out.append(f'<text x="{Y(-3.2):.1f}" y="{ZZ(-2.0):.1f}" fill="#9aa0a8" font-size="8" text-anchor="middle">journal</text>')
# crank arm on the back end of the axle
out.append(f'<line x1="{Y(-9):.1f}" y1="{ZZ(0):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(2.6):.1f}" stroke="#cfd4da" stroke-width="2.6"/>')
out.append(f'<circle cx="{Y(-9):.1f}" cy="{ZZ(2.6):.1f}" r="2.0" fill="url(#pin)" stroke="#eef0f4" stroke-width="0.7"/>')
out.append(f'<text x="{Y(-9)-4:.1f}" y="{ZZ(1.3):.1f}" fill="#9aa0a8" font-size="9" text-anchor="end">crank</text>')
# action rod (vertical, behind neck) + pull arrow
out.append(f'<line x1="{Y(-9):.1f}" y1="{ZZ(2.6):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(-6):.1f}" stroke="#8aa0c0" stroke-width="2.6"/>')
out.append(f'<line x1="{Y(-9):.1f}" y1="{ZZ(-3.5):.1f}" x2="{Y(-9):.1f}" y2="{ZZ(-5.6):.1f}" stroke="#8aa0c0" stroke-width="1.4" marker-end="url(#arr)"/>')
out.append(f'<text x="{Y(-9)+4:.1f}" y="{ZZ(-4.6):.1f}" fill="#8aa0c0" font-size="9">rod ↓ from pedal</text>')
out.append('</svg>')
open("disc_assembly_v7.svg","w").write("\n".join(out))
import xml.dom.minidom as m; m.parse("disc_assembly_v7.svg")
import cairosvg; cairosvg.svg2png(url="disc_assembly_v7.svg",write_to="/tmp/chk.png",output_width=940)
print("ok tip-radius=prong-radius=%.1f  air/side=%.2f"%(rp,gap))
