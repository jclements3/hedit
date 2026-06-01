import re, numpy as np
from math import comb
s=open('clements47.md').read()
# strip previously inserted curve block (comment + 2 polylines)
s=re.sub(r'<!-- natural \(N\) / sharp \(S\) disc-cut quintics -->\n<polyline[^\n]*\n<polyline[^\n]*\n','',s)
svg=s.split('## 8. Final geometry')[1]
g=np.array([[float(a),float(b)] for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="1.50" fill="#6ee0a0"/>',svg)])
d=np.array([[float(a),float(b)] for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="2.00" fill="#e0b86e"/>',svg)])
def fitp(vals,t):
    B=np.array([[comb(5,k)*(1-tt)**(5-k)*tt**k for k in range(6)] for tt in t])
    A=B[:,1:5]; rhs=vals-B[:,0]*vals[0]-B[:,5]*vals[-1]; return np.array([vals[0],*np.linalg.lstsq(A,rhs,rcond=None)[0],vals[-1]])
def poly(P,col):
    cl=np.concatenate([[0],np.cumsum(np.hypot(np.diff(P[:,0]),np.diff(P[:,1])))]); t=cl/cl[-1]
    cx=fitp(P[:,0],t); cy=fitp(P[:,1],t)
    tt=np.linspace(0,1,240); B=np.array([[comb(5,k)*(1-u)**(5-k)*u**k for k in range(6)] for u in tt])
    X=B@cx; Y=B@cy
    return '<polyline fill="none" stroke="%s" stroke-width="1.0" opacity="0.85" points="%s"/>'%(col," ".join("%.2f,%.2f"%(x,y) for x,y in zip(X,Y)))
fn=1-2**(-1/12); fs=1-2**(-1/6)
pn=poly(g+fn*(d-g),'#c0a0ff'); ps=poly(g+fs*(d-g),'#ff8c5a')
anchor='<!-- natural/sharp disc-cut points -->'
s=s.replace(anchor,'<!-- natural (N) / sharp (S) disc-cut quintics -->\n'+pn+'\n'+ps+'\n'+anchor)
open('clements47.md','w').write(s)
# re-extract final svg
svg2=s.split('## 8. Final geometry')[1].split('xml\n',1)[1].split('\n```',1)[0].strip()
open('erand47.svg','w').write(svg2+'\n')
print('polylines:',svg2.count('<polyline'),'| nat dots:',svg2.count('#c0a0ff'),'sharp dots:',svg2.count('#ff8c5a'))
print('wellformed:',svg2.startswith('<svg') and svg2.endswith('</svg>'))
