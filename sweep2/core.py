"""
Clements-49 design core.

`frame.svg` + this file regenerate ALL geometry. Nothing downstream is hand-edited.
build_model() returns named Components; each Component carries:
  .loops : list of cross-section loops (N,3)  -> for wireframe / native B-rep loft
  .mesh  : (verts, faces) triangle mesh       -> universal, for every mesh writer

Coordinates: z-up mm, floor z=0, +x bass->treble, +y action/disc side.
"""
import re, numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

FLOOR = 1915.254
ROSE_TURNS = 0.5   # column-rose spiral over crown->base (matches harp_gen/FCMacro shell); convoy cars ride the helix

PARAMS = dict(
    S=160, M=90,                      # frame stations, points/ring
    PLATE_OUT=35.3, PLATE_LEG=3.4,    # neck/pillar U-beam (brass plate relationship)
    Z_REUNION=130.0, Z_SOLID=40.0, T_THIN=4.0, T_THICK=10.0,  # base shell wall grading
    N_BASE=18, CLOSE=10.0,            # base slices, foot-merge close
    N_FEET=4, FOOT_HALF_DEG=20.0, FOOT_H=20.0, FOOT_TAPER=0.35, FOOT_BIAS=1.15,
)

class Component:
    def __init__(self, name, mesh, loops=None):
        self.name=name; self.mesh=mesh; self.loops=loops

# ---------------- frame.svg ----------------
def _flatten(d, steps=48):
    # full path parser: M/L/C/V/H/Z, absolute & relative (re-authored frame uses V/H + relative c)
    t=re.findall(r'[MmCcLlVvHhZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',d)
    pts=[];i=0;x=0.0;y=0.0;cmd=None
    def n():
        nonlocal i;v=float(t[i]);i+=1;return v
    while i<len(t):
        if t[i] in 'MmCcLlVvHhZz':cmd=t[i];i+=1
        if cmd is None:i+=1;continue
        C=cmd.upper();rel=cmd.islower()
        if C=='M':
            a,b=n(),n();x,y=((x+a),(y+b)) if (rel and pts) else (a,b)
            pts.append(np.array([x,y]));cmd='l' if rel else 'L'
        elif C=='L':
            a,b=n(),n();x,y=((x+a),(y+b)) if rel else (a,b);pts.append(np.array([x,y]))
        elif C=='H':
            a=n();x=(x+a) if rel else a;pts.append(np.array([x,y]))
        elif C=='V':
            a=n();y=(y+a) if rel else a;pts.append(np.array([x,y]))
        elif C=='C':
            x1,y1,x2,y2,ex,ey=n(),n(),n(),n(),n(),n()
            if rel:x1+=x;y1+=y;x2+=x;y2+=y;ex+=x;ey+=y
            cur=np.array([x,y]);c1=np.array([x1,y1]);c2=np.array([x2,y2]);e=np.array([ex,ey])
            for s in range(1,steps+1):
                u=s/steps;pts.append((1-u)**3*cur+3*(1-u)**2*u*c1+3*(1-u)*u**2*c2+u**3*e)
            x,y=ex,ey
        else:  # Z
            pass
    return np.array(pts)

def load_frame(svg_path):
    import re as _re
    svg=open(svg_path).read()
    def getd(*pids):                              # accept legacy *_combined_path or re-authored *_curve ids
        for pid in pids:
            key='id="%s"'%pid
            if key in svg:
                i=svg.index(key);ps=svg.rfind('<path',0,i);pe=svg.index('/>',i)
                m=_re.search(r'\sd="([^"]*)"',svg[ps:pe])
                if m:return m.group(1)
        raise KeyError(pids)
    return (_flatten(getd("green_combined_path","green_curve")),
            _flatten(getd("red_combined_path","red_curve")),
            _flatten(getd("blue_combined_path","blue_curve")))

# ---------------- section family ----------------
def _curve(c,b,n=720):
    th=np.linspace(0,2*np.pi,n,endpoint=False);r=b*(c+np.cos(th))
    return np.column_stack([-r*np.sin(th),r*np.cos(th)])
