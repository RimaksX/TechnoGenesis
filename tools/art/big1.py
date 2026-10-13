import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import machines3d as MM, model3d as M, preview3d as P
out = sys.argv[1]; names = sys.argv[2:]
tiles = []
for n in names:
    m = MM.ALL[n](4) if n == "carbon_capacitor" else MM.ALL[n]()
    els, imgs, place = M.build(m, frames=4)
    tiles.append(P.render(m, imgs[1], place, yaw=28, pitch=26, px=17, extent=14, bg=(70,72,80)))
w, h = tiles[0].size
cols = 3
sheet = Image.new("RGB", (w*cols, h*((len(tiles)+cols-1)//cols)))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i%cols)*w, (i//cols)*h))
sheet.save(out)
