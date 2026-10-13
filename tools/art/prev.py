import sys
sys.path.insert(0, '.')
from PIL import Image
from kontur_gen import machines3d as MM, model3d as M, preview3d as P
out = sys.argv[1]
yaw = float(sys.argv[2]) if len(sys.argv) > 2 else 35
ids = list(MM.ALL)
tiles = []
for mid in ids:
    fn = MM.ALL[mid]
    m = fn(4) if mid == "carbon_capacitor" else fn()
    els, imgs, place = M.build(m, frames=1 if False else None) if False else M.build(m, frames=4)
    im = P.render(m, imgs[0], place, yaw=yaw, pitch=28, px=10)
    tiles.append(im)
w, h = tiles[0].size
cols = 4
sheet = Image.new("RGB", (w*cols, h*((len(tiles)+cols-1)//cols)))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i%cols)*w, (i//cols)*h))
sheet.save(out)
print(sheet.size)
