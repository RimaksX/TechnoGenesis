import sys
sys.path.insert(0, '.')
from kontur_gen import multi as MU, model3d as M
names = sys.argv[1:] or list(MU.BIG)
for n in names:
    try:
        m = MU.BIG[n]()
    except Exception as e:
        print(f"{n:26s} ОШИБКА {e}"); continue
    iss, ov, fl = MU.check_big(m)
    print(f"{n:26s} boxes={len(m.boxes):3d} issues={len(iss)} overlaps={len(ov)} floating={len(fl)}")
    for i in iss[:6]: print("   ISSUE", i)
    for o in ov[:14]: print("   OVER", o[0], o[1], o[2], "A", o[3], "B", o[4])
    for f in fl[:8]: print("   FLOAT", f)
