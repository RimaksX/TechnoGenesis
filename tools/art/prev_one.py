import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import multi as MU, model3d as M, preview3d as P
out = sys.argv[1]; name = sys.argv[2]; yaw = float(sys.argv[3]); pitch = float(sys.argv[4]); px = int(sys.argv[5])
m = MU.BIG[name]()
els, imgs, place = M.build(m, frames=4)
ext = max(m.X, m.Z, m.Y) * 0.62
img = P.render(m, imgs[1], place, yaw=yaw, pitch=pitch, px=px, extent=ext, bg=(70, 72, 80), center=(m.X / 2, m.Y / 2, m.Z / 2))
img.save(out); print(img.size)
