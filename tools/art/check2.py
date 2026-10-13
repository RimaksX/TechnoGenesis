import sys
sys.path.insert(0, '.')
from kontur_gen import machines3d as MM, model3d as M
for mid, fn in MM.ALL.items():
    m = fn() if mid != "carbon_capacitor" else fn(3)
    fl = M.floating(m)
    print(mid, "висящих:", len(fl))
    for f in fl: print("   ", f)
