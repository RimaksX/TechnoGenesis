"""Направляющая шахтёра (модели, текстура, блокстейт, лут) и текстуры трёх наконечников бура."""
import json, math
from pathlib import Path
from PIL import Image

R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"
OUT = (22, 26, 36)

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def mul(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)

# ---------------------------------------------------------------- направляющая: расклад граней по участкам одной текстуры
FACES = ("north", "south", "east", "west", "up", "down")

def dims(frm, to, f):
    dx, dy, dz = (to[0] - frm[0], to[1] - frm[1], to[2] - frm[2])
    return {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}[f]

def is_edge(x, y, w, h):
    return x == 0 or y == 0 or x == w - 1 or y == h - 1

CASING = (62, 65, 73)
PLATE = (98, 102, 112)
COPPER = [(184, 114, 66), (152, 92, 54)]

def paint(w, h, face, role):
    """Корпус направляющей: тёмная сталь, симметричная фаска (грани одной детали по-разному развёрнуты на разных сторонах),
    заклёпки по углам и шов по центру; сверху светлая планка с медной шиной по оси балки."""
    out = {}
    cx = (w // 2 - 1, w // 2) if w % 2 == 0 else (w // 2,)
    cy = (h // 2 - 1, h // 2) if h % 2 == 0 else (h // 2,)
    for y in range(h):
        for x in range(w):
            edge = is_edge(x, y, w, h)
            rivet = not edge and w >= 6 and h >= 6 and (x, y) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))
            if face == "up":
                base = PLATE
                c = mul(base, 0.74 if edge else 1.0)
                bus_len = x in cx                                   # шина вдоль оси z, доходит до самого края
                bus_cross = role == "core" and y in cy
                if bus_len or bus_cross:
                    c = COPPER[(x + y) % 2]
                elif rivet:
                    c = mul(base, 1.45)
                elif not edge and (x + y) % 4 == 0:
                    c = mul(base, 1.06)
            elif face == "down":
                c = mul(CASING, 0.6 if edge else 0.85)
            else:
                c = mul(CASING, 0.7 if edge else 1.0)
                if rivet:
                    c = mul(CASING, 1.6)
                elif not edge and w >= 6 and h >= 6 and y in cy:
                    c = mul(CASING, 0.8)                            # шов листа
                elif not edge and (x + y) % 5 == 0:
                    c = mul(CASING, 1.07)
            out[(x, y)] = (*c, 255)
    return out

class Sheet:
    def __init__(self):
        self.items = []
        self.pos = []

    def add(self, w, h, px):
        self.items.append((w, h, px))
        return len(self.items) - 1

    def pack(self, width=64):
        x = y = rowh = 0
        for (w, h, _) in self.items:
            w4, h4 = (w + 3) // 4 * 4, (h + 3) // 4 * 4
            if x + w4 > width:
                x, y, rowh = 0, y + rowh, 0
            self.pos.append((x, y))
            x += w4
            rowh = max(rowh, h4)
        self.size = (width, max(16, (y + rowh + 15) // 16 * 16))

    def image(self):
        im = Image.new("RGBA", self.size, (0, 0, 0, 0))
        for (w, h, px), (ox, oy) in zip(self.items, self.pos):
            for (x, y), c in px.items():
                im.putpixel((ox + x, oy + y), c)
        return im

    def uv(self, i):
        w, h, _ = self.items[i]
        ox, oy = self.pos[i]
        kx, ky = 16.0 / self.size[0], 16.0 / self.size[1]
        return [round(ox * kx, 4), round(oy * ky, 4), round((ox + w) * kx, 4), round((oy + h) * ky, 4)]

def element(sheet, frm, to, role, omit=()):
    ids = {}
    for f in FACES:
        if f in omit:
            continue
        w, h = dims(frm, to, f)
        ids[f] = sheet.add(w, h, paint(w, h, f, role))
    return {"from": list(frm), "to": list(to), "_f": ids, "role": role}

def finish(sheet, els):
    return [{"from": e["from"], "to": e["to"],
             "faces": {f: {"uv": sheet.uv(i), "texture": "#t"} for f, i in e["_f"].items()}} for e in els]

FACE_MAP = {"west": {"north": "west", "south": "east", "east": "south", "west": "north"},
            "east": {"north": "east", "south": "west", "east": "south", "west": "north"}}

def to_dir(b, d):
    (x0, y0, z0), (x1, y1, z1) = b["from"], b["to"]
    if d == "west":
        f, t = [z0, y0, x0], [z1, y1, x1]
    else:
        f, t = [16 - z1, y0, x0], [16 - z0, y1, x1]
    faces = {FACE_MAP[d].get(n, n): dict(v) for n, v in b["faces"].items()}
    for n in ("up", "down"):
        if n in faces:
            faces[n]["rotation"] = 90
    return dict(b, **{"from": f, "to": t, "faces": faces})

sheet = Sheet()
core_e = element(sheet, (4, 4, 4), (12, 12, 12), "core")
arm_e = element(sheet, (4, 4, 0), (12, 12, 4), "arm", omit=("south",))
sheet.pack()
core = finish(sheet, [core_e])
arm = finish(sheet, [arm_e])
tex_path = A / "textures/block/miner_rail.png"
tex_path.parent.mkdir(parents=True, exist_ok=True)
sheet.image().save(tex_path)
tex = {"t": "kontur:block/miner_rail", "particle": "kontur:block/miner_rail"}
dump(A / "models/block/miner_rail_core.json", {"textures": tex, "elements": core})
dump(A / "models/block/miner_rail_arm.json", {"textures": tex, "elements": arm})
INV = {"gui": {"rotation": [30, 225, 0], "scale": [0.9, 0.9, 0.9]}, "fixed": {"scale": [0.9, 0.9, 0.9]},
       "ground": {"scale": [0.6, 0.6, 0.6], "translation": [0, 3, 0]},
       "thirdperson_righthand": {"rotation": [75, 45, 0], "scale": [0.5, 0.5, 0.5], "translation": [0, 2.5, 0]},
       "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}
dump(A / "models/block/miner_rail_inventory.json", {"parent": "minecraft:block/block", "textures": tex, "display": INV,
                                                       "elements": core + [to_dir(arm[0], "west"), to_dir(arm[0], "east")]})
dump(A / "models/item/miner_rail.json", {"parent": "kontur:block/miner_rail_inventory"})
rot = {"north": {}, "east": {"y": 90}, "south": {"y": 180}, "west": {"y": 270}}
parts = [{"apply": {"model": "kontur:block/miner_rail_core"}}]
for d, r in rot.items():
    parts.append({"when": {d: "true"}, "apply": dict({"model": "kontur:block/miner_rail_arm"}, **r)})
dump(A / "blockstates/miner_rail.json", {"multipart": parts})
dump(D / "loot_table/blocks/miner_rail.json", {
    "type": "minecraft:block",
    "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": "kontur:miner_rail"}],
               "conditions": [{"condition": "minecraft:survives_explosion"}]}],
    "random_sequence": "kontur:blocks/miner_rail"})
