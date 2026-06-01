import re, numpy as np
from math import comb
s=open('clements47.md').read(); svg=s.split('## 8. Final geometry')[1]
g=np.array([[float(a),float(b)] for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="1.50" fill="#6ee0a0"/>',svg)])
d=np.array([[float(a),float(b)] for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="2.00" fill="#e0b86e"/>',svg)])
fn=1-2**(-1/12); nat=g+fn*(d-g)
def fitq(xv,zv):
    u=(xv-xv[0])/(xv[-1]-xv[0]); B=np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in u])
    A=B[:,1:5]; rhs=zv-B[:,0]*zv[0]-B[:,5]*zv[-1]; return np.array([zv[0],*np.linalg.lstsq(A,rhs,rcond=None)[0],zv[-1]])
# (a) y as fn of normalized x
cy=fitq(nat[:,0],nat[:,1]); u=(nat[:,0]-nat[0,0])/(nat[-1,0]-nat[0,0])
B=np.array([[comb(5,k)*(1-t)**(5-k)*t**k for k in range(6)] for t in u]); resA=np.abs(B@cy-nat[:,1])
# (b) parametric by chord length: x(t),y(t)
cl=np.concatenate([[0],np.cumsum(np.hypot(np.diff(nat[:,0]),np.diff(nat[:,1])))]); t=cl/cl[-1]
Bt=np.array([[comb(5,k)*(1-tt)**(5-k)*tt**k for k in range(6)] for tt in t])
def fitp(vals,t):
    B=np.array([[comb(5,k)*(1-tt)**(5-k)*tt**k for k in range(6)] for tt in t])
    A=B[:,1:5]; rhs=vals-B[:,0]*vals[0]-B[:,5]*vals[-1]; return np.array([vals[0],*np.linalg.lstsq(A,rhs,rcond=None)[0],vals[-1]])
cxp=fitp(nat[:,0],t); cyp=fitp(nat[:,1],t)
resB=np.hypot(Bt@cxp-nat[:,0],Bt@cyp-nat[:,1])
print('(a) y(x) quintic  max=%.2f  argmax=%d'%(resA.max(),resA.argmax()))
print('(b) parametric    max=%.2f  argmax=%d'%(resB.max(),resB.argmax()))
print('resA per-string (px):',np.round(resA,1))