def _run(m):
    best=(0,0);i=0;N=len(m)
    while i<N:
        if m[i]:
            j=i
            while j<N and m[j]:j+=1
            if j-i>best[1]-best[0]:best=(i,j)
            i=j
        else:i+=1
    return np.arange(*best)
def _arc(c,b,yc,l2r):
    P=_curve(c,b);P=np.roll(P,-np.argmin(P[:,1]),0);A=P[_run(P[:,1]>=yc)]
    if (A[0,0]>A[-1,0])==l2r:A=A[::-1]
    return A
def _shell(ci,b): return Polygon(_curve(2.0,b),[_curve(ci,b)])
def _opened(yc,b):
    oa=_arc(2.0,b,yc,True);ia=_arc(1.0,b,yc,False)
    xol,xor=oa[0,0],oa[-1,0];xir,xil=ia[0,0],ia[-1,0];foot=min(oa[:,1].min(),-b)
    return Polygon(np.vstack([oa,[[xor,yc],[xor,foot],[xir,foot],[xir,yc]],ia,
                              [[xil,yc],[xil,foot],[xol,foot],[xol,yc]]]))
def _fillet(p,r): return p.buffer(-r,join_style="round").buffer(2*r,join_style="round").buffer(-r,join_style="round")

def limacon(g,b,fr=0.3):
    r=min(fr*b/2,0.7*g*b);base=_shell(2-2*g,b)
    P=_fillet(base,r) if r>1e-3 else base
    if P.is_empty or P.area<1e-6:P=base
    e=np.array(P.exterior.coords);e[:,1]-=e[:,1].min();return e
def opened(g,b):
    yc=(g-0.5)/0.5*1.4*b;P=_opened(max(yc,1e-3),b)
    e=np.array(P.exterior.coords);e[:,1]-=e[:,1].min();return e
def plate_u(outer_w,leg_w,H):
    ow=outer_w/2;iw=max(ow-leg_w,0.5)
    return np.array([(-ow,0),(-ow,H),(ow,H),(ow,0),(iw,0),(iw,H-leg_w),(-iw,H-leg_w),(-iw,0)])

def section_rings(g,b,fr=0.3):
    """The real morph. Returns rings with the DIMPLE at y=0 (spine), belly up:
       g<=0.5 -> [outer limaçon c=2, inner bore c_in=2-2g]   (hollow shell, 2 rings)
       g> 0.5 -> [U-beam outline]  (_opened: outer+cardioid arcs bridged by legs, 1 ring)
    Outer-and-bore are shifted together so the dimple lands on the spine."""
    if g<=0.5:
        rr=min(fr*b/2,0.7*g*b)
        P=_fillet(_shell(2-2*g,b),rr) if rr>1e-3 else _shell(2-2*g,b)
        if P.is_empty or P.area<1e-6: P=_shell(2-2*g,b)
    else:
        yc=(g-0.5)/0.5*1.4*b
        rr=min(fr*b/2,0.7*g*b)
        Pu=_opened(max(yc,1e-3),b)
        P=_fillet(Pu,rr) if rr>1e-3 else Pu
        if P.is_empty or P.area<1e-6: P=Pu
    rings=[np.array(P.exterior.coords)]+[np.array(h.coords) for h in P.interiors]
    sh=rings[0][:,1].min()                       # dimple of the OUTER ring -> y=0
    return [r-[0,sh] for r in rings]