dump(D / "loot_table/blocks/miner.json", {
    "type": "minecraft:block",
    "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": "kontur:miner"}],
               "conditions": [{"condition": "minecraft:survives_explosion"}]}],
    "random_sequence": "kontur:blocks/miner"})

# ---------------------------------------------------------------- наконечники бура
RAMPS = {
    "iron": [(52, 54, 62), (96, 98, 108), (146, 148, 158), (192, 194, 204), (232, 234, 242)],
    "steel": [(26, 36, 62), (52, 72, 112), (86, 112, 164), (130, 158, 208), (190, 212, 244)],
    "carbide": [(24, 22, 38), (50, 44, 74), (84, 74, 120), (132, 118, 174), (196, 184, 232)],
}
POINT = {"iron": (236, 238, 246), "steel": (224, 236, 255), "carbide": (244, 236, 255)}

def tip_texture(name):
    """Вертикальный бур остриём вниз: шестигранный хвостовик, затем конус с винтовой канавкой; свет слева."""
    ramp = RAMPS[name]
    px = {}
    for y in range(1, 15):
        if y <= 4:
            half = 3.5                                   # хвостовик
        else:
            half = 3.0 - 2.5 * (y - 5) / 9.0            # конус до острия
        for x in range(16):
            d = x + 0.5 - 8.0
            if abs(d) > half:
                continue
            s = d / max(half, 0.6)                       # -1 слева, +1 справа
            idx = 3.2 - (s + 1) * 1.55                   # свет слева, тень справа
            if y <= 4:
                if y == 1:
                    idx += 0.8                           # верхняя грань хвостовика
                if y == 4:
                    idx -= 1.2                           # кольцо у основания
            else:
                if ((x + y * 1.0) % 4.0) < 1.6:
                    idx -= 1.5                           # винтовая канавка
                elif ((x + y * 1.0) % 4.0) < 2.4:
                    idx += 0.7                           # блик на кромке витка
            col = ramp[max(0, min(4, int(round(idx))))]
            if y >= 13:
                col = POINT[name]
            px[(x, y)] = col
    return px

def save_tip(name):
    px = tip_texture(name)
    xs = [p[0] for p in px]
    ys = [p[1] for p in px]
    # по центру клетки: сдвиг целым числом пикселей, чтобы отступы слева-справа и сверху-снизу отличались не больше чем на 1
    dx = (15 - max(xs)) - min(xs)
    dy = (15 - max(ys)) - min(ys)
    sx, sy = dx // 2, dy // 2
    px = {(x + sx, y + sy): c for (x, y), c in px.items()}
    im = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
    pts = set(px)
    for (x, y), c in px.items():
        im.putpixel((x + 1, y + 1), (*c, 255))
    for (x, y) in pts:
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + ddx, y + ddy)
            if n not in pts:
                im.putpixel((n[0] + 1, n[1] + 1), (*OUT, 255))
    im = im.crop((1, 1, 17, 17))
    im.save(A / f"textures/item/drill_tip_{name}.png")
    dump(A / f"models/item/drill_tip_{name}.json", {"parent": "minecraft:item/generated",
                                                       "textures": {"layer0": f"kontur:item/drill_tip_{name}"}})
    return im

ims = [save_tip(n) for n in RAMPS]
big = Image.new("RGBA", (16 * 3, 16), (70, 72, 80, 255))
for i, im in enumerate(ims):
    big.alpha_composite(im, (16 * i, 0))
for n in RAMPS:
    im = Image.open(A / f"textures/item/drill_tip_{n}.png").convert("RGBA")
    xs = [x for y in range(16) for x in range(16) if im.getpixel((x, y))[3]]
    ys = [y for y in range(16) for x in range(16) if im.getpixel((x, y))[3]]
    print(n, "L/R", min(xs), 15 - max(xs), "T/B", min(ys), 15 - max(ys))
big.resize((16 * 3 * 12, 16 * 12), Image.NEAREST).save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/tips.png")
