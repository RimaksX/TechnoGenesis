import sys; sys.path.insert(0,'.')
from kontur_gen import multi as MU, assembly as A
raw = len(sys.argv)>1 and sys.argv[1]=="raw"
names = [a for a in sys.argv[1:] if a!="raw"]
for n,f in (A.RAW if raw else A.DESIGNS).items():
    if names and n not in names: continue
    m=f(); iss,ov,fl=MU.check_big(m)
    print(n,len(m.boxes),len(iss),len(ov),len(fl))
    for o in ov[:8]: print(' OVER',o)
    for x in fl[:8]: print(' FLOAT',x)
    for i in iss[:5]: print(' ISS',i)