def _variable_bore(ext, t_spine, t_wing, t_shell):
    """Spine-and-wings inner wall: offset the outer contour `ext` (dimple/spine at
    min-y, belly up) INWARD by an angle-dependent wall t(theta), theta=0 at the
    dimple/front face, 180 at the belly. Replaces the single uniform crown=2gb so
    the wall is THICK at the spine (UD load-path/stringbar), THIN at the radiating
    wings, and a thin woven value around the shell. Graded (no step -> no stress riser)."""
    P=Polygon(ext)
    if not P.is_valid: P=P.buffer(0)
    if P.geom_type=="MultiPolygon": P=max(P.geoms,key=lambda g:g.area)
    C=np.array(P.centroid.coords[0])
    e=_resample(np.array(P.exterior.coords),720)
    d=np.roll(e,-1,0)-np.roll(e,1,0)
    nrm=np.c_[d[:,1],-d[:,0]]; nrm/=(np.hypot(*nrm.T)[:,None]+1e-12)
    to_c=C-e; nrm[np.sum(nrm*to_c,1)<0]*=-1            # inward (toward centroid)
    dd=e-C; th=np.degrees(np.arccos(np.clip(-dd[:,1]/(np.hypot(*dd.T)+1e-12),-1,1)))
    def tt(a):
        if a<=20: return t_spine
        if a<=70: return t_spine+(t_wing-t_spine)*(a-20)/50.0
        return t_wing+(t_shell-t_wing)*min((a-70)/20.0,1.0)
    t=np.array([tt(a) for a in th])
    Pi=Polygon(e+nrm*t[:,None]).buffer(0)
    if Pi.is_empty or Pi.geom_type=="MultiPolygon" or Pi.area<1e-6:
        Pi=P.buffer(-min(t_spine,t_wing,t_shell))      # robust fallback: uniform thin
        if getattr(Pi,"geom_type","")=="MultiPolygon": Pi=max(Pi.geoms,key=lambda g:g.area)
    return np.array(Pi.exterior.coords)

# ---------------- helpers ----------------
def _resample(poly,n):
    poly=np.vstack([poly,poly[:1]]);d=np.r_[0,np.cumsum(np.hypot(*np.diff(poly,axis=0).T))]
    if d[-1]==0:return np.repeat(poly[:1],n,0)
    u=np.linspace(0,d[-1],n,endpoint=False)
    return np.c_[np.interp(u,d,poly[:,0]),np.interp(u,d,poly[:,1])]
def _roll(e):
    k=int(np.argmax(e[:,1]*1e4-np.abs(e[:,0])));return np.roll(e,-k,axis=0)  # belly/crown apex (unique)
def skin_tube(loops, closed_ring=True, cap_ends=False):
    """loops: list of (N,3) consistent N -> triangle mesh."""
    V=[];F=[];N=len(loops[0])
    for lp in loops:
        for p in lp:V.append(p)
    for k in range(len(loops)-1):
        for j in range(N):
            a=k*N+j;b=k*N+(j+1)%N;c=(k+1)*N+(j+1)%N;d=(k+1)*N+j
            F+=[[a,b,c],[a,c,d]]
    return np.array(V,float),np.array(F,int)

def cap_annulus(ring_out, ring_in, flip=False):
    """Triangulate the flat annular cap between two M-point rings (outer over inner).
    Vertices are expected stacked [ring_out (M), ring_in (M)] starting at index 0."""
    M=len(ring_out);F=[]
    for j in range(M):
        a=j;b=(j+1)%M;c=M+(j+1)%M;d=M+j
        F+=[[a,b,c],[a,c,d]]
    F=np.array(F,int)
    if flip:F=F[:,::-1]
    return F

