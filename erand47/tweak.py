s=open('clements47.md').read()
n_dot=s.count('"1.10"')
s=s.replace('"1.10"','"0.80"')                                   # all N/S dots smaller
n_fin=s.count('stroke-width="1.0" opacity="0.85"')
s=s.replace('stroke-width="1.0" opacity="0.85"','stroke-width="0.6" opacity="0.85"')   # final-SVG curves thinner
n_gen=s.count('stroke-width="1.2" points')
s=s.replace('stroke-width="1.2" points','stroke-width="0.6" points')                   # generator curves thinner
open('clements47.md','w').write(s)
print('dots shrunk:',n_dot,'| final lines thinned:',n_fin,'| generator lines thinned:',n_gen)
# re-extract + validate final svg (NOT presenting md per request)
svg=s.split('## 8. Final geometry')[1].split('xml\n',1)[1].split('\n```',1)[0].strip()
open('erand47.svg','w').write(svg+'\n')
import xml.dom.minidom as m; m.parseString(svg); print('SVG valid; dots r=0.80, curves sw=0.6')
