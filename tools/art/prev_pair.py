import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import multi as MU, model3d as M, preview3d as P
out = sys.argv[1]; names = sys.argv[2:]
views = ((-20, 14), (28, 26))
rows = []
for n in names:
    m = MU.BIG[n]()
    els, imgs, place = M.build(m, frames=4)
    ext = max(m.X, m.Z, m.Y) * 0.6
    px = int(420 / (2 * ext))
    row = [P.render(m, imgs[1], place, yaw=y, pitch=p, px=px, extent=ext, bg=(70, 72, 80), center=(m.X / 2, m.Y / 2, m.Z / 2)) for (y, p) in views]
    rows.append(row)
w, h = rows[0][0].size
sheet = Image.new("RGB", (w * 2, h * len(rows)))
for i, row in enumerate(rows):
    for j, t in enumerate(row):
        sheet.paste(t.resize((w, h)), (j * w, i * h))
sheet.save(out); print(sheet.size)
