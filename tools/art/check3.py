import sys
sys.path.insert(0, '.')
from kontur_gen import machines3d as MM, model3d as M
EPS = 1e-6
for mid, fn in MM.ALL.items():
    m = fn() if mid != "carbon_capacitor" else fn(3)
    bs = m.boxes
    weak = []
    for i, a in enumerate(bs):
        tot = 0
        for j, b in enumerate(bs):
            if i == j: continue
            ov = [min(a.b[k], b.b[k]) - max(a.a[k], b.a[k]) for k in range(3)]
            if any(o < -EPS for o in ov): continue
            t = [k for k in range(3) if abs(ov[k]) <= EPS]
            if len(t) == 1:
                tot += ov[[k for k in range(3) if k != t[0]][0]] * ov[[k for k in range(3) if k != t[0]][1]]
        if tot < 1.0:
            weak.append((i, a.a, a.b, round(tot, 2)))
    print(mid, "слабый контакт:", len(weak))
    for w in weak: print("   ", w)
