import sys
sys.path.insert(0, '.')
from kontur_gen import machines3d as MM, model3d as M
for mid, fn in MM.ALL.items():
    m = fn() if mid != "carbon_capacitor" else fn(3)
    els, imgs, place = M.build(m)
    iss = M.validate(m, place)
    vo = M.volume_overlaps(m)
    used = sum(w*h for (_,_,w,h) in place.values())
    print(f"{mid:26s} boxes={len(m.boxes):3d} faces={len(place):3d} atlas={m.atlas} fill={used/(m.atlas**2):.0%} issues={len(iss)} overlaps={len(vo)}")
    for i in iss[:5]: print("   ", i)
    for v in vo[:8]: print("   ", m.boxes[v[0]].name, m.boxes[v[1]].name, v)