# ---------------- frame loft ----------------
def _frame_rings(green,red,blue,P,convoy=False,anchors=None):
    # convoy=True: build the stylized convoy road as ONE continuous outer loop (c=2 family
    # all the way: limaçon shell -> opened U), so vertex-index isolines stay continuous through
    # the morph (no opened->plate_u shape switch), and repair the spurious fixed-centre normal
    # double-flip across the rear shoulder. Default (False) preserves the loft/base behaviour.
    seg=np.r_[0,np.cumsum(np.hypot(*np.diff(green,axis=0).T))]
    S=P["S"];M=P["M"];us=np.linspace(0,seg[-1],S)
    spine=np.c_[np.interp(us,seg,green[:,0]),np.interp(us,seg,green[:,1])];rs=us
    n1=np.array([944.8366,592.44576]);n3=np.array([833.122,604.645]);n0=np.array([251.243,1781.29])
    arc1=rs[np.argmin(np.hypot(*(spine-n1).T))];arc3=rs[np.argmin(np.hypot(*(spine-n3).T))]
    if convoy:
        # The canonical morph axis (section 1) is the pole-origin L-corner at frame (963,560):
        # the limaçon body meets the U-beam pillar at a sharp corner, not a long pillar-ward ramp.
        # Anchor arc1/arc3 to bracket that corner so the convoy crosswalks + purple morph circle
        # land on the L (the engine draws the circle at the stoplight midpoint).
        ipole=int(np.argmin(np.hypot(spine[:,0]-963.,spine[:,1]-560.)))
        arc1=rs[max(ipole-1,0)];arc3=rs[min(ipole+1,S-1)]
    if anchors:                                   # authored transition anchors (picker spec)
        def _snap(a):
            return int(np.argmin(np.hypot(spine[:,0]-a['x'],spine[:,1]-a['y'])))
        arc1=rs[_snap(anchors['sh_in'])];arc3=rs[_snap(anchors['sh_out'])]
    cen=np.array([400.,900.])
    def tang(i):
        a=spine[max(i-1,0)];b=spine[min(i+1,S-1)];v=b-a;nn=np.hypot(*v);return v/nn if nn else np.array([1.,0.])
    def fh(p,d,poly):
        best=None
        for i in range(len(poly)-1):
            a=poly[i];b=poly[i+1];e=b-a;den=d[0]*(-e[1])-d[1]*(-e[0])
            if abs(den)<1e-9:continue
            r=a-p;t=(r[0]*(-e[1])-r[1]*(-e[0]))/den;u=(d[0]*r[1]-d[1]*r[0])/den
            if 0<=u<=1 and t>1e-3 and (best is None or t<best):best=t
        return best
    def NhC(i):
        p=spine[i];T=tang(i);Nn=np.array([-T[1],T[0]])
        if (p-cen)@Nn<0:Nn=-Nn
        return Nn,fh(p,Nn,red),fh(p,Nn,blue)
    def gv(s,h,c,g1):
        if s<arc1:return min(max(2*c/h,0.03),0.49)
        if s<=arc3:return g1+(1.0-g1)*(s-arc1)/(arc3-arc1)
        return 1.0
    i1=int(np.argmin(np.hypot(*(spine-n1).T)));N,h1,c1=NhC(i1)
    g1=min(max(2*(c1 or 6)/(h1 or 200),0.05),0.49)
    ifl=min([i for i in range(S) if rs[i]<arc1],key=lambda i:abs(FLOOR-spine[i,1]))
    N,hf,cf=NhC(ifl);hf=hf or 200;bf=hf/4;gf=gv(rs[ifl],hf,cf or 6,g1)
    W_out=np.ptp(_curve(2.0,bf)[:,0]);W_in=np.ptp(_curve(2-2*gf,bf)[:,0]);LEG_F=(W_out-W_in)/2
    ub=[i for i in range(S) if rs[i]>arc3];ic=min(ub,key=lambda i:np.hypot(*(spine[i]-n0)))
    sc=rs[ic];se=rs[-1]
    def Udims(s):
        if s<=sc:return P["PLATE_OUT"],P["PLATE_LEG"]
        t=(s-sc)/(se-sc);return P["PLATE_OUT"]*(W_out/P["PLATE_OUT"])**t, P["PLATE_LEG"]*(LEG_F/P["PLATE_LEG"])**t
    ext1=limacon(g1,(h1 or 80)/4);W1=np.ptp(ext1[:,0])
    # normal field (fixed-centre). For the convoy, repair the spurious double-flip across the
    # rear shoulder by holding the same side as just-before-shoulder through the morph window.
    Nfield=np.array([NhC(i)[0] for i in range(S)])
    if convoy:
        i_a1=int(np.argmin(np.abs(rs-arc1))); i_a3=int(np.argmin(np.abs(rs-arc3)))
        for i in range(i_a1,min(i_a3+8,S-1)+1):
            if Nfield[i]@Nfield[i-1]<0: Nfield[i]=-Nfield[i]
    rings=[];prevh=200.;bores=[]      # bores[i]=inner-bore ring (M pts) where the hollow shell exists, else None
    # spine-and-wings: soundbox (s<arc1) wall is keyed to cumulative load via spine-y (base=max y, treble=min y)
    _sb_ys=[spine[i,1] for i in range(S) if rs[i]<arc1]
    _sb_ymin=min(_sb_ys) if _sb_ys else 0.0; _sb_ymax=max(_sb_ys) if _sb_ys else 1.0  # treble=min, base=max
    apex_i=int(np.argmin(spine[:,1])) # top of the harp; stations after this descend = the column (rose)
    def _vang(i):
        a=spine[max(i-2,0)];bb=spine[min(i+2,S-1)];vv=bb-a
        return np.degrees(np.arctan2(abs(vv[0]),abs(vv[1])))
    crown_i=next((i for i in range(apex_i,S) if _vang(i)<10), apex_i+6)  # neck->column junction
    CROWN_WIN=8
    if anchors:
        crown_i=int(np.argmin(np.hypot(spine[:,0]-anchors['cr_out']['x'],spine[:,1]-anchors['cr_out']['y'])))
        CROWN_WIN=max(crown_i-int(np.argmin(np.hypot(spine[:,0]-anchors['cr_in']['x'],spine[:,1]-anchors['cr_in']['y']))),1)
    for i in range(S):
        _,h,c=NhC(i); N=Nfield[i]
        if h is None or h<10:h=prevh
        prevh=h;c=c if c else max(3,0.08*h);b=h/4;s=rs[i];g=gv(s,h,c,g1)
        o=np.array([spine[i,0],0.,FLOOR-spine[i,1]]);v=np.array([N[0],0.,-N[1]]);u=np.array([0.,1.,0.])
        bore=None;rose_bore=None
        if s<arc1:ext=limacon(g,b)
        elif s<=arc3:
            ext=opened(g,b);nat=np.ptp(ext[:,0]);tw=W1+(P["PLATE_OUT"]-W1)*(s-arc1)/(arc3-arc1)
            if nat>1e-6:ext[:,0]*=tw/nat
        elif convoy:
            # neck/U-beam -> ROSE column, MORPHED smoothly across a window at the crown
            # (was an abrupt one-station cut U-beam->rose; now a smoothstep blend over CROWN_WIN stations).
            def _uext():
                e=opened(1.0,b);nt=np.ptp(e[:,0])
                tt=(s-sc)/(se-sc) if se>sc else 0.0;tw=P["PLATE_OUT"]+(W_out-P["PLATE_OUT"])*min(max(tt,0),1)
                if nt>1e-6:e[:,0]*=tw/nt
                return e
            def _rext():
                th=np.linspace(0,2*np.pi,M,endpoint=False);fl=(3+0.4*np.sin(12*th))/3.4
                return np.c_[(h/2)*fl*np.cos(th), h/2+(h/2)*fl*np.sin(th)]   # centred on cyan, petals reach red
            if i<crown_i-CROWN_WIN:                        # neck -> opened U (continuous c=2 loop)
                ext=_uext()
            elif i>=crown_i:                               # descending column -> ROSE, SPIRALS down (helical flutes)
                spin=ROSE_TURNS*2*np.pi*(i-crown_i)/max(S-1-crown_i,1)   # 0 at crown -> ROSE_TURNS turns at base
                th=np.linspace(0,2*np.pi,M,endpoint=False)+spin;fl=(3+0.4*np.sin(12*th))/3.4
                ext=np.c_[(h/2)*fl*np.cos(th), h/2+(h/2)*fl*np.sin(th)]   # vertices+flutes rotate together (phase-lock kept)
                rose_bore=np.c_[(c/2)*np.cos(th), h/2+(c/2)*np.sin(th)]   # bore Ø=green<->blue, concentric, same spin
            else:                                          # CROWN MORPH: smoothstep blend U-beam -> rose
                t=(i-(crown_i-CROWN_WIN))/float(CROWN_WIN);t=t*t*(3-2*t)
                eU=_resample(_roll(_uext()),M);eR=_resample(_roll(_rext()),M)
                ext=(1-t)*eU+t*eR
        else:
            ow,lw=Udims(s);ext=plate_u(ow,lw,h)
        # INNER wall of the hollow shell: inward offset of the outer contour by the wall thickness
        # crown=b(2-c_in)=2gb. This is the real inner wall -- limaçon bore -> cardioid -> U-channel
        # whose legs open to the green line. The cusp never closes (Section 3/4), so it is CONTINUOUS.
        if convoy:
            if rose_bore is not None:                        # column rose: bore = green<->blue circle
                bore=np.array([o+q[1]*v+q[0]*u for q in _resample(rose_bore,M)])
            elif s<arc1:                                     # SOUNDBOX: spine-and-wings g(theta) variable wall
                tau=min(max((spine[i,1]-_sb_ymin)/(_sb_ymax-_sb_ymin+1e-9),0.0),1.0)  # 1=base, 0=treble
                iw2d=_variable_bore(ext, 1.5+2.5*tau, 2.5, 2.5+1.0*tau)               # spine/wing/shell mm
                bore=np.array([o+q[1]*v+q[0]*u for q in _resample(iw2d,M)])
            else:
                crown=float(np.clip(2*g*b, 2.0, 0.42*min(np.ptp(ext[:,0]),np.ptp(ext[:,1])+1e-9)))
                poly=Polygon(ext)
                if not poly.is_valid: poly=poly.buffer(0)
                inn=poly.buffer(-crown,join_style="round")
                if inn.is_empty: inn=poly.buffer(-0.5*crown,join_style="round")
                if getattr(inn,"geom_type","")=="MultiPolygon": inn=max(inn.geoms,key=lambda gg:gg.area)
                if (not inn.is_empty) and inn.area>1e-6:
                    iw2d=np.array(inn.exterior.coords)
                else:                                            # degenerate offset -> shrink toward centroid
                    cxy=ext.mean(0); iw2d=cxy+0.6*(ext-cxy)
                bore=np.array([o+q[1]*v+q[0]*u for q in _resample(iw2d,M)])
        ext=_roll(ext);R=_resample(ext,M)   # ROSE flutes are spun in `ext`; lane spin is re-applied in dimple_resample
        rings.append(np.array([o+q[1]*v+q[0]*u for q in R]));bores.append(bore)
    meta=dict(arc1=arc1,arc3=arc3,s_contact=sc,W_out=W_out,W_in=W_in,LEG_F=LEG_F)
    if convoy: meta["bores"]=bores; meta["crown_i"]=int(crown_i)
    return rings,meta

