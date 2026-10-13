import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import multi as MU, model3d as M, preview3d as P
out = sys.argv[1]; names = sys.argv[2:]
yaws = (-32, 38)
tiles = []
for n in names:
    m = MU.BIG[n]()
    MU.slice_model  # noqa
    els, imgs, place = M.build(m, frames=4)
    ext = max(m.X, m.Z, m.Y) * 0.78
    row = []
    for yaw in yaws:
        row.append(P.render(m, imgs[1], place, yaw=yaw, pitch=28, px=int(560 / (2 * ext)) or 6, extent=ext, bg=(70, 72, 80),
                            center=(m.X / 2, m.Y / 2, m.Z / 2)))
    tiles.append(row)
w, h = tiles[0][0].size
sheet = Image.new("RGB", (w * 2, h * len(tiles)))
for i, row in enumerate(tiles):
    for j, t in enumerate(row):
        sheet.paste(t.resize((w, h)), (j * w, i * h))
sheet.save(out)
print(sheet.size)
