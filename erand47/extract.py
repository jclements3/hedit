s=open('clements47.md').read()
code=s.split('## 7. Parametric generator')[1].split('python\n',1)[1].split('\n```',1)[0]
open('gen.py','w').write(code)
print('extracted',code.count('\n'),'lines')
