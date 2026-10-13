"""Предпросмотр кабелей и труб по их JSON-моделям (без игры)."""
import json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, '.')
from kontur_gen import preview3d as P

A = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur")
S = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad")

def to_dir(b, d):
    (x0, y0, z0), (x1, y1, z1) = b["from"], b["to"]
    if d == "north": f, t = [x0, y0, z0], [x1, y1, z1]
    elif d == "south": f, t = [x0, y0, 16 - z1], [x1, y1, 16 - z0]
    elif d == "west": f, t = [z0, y0, x0], [z1, y1, x1]
    elif d == "east": f, t = [16 - z1, y0, x0], [16 - z0, y1, x1]
    elif d == "up": f, t = [x0, 16 - z1, y0], [x1, 16 - z0, y1]
    else: f, t = [x0, z0, y0], [x1, z1, y1]
    return dict(b, **{"from": f, "to": t})

class FB:
    def __init__(self, a, b, faces):
        self.a, self.b, self.faces, self.rot = a, b, faces, None
class FM:
    def __init__(self): self.boxes = []

def build(id_, dirs):
    core = json.loads((A / f"models/block/{id_}_core.json").read_text())
    side = json.loads((A / f"models/block/{id_}_side.json").read_text())
    els = [(e, core["textures"]) for e in core["elements"]]
    for d in dirs:
        els += [(to_dir(e, d), side["textures"]) for e in side["elements"]]
    names = sorted({v for _, t in els for v in t.values()})
    imgs = {n: Image.open(A / "textures" / (n.split(":")[1] + ".png")).convert("RGBA") for n in names}
    W = sum(i.width for i in imgs.values()); H = max(i.height for i in imgs.values())
    atlas = Image.new("RGBA", (W, H)); texs = {}; x = 0
    for n in names:
        atlas.paste(imgs[n], (x, 0)); texs[n] = x; x += imgs[n].width
    model = FM(); place = {}
    for bi, (e, t) in enumerate(els):
        model.boxes.append(FB(e["from"], e["to"], list(e["faces"])))
        for fn, f in e["faces"].items():
            tex = t[f["texture"][1:]]
            u0, v0, u1, v1 = f["uv"]
            im = imgs[tex]
            kx, ky = im.width / 16, im.height / 16
            place[(bi, fn)] = (texs[tex] + int(round(min(u0, u1) * kx)), int(round(min(v0, v1) * ky)),
                               max(1, int(round(abs(u1 - u0) * kx))), max(1, int(round(abs(v1 - v0) * ky))))
    return model, atlas, place

if __name__ == "__main__":
    ids = sys.argv[2:]
    tiles = []
    for id_ in ids:
        for dirs in (("west", "east"), ("west", "north", "up")):
            m, at, pl = build(id_, dirs)
            tiles.append(P.render(m, at, pl, yaw=35, pitch=28, px=10, bg=(70, 72, 78)))
    w, h = tiles[0].size
    sheet = Image.new("RGB", (w * 2, h * (len(tiles) // 2)))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * w, (i // 2) * h))
    sheet.save(S / sys.argv[1])
    print(sheet.size)
