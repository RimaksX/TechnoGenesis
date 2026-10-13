"""Собирает машину обратно из нарезанных клеток (каждая со своим атласом) и рисует: проверка нарезки."""
import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import multi as MU, model3d as M, preview3d as P
from kontur_gen.model3d import Model, Box
out = sys.argv[1]; name = sys.argv[2]; yaw = float(sys.argv[3]); pitch = float(sys.argv[4]); px = int(sys.argv[5])
big = MU.BIG[name]()
parts = MU.slice_model(big)
comp = Model("comp")
place = {}
atlases = []
yoff = 0
for idx, pm in sorted(parts.items()):
    els, imgs, pl = M.build(pm, frames=4)
    c, r, y = idx % big.w, (idx // big.w) % big.d, idx // (big.w * big.d)
    lo = (16 * c, 16 * y, 16 * r)
    base = len(comp.boxes)
    for bi, bx in enumerate(pm.boxes):
        nb = Box([bx.a[i] + lo[i] for i in range(3)], [bx.b[i] + lo[i] for i in range(3)], bx.mat, bx.faces, None, bx.name)
        comp.boxes.append(nb)
    for (bi, f), (x0, y0, w, h) in pl.items():
        place[(base + bi, f)] = (x0, y0 + yoff, w, h)
    atlases.append((imgs[1], yoff))
    yoff += pm.atlas
W = max(a.size[0] for a, _ in atlases)
atlas = Image.new("RGBA", (W, yoff), (0, 0, 0, 0))
for a, yo in atlases:
    atlas.paste(a, (0, yo))
ext = max(big.X, big.Z, big.Y) * 0.62
img = P.render(comp, atlas, place, yaw=yaw, pitch=pitch, px=px, extent=ext, bg=(70, 72, 80), center=(big.X / 2, big.Y / 2, big.Z / 2))
img.save(out); print(img.size)
