import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import machines3d as MM, model3d as M, preview3d as P
names = sys.argv[2:]
out = sys.argv[1]
tiles = []
for n in names:
    m = MM.ALL[n](4) if n == "carbon_capacitor" else MM.ALL[n]()
    els, imgs, place = M.build(m, frames=4)
    for yaw in (30, 150):
        tiles.append(P.render(m, imgs[1], place, yaw=yaw, pitch=30, px=20, extent=14, bg=(70,72,80)))
w, h = tiles[0].size
sheet = Image.new("RGB", (w*2, h*(len(tiles)//2)))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i%2)*w, (i//2)*h))
sheet.save(out)
