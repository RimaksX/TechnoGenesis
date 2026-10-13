"""Текстуры покрытий солнечных панелей 16x16: пластина с рамкой, сеткой элементов и шинами; класс виден по металлу и цвету."""
from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
OUT = (18, 22, 32)
TIERS = {
    "coating_basic": dict(frame=[(70, 76, 90), (112, 120, 138), (156, 164, 182)], cell=[(20, 34, 86), (34, 58, 128), (60, 92, 176)],
                          bus=(96, 124, 196), sheen=(150, 178, 240), gap=(14, 20, 48)),
    "coating_aluminum": dict(frame=[(112, 122, 140), (170, 182, 202), (222, 230, 244)], cell=[(52, 82, 134), (88, 122, 178), (130, 164, 214)],
                             bus=(150, 184, 226), sheen=(236, 244, 252), gap=(46, 66, 104)),
    "coating_gold": dict(frame=[(128, 86, 20), (198, 144, 36), (250, 208, 84)], cell=[(120, 80, 22), (190, 138, 40), (232, 184, 70)],
                         bus=(255, 226, 120), sheen=(255, 244, 190), gap=(84, 54, 12)),
}

def build(name, t):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = {}
    for y in range(2, 14):
        for x in range(0, 16):
            px[(x, y)] = OUT                                    # контур
    for y in range(3, 13):
        for x in range(1, 15):
            edge_tl = x == 1 or y == 3
            edge_br = x == 14 or y == 12
            if edge_tl or edge_br:
                px[(x, y)] = t["frame"][2] if edge_tl and not edge_br else t["frame"][0] if edge_br and not edge_tl else t["frame"][1]
    cols = [(2, 4), (6, 8), (10, 12)]
    rows = [(4, 6), (8, 10)]
    for y in range(4, 12):
        for x in range(2, 14):
            px[(x, y)] = t["gap"]                               # зазоры между элементами
    for (x0, x1) in cols:
        for (y0, y1) in rows:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    c = t["cell"][1]
                    if x == x0 + 1:
                        c = t["bus"]                            # тонкая шина по центру элемента
                    if y == y1:
                        c = t["cell"][0]                        # тень снизу
                    if (x, y) == (x0, y0):
                        c = t["sheen"]                          # блик в углу
                    px[(x, y)] = c
    for (x, y), c in px.items():
        im.putpixel((x, y), (*c, 255))
    im.save(ITEM / f"{name}.png")

for n, t in TIERS.items():
    build(n, t)
names = list(TIERS) + ["module_worker", "radiator_copper"]
sh = Image.new("RGBA", (16 * len(names), 16), (70, 72, 80, 255))
for i, n in enumerate(names):
    sh.alpha_composite(Image.open(ITEM / f"{n}.png").convert("RGBA"), (16 * i, 0))
sh.resize((sh.width * 12, sh.height * 12), Image.NEAREST).save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/coat_new.png")