# ---------------- base shell + feet ----------------
def _smooth(u):u=np.clip(u,0,1);return u*u*(3-2*u)
def _base_and_feet(frame_mesh,P):
    import trimesh
    mesh=trimesh.Trimesh(vertices=frame_mesh[0],faces=frame_mesh[1],process=False)
    ZR=P["Z_REUNION"];ZS=P["Z_SOLID"];Tn=P["T_THIN"];Tk=P["T_THICK"]
    def wt(z):
        if z<=ZS:return Tk
        return Tk+(Tn-Tk)*_smooth((z-ZS)/(ZR-ZS))
    rings=[]
    for z in np.linspace(2.0,ZR,P["N_BASE"]):
        sec=mesh.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
        if sec is None:continue
        polys=[Polygon(d[:,:2]).buffer(0) for d in sec.discrete if len(d)>=4]
        polys=[p for p in polys if p.is_valid and p.area>1]
        if not polys:continue
        O=unary_union(polys).buffer(P["CLOSE"]).buffer(-P["CLOSE"])
        if O.geom_type=="MultiPolygon":O=max(O.geoms,key=lambda g:g.area)
        I=O.buffer(-wt(z))
        if I.geom_type=='MultiPolygon':I=max(I.geoms,key=lambda g:g.area) if len(I.geoms) else I
        rings.append((z,O,I))
    # base mesh: outer wall + inner wall
    M=120
    def ring3(poly,z):return np.c_[_resample(np.array(poly.exterior.coords),M),np.full(M,z)]
    outer=[ring3(O,z) for z,O,I in rings]
    inner=[ring3(I,z) for z,O,I in rings if not I.is_empty]
    Vo,Fo=skin_tube(outer);Vi,Fi=skin_tube(inner)
    base_V=np.vstack([Vo,Vi]);base_F=np.vstack([Fo,Fi+len(Vo)])
    base=Component("base",(base_V,base_F),loops=outer)
    # feet
    z0,O0,I0=rings[0];C=np.array(O0.centroid.coords[0]);oc=np.array(O0.exterior.coords)
    dirs=np.array([(1,1),(1,-1),(-1,1),(-1,-1)],float);dirs/=np.linalg.norm(dirs,axis=1,keepdims=True)
    bw=np.array([P["FOOT_BIAS"],P["FOOT_BIAS"],1.0,1.0]);HALF=np.radians(P["FOOT_HALF_DEG"])
    def arcwin(poly,aang):
        c=np.array(poly.exterior.coords);ca=np.arctan2(c[:,1]-C[1],c[:,0]-C[0])
        dd=(ca-aang+np.pi)%(2*np.pi)-np.pi;return c[np.abs(dd)<=HALF]
    fV=[];allF=[];base_off=0
    for d,w in zip(dirs,bw):
        A=C+(oc[np.argmax((oc-C)@d)]-C)*w;aang=np.arctan2(A[1]-C[1],A[0]-C[0])
        ow=arcwin(O0,aang);iw=arcwin(I0,aang)
        if len(ow)<2 or len(iw)<2:continue
        band=Polygon(np.vstack([ow,iw[::-1]])).buffer(0)
        if getattr(band,"geom_type","")=="MultiPolygon": band=max(band.geoms,key=lambda g:g.area)
        if band.is_empty:continue
        bc=np.array(band.centroid.coords[0]);loops=[]
        for k in range(9):
            t=k/8;z=-P["FOOT_H"]*t;sc=1.0-P["FOOT_TAPER"]*t
            poly=Polygon((np.array(band.exterior.coords)-bc)*sc+bc)
            if t>0.7:poly=poly.buffer(-3).buffer(3)
            loops.append(np.c_[_resample(np.array(poly.exterior.coords),40),np.full(40,z)])
        v,f=skin_tube(loops);allF.append(f+base_off);fV.append(v);base_off+=len(v)
    feet=Component("feet",(np.vstack(fV),np.vstack(allF)))
    return base,feet,rings

# ---------------- top level ----------------
def build_model(svg_path="frame.svg", scalars="frame_scalars.json", use_param=True, **over):
    """Default: swept-function loft driven by the five authored scalars
    (frame_scalars.json). Pass use_param=False for the legacy ray-cast loft."""
    P={**PARAMS,**over}
    if use_param:
        import os, loft_param as LP
        if not os.path.exists(scalars):
            LP.save_scalars(LP.author_scalars(svg_path), scalars)
        comps,P=LP.build_param(scalars,**over)
        return comps, dict(source="swept-function loft", scalars=scalars), P
    g,r,b=load_frame(svg_path)
    rings,meta=_frame_rings(g,r,b,P)
    frame_mesh=skin_tube(rings)
    frame=Component("frame",frame_mesh,loops=rings)
    base,feet,_=_base_and_feet(frame_mesh,P)
    return dict(frame=frame,base=base,feet=feet), meta, P

if __name__=="__main__":
    comps,meta,P=build_model()
    for n,c in comps.items():
        print(f"{n:6s} verts={len(c.mesh[0]):6d} faces={len(c.mesh[1]):6d}"
              + (f" loops={len(c.loops)}" if c.loops else ""))
    print("meta:",{k:round(v,1) for k,v in meta.items()})
