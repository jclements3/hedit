import numpy as np
W,H=980,620
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Georgia,serif">']
out.append('''<defs>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6eaef"/><stop offset="1" stop-color="#6a6f78"/></linearGradient>
<radialGradient id="disc" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="#dfe3e9"/><stop offset="1" stop-color="#646973"/></radialGradient>
<marker id="rot" markerWidth="9" markerHeight="9" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#e0b86e"/></marker>
<marker id="bl" markerWidth="9" markerHeight="9" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#7fb0ff"/></marker></defs>''')
out.append(f'<rect width="{W}" height="{H}" fill="#13110d"/>')
out.append('<text x="490" y="30" fill="#eef0f4" font-size="16" text-anchor="middle">neck action train — rod slides → cranks rotate all the class discs (slider-crank)</text>')

def train(yrod, ydisc, rotsign, rodcol, lab, engaged):
    o=[]
    xs=[300,470,640,810]
    throw=22 if engaged else 0
    # crank flat angle and engaged angle
    a0=np.radians(-120)                 # flat: crank up-left
    aeng=a0+np.radians(58)*rotsign
    rc=15
    o.append(f'<text x="150" y="{ydisc+5}" fill="{rodcol}" font-size="12">{lab}</text>')
    # action rod
    o.append(f'<rect x="250" y="{yrod-4}" width="600" height="8" rx="3" fill="url(#steel)" stroke="#9aa0a8" stroke-width="0.6"/>')
    for x in xs:
        a = aeng if engaged else a0
        pinx,piny = x+rc*np.cos(a), ydisc+rc*np.sin(a)
        # disc
        o.append(f'<circle cx="{x}" cy="{ydisc}" r="17" fill="url(#disc)" stroke="#eef0f4" stroke-width="0.8"/>')
        o.append(f'<circle cx="{x}" cy="{ydisc}" r="2.4" fill="#23262b"/>')          # axle
        o.append(f'<line x1="{x}" y1="{ydisc}" x2="{pinx:.0f}" y2="{piny:.0f}" stroke="#2a2d31" stroke-width="3"/>')  # crank arm
        o.append(f'<circle cx="{pinx:.0f}" cy="{piny:.0f}" r="2.6" fill="#e0b86e"/>') # crank pin
        # link from rod to pin (rod attach directly above home pin x)
        rax = x + (throw)                                                            # rod attach shifts with throw
        o.append(f'<line x1="{rax:.0f}" y1="{yrod}" x2="{pinx:.0f}" y2="{piny:.0f}" stroke="#cfd4da" stroke-width="2"/>')
        o.append(f'<circle cx="{rax:.0f}" cy="{yrod}" r="2.4" fill="#9aa0a8"/>')
        if engaged:
            o.append(f'<path d="M {x-12},{ydisc-12} A 17 17 0 0 {1 if rotsign>0 else 0} {x+ (12*rotsign):.0f},{ydisc-13}" fill="none" stroke="#e0b86e" stroke-width="1.4" marker-end="url(#rot)"/>')
    return o

# headers for the two states
# NATURAL train (top): show flat (left half) & engaged (right half) conceptually with one train each
out+=train(110,150,+1,'#c0a0ff','natural rod (1st notch)',False)
# SHARP train (bottom)
out+=train(300,340,+1,'#ff8c5a','sharp rod (2nd notch)',False)

# right side: ENGAGED illustration (one disc zoom)
zx,zy=720,540
out.append(f'<text x="490" y="500" fill="#cdd2da" font-size="12" text-anchor="middle">one station, engaged: rod slides Δ → link drives crank pin → disc turns ~60°; spring returns on release</text>')
# bell crank feeding rods (left)
out.append('<text x="120" y="110" fill="#e0b86e" font-size="11">bell-crank</text>')
for yy,c in [(110,'#c0a0ff'),(300,'#ff8c5a')]:
    out.append(f'<circle cx="150" cy="{yy+40}" r="9" fill="#2a2d31" stroke="#e0b86e" stroke-width="2"/>')
    out.append(f'<line x1="150" y1="{yy+40}" x2="250" y2="{yy}" stroke="#e0b86e" stroke-width="3"/>')
    out.append(f'<line x1="150" y1="{yy+40}" x2="150" y2="{yy+90}" stroke="#7fb0ff" stroke-width="2.6"/>')
    out.append(f'<line x1="150" y1="{yy+78}" x2="150" y2="{yy+92}" stroke="#7fb0ff" stroke-width="1.4" marker-end="url(#bl)"/>')
# slide arrows on rods
out.append('<line x1="540" y1="96" x2="600" y2="96" stroke="#c0a0ff" stroke-width="1.6" marker-end="url(#rot)"/><text x="560" y="90" fill="#c0a0ff" font-size="10">slide</text>')
out.append('<line x1="540" y1="286" x2="600" y2="286" stroke="#ff8c5a" stroke-width="1.6" marker-end="url(#rot)"/><text x="560" y="280" fill="#ff8c5a" font-size="10">slide</text>')
# return springs (right ends)
def spring(x0,y):
    pts=" ".join("%d,%d"%(x0+i*7,(y-6 if i%2 else y+6)) for i in range(7))
    return f'<polyline points="{x0-4},{y} {pts} {x0+46},{y}" fill="none" stroke="#9ad8b0" stroke-width="1.6"/>'
out.append(spring(852,110)); out.append('<text x="892" y="100" fill="#9ad8b0" font-size="10">return</text>')
out.append(spring(852,300))
# zoomed engaged station (bottom)
out+=train(540,580,+1,'#8a8f98','',True)
out.append('<text x="150" y="585" fill="#8a8f98" font-size="11">ENGAGED</text>')
out.append('</svg>')
open('action_train_v2.svg','w').write("\n".join(out))
import xml.dom.minidom as m; m.parse('action_train_v2.svg')
import cairosvg; cairosvg.svg2png(url='action_train_v2.svg',write_to='/tmp/chk.png',output_width=980)
print('built')
