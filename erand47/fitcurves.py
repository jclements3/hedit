import re, numpy as np
from math import comb
s=open('clements47.md').read()
svg=s.split('## 8. Final geometry')[1]
g=np.array([[float(a),float(b)] for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="1.50" fill="#6ee0a0"/>',svg)])
d=np.array([[float(a),float(b)] for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="2.00" fill="#e0b86e"/>',svg)])
fn=1-2**(-1/12); fs=1-2**(-1/6)
nat=g+fn*(d-g); shp=g+fs*(d-g)
def fit_quintic(xv,zv):
    u=(xv-xv[0])/(xv[-1]-xv[0])
    B=np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in u])
    A=B[:,1:5]; rhs=zv-B[:,0]*zv[0]-B[:,5]*zv[-1]
    return np.array([zv[0],*np.linalg.lstsq(A,rhs,rcond=None)[0],zv[-1]])
def poly(P,col):
    cx=fit_quintic(P[:,0],P[:,0]); cy=fit_quintic(P[:,0],P[:,1])  # param by normalized x
    tt=np.linspace(0,1,200); B=np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in tt])
    X=np.linspace(P[0,0],P[-1,0],200); Y=B@cy
    pts=" ".join("%.2f,%.2f"%(x,y) for x,y in zip(X,Y))
    # fit residual check (max dist of dots to curve in y at their x)
    Bd=np.array([[comb(5,k)*(1-((px-P[0,0])/(P[-1,0]-P[0,0])))**(5-k)*((px-P[0,0])/(P[-1,0]-P[0,0]))**k for k in range(6)] for px in P[:,0]])
    res=np.abs(Bd@cy - P[:,1])
    return f'<polyline fill="none" stroke="{col}" stroke-width="1.0" opacity="0.85" points="{pts}"/>', res.max()
pn,rn=poly(nat,'#c0a0ff'); ps,rs=poly(shp,'#ff8c5a')
print('max fit residual px  natural=%.2f  sharp=%.2f'%(rn,rs))
anchor='<!-- natural/sharp disc-cut points -->'
assert s.count(anchor)==1
s=s.replace(anchor, '<!-- natural (N) / sharp (S) disc-cut quintics -->\n'+pn+'\n'+ps+'\n'+anchor)
open('clements47.md','w').write(s)
print('curves inserted')
