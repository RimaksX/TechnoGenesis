"""Кабели (оплётка в тёмных тонах) и трубы предметов и жидкостей: текстуры, модели, блокстейты, лут, рецепты, названия."""
import json
from pathlib import Path
from PIL import Image

R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------------- кабели
# Цвет определяет класс (1-4), одинаковый у кабелей и труб: серый, зелёный, синий, фиолетовый.
TIER_COLORS = {1: (130, 134, 140), 2: (84, 160, 110), 3: (80, 124, 206), 4: (150, 96, 200),
               5: (72, 176, 184), 6: (214, 226, 236)}      # 5 и 6 - газовые трубы: бирюзовый и белёсый
CABLES = {
    "copper_wire": dict(name_ru="Медный провод", name_en="Copper Wire", tier=1),
    "ceramic_cable": dict(name_ru="Керамический кабель", name_en="Ceramic Cable", tier=2),
    "armored_cable": dict(name_ru="Бронированный кабель", name_en="Armored Cable", tier=3),
    "superconducting_cable": dict(name_ru="Сверхпроводящий кабель", name_en="Superconducting Cable", tier=4),
}

# ---------------------------------------------------------------- трубы
PIPES = {
    "item_pipe": dict(name_ru="Труба предметов", name_en="Item Pipe", tier=1, glass=False, f=1, bands=[(2, 3)], big=False),
    "item_pipe_fast": dict(name_ru="Скоростная труба предметов", name_en="Fast Item Pipe", tier=2, glass=False, f=1,
                           bands=[(1, 2), (3, 4)], big=False),
    "item_pipe_express": dict(name_ru="Экспресс-труба предметов", name_en="Express Item Pipe", tier=3, glass=False, f=2,
                              bands=[(2, 3), (3, 4)], big=True),
    "item_pipe_ultra": dict(name_ru="Магистральная труба предметов", name_en="Trunk Item Pipe", tier=4, glass=False, f=2,
                            bands=[(2, 3), (3, 4)], big=True),
    "fluid_pipe": dict(name_ru="Труба жидкостей", name_en="Fluid Pipe", tier=1, glass=True, f=1, bands=[(2, 3)], big=False),
    "fluid_pipe_fast": dict(name_ru="Усиленная труба жидкостей", name_en="Reinforced Fluid Pipe", tier=2, glass=True, f=1,
                            bands=[(1, 2), (3, 4)], big=False),
    "fluid_pipe_heavy": dict(name_ru="Тяжёлая труба жидкостей", name_en="Heavy Fluid Pipe", tier=3, glass=True, f=2,
                             bands=[(2, 3), (3, 4)], big=True),
    "fluid_pipe_ultra": dict(name_ru="Магистральная труба жидкостей", name_en="Trunk Fluid Pipe", tier=4, glass=True, f=2,
                             bands=[(2, 3), (3, 4)], big=True),
    "gas_pipe": dict(name_ru="Газовая труба", name_en="Gas Pipe", tier=5, glass=False, f=1, bands=[(2, 3)], big=False),
    "gas_pipe_heavy": dict(name_ru="Тяжёлая газовая труба", name_en="Heavy Gas Pipe", tier=6, glass=False, f=2,
                           bands=[(2, 3), (3, 4)], big=True),
}

# ---------------------------------------------------------------- рисование граней
def mul(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)

def mixc(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(len(a)))

FACE_NAMES = ("north", "south", "east", "west", "up", "down")

def face_dims(frm, to, f):
    dx, dy, dz = (to[0] - frm[0], to[1] - frm[1], to[2] - frm[2])
    return {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}[f]

def is_edge(x, y, w, h):
    return x == 0 or y == 0 or x == w - 1 or y == h - 1

def paint_metal(w, h, tier):
    """Рисунок симметричен по обеим осям: грань одной и той же детали по-разному развёрнута на разных сторонах, поэтому
    фаска «свет сверху-слева, тень снизу-справа» давала бы разные края у одинаковых граней."""
    base = mixc((60, 62, 68), TIER_COLORS[tier], 0.18)
    out = {}
    for y in range(h):
        for x in range(w):
            c = mul(base, 0.74) if is_edge(x, y, w, h) else base
            if not is_edge(x, y, w, h):
                if w >= 6 and h >= 6:
                    if (x, y) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
                        c = mul(base, 1.55)                       # заклёпка
                    elif y in (h // 2, (h - 1) // 2) and 2 <= x <= w - 3:
                        c = mul(base, 0.86)                       # шов листа
                    elif (x + y) % 5 == 0:
                        c = mul(base, 1.06)
                else:
                    c = mul(base, 1.08)
            out[(x, y)] = (*c, 255)
    return out

def paint_glass(w, h, tier):
    frame = (92, 100, 114)
    out = {}
    for y in range(h):
        for x in range(w):
            if is_edge(x, y, w, h) or w < 4 or h < 4:
                out[(x, y)] = (*frame, 255)
            else:
                out[(x, y)] = (176, 214, 236, 54)
    if w >= 6 and h >= 6:
        for (x, y) in ((2, 2), (3, 2), (2, 3)):
            out[(x, y)] = (246, 250, 255, 190)                # блики
        out[(w - 3, h - 3)] = (214, 236, 250, 120)
    return out

def paint_collar(w, h, tier):
    """Воротник: симметричная фаска, узкие полосы (2 пикселя) - одной яркости с насечкой вдоль длинной стороны."""
    t = TIER_COLORS[tier]
    out = {}
    for y in range(h):
        for x in range(w):
            if min(w, h) <= 2:
                along = x if w >= h else y
                c = mul(t, 0.8 if along % 4 == 0 else 0.96)
            else:
                c = mul(t, 0.68 if is_edge(x, y, w, h) else 1.0)
            out[(x, y)] = (*c, 255)
    return out

def paint_cap(w, h, tier):
    """Торец воротника: тёмный фланец с болтами и углублением в центре, тонкая полоса цвета класса по краю отверстия."""
    base = (46, 48, 54)
    out = {}
    for y in range(h):
        for x in range(w):
            edge = is_edge(x, y, w, h)
            c = mul(base, 0.78 if edge else 1.0)
            if not edge:
                if (x, y) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
                    c = (104, 108, 116)                       # болты
                elif 2 <= x <= w - 3 and 2 <= y <= h - 3:
                    inner = 3 <= x <= w - 4 and 3 <= y <= h - 4
                    c = (22, 24, 28) if inner else mul(TIER_COLORS[tier], 0.7)
            out[(x, y)] = (*c, 255)
    return out

CABLE_DARK = (34, 36, 42)

def _dark(x, y, k, seed):
    """Тёмная заливка с небольшой градацией: три близких тона по детерминированной сетке."""
    hsh = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
    hsh = (hsh ^ (hsh >> 13)) * 1274126177
    step = (0.86, 1.0, 1.16)[(hsh >> 7) % 3]
    return mul(CABLE_DARK, step * k)

def _tier_px(x, y, t, seed):
    """Цвет класса с небольшим разбросом яркости по пикселям (три близких тона)."""
    hsh = (x * 19349663) ^ (y * 73856093) ^ (seed * 2654435761 & 0xFFFFFF)
    hsh = (hsh ^ (hsh >> 11)) * 2246822519 & 0xFFFFFFFF
    return mul(t, (0.96, 1.0, 1.04)[(hsh >> 9) % 3])

def paint_cable(w, h, tier, kind, seed=0):
    """Кабель: цвет класса только по краю граней (линии вдоль провода и кольцо на торце и узле), всё остальное - тёмные
    пиксели с градацией. Рисунок симметричен: грань может быть развёрнута любой стороной.
    kind: 'u' - линии по верхней и нижней строкам, 'v' - по левому и правому столбцам, 'cap' и 'core' - кольцо по периметру."""
    t = TIER_COLORS[tier]
    out = {}
    for y in range(h):
        for x in range(w):
            if kind in ("cap", "core"):
                edge = is_edge(x, y, w, h)
            elif kind == "u":
                edge = y in (0, h - 1)
            else:
                edge = x in (0, w - 1)
            if edge:
                c = _tier_px(x, y, t, seed)
            else:
                inner = kind in ("cap", "core") and is_edge(x - 1, y - 1, w - 2, h - 2) if w > 2 and h > 2 else False
                c = _dark(x, y, 0.8 if inner else 1.0, seed)
            out[(x, y)] = (*c, 255)
    return out

class Sheet:
    """Текстура одной модели: каждая грань каждой детали получает свой участок (кратный 4 пикселям), рисуется по роли."""
    def __init__(self):
        self.items = []      # (w, h, pixels)
        self.pos = []

    def add(self, w, h, pixels):
        self.items.append((w, h, pixels))
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

    def uv(self, idx):
        w, h, _ = self.items[idx]
        ox, oy = self.pos[idx]
        k = 16.0 / self.size[0]
        kv = 16.0 / self.size[1]
        return [round(ox * k, 4), round(oy * kv, 4), round((ox + w) * k, 4), round((oy + h) * kv, 4)]

def element(sheet, frm, to, painter, omit=(), runs=None):
    """Деталь-кубоид: painter(w, h, face) возвращает пиксели грани."""
    faces = {}
    for f in FACE_NAMES:
        if f in omit:
            continue
        w, h = face_dims(frm, to, f)
        idx = sheet.add(w, h, painter(w, h, f))
        faces[f] = idx
    return {"from": list(frm), "to": list(to), "_faces": faces}

def finish(sheet, els):
    """Подставляет в элементы координаты текстуры после раскладки."""
    out = []
    for e in els:
        d = {"from": e["from"], "to": e["to"],
             "faces": {f: {"uv": sheet.uv(i), "texture": "#t"} for f, i in e["_faces"].items()}}
        out.append(d)
    return out

FACE_MAP = {      # локальная грань элемента (описан для севера) -> грань после переноса на сторону d
    "north": {},
    "south": {"north": "south", "south": "north", "east": "west", "west": "east"},
    "west": {"north": "west", "south": "east", "east": "south", "west": "north"},
    "east": {"north": "east", "south": "west", "east": "south", "west": "north"},
    "up": {"north": "up", "south": "down", "up": "south", "down": "north"},
    "down": {"north": "down", "south": "up", "up": "south", "down": "north"},
}

def to_dir(b, d):
    """Элемент, описанный для севера (рука к z=0), переносится на сторону d вместе с названиями граней."""
    (x0, y0, z0), (x1, y1, z1) = b["from"], b["to"]
    if d == "north":
        f, t = [x0, y0, z0], [x1, y1, z1]
    elif d == "south":
        f, t = [x0, y0, 16 - z1], [x1, y1, 16 - z0]
    elif d == "west":
        f, t = [z0, y0, x0], [z1, y1, x1]
    elif d == "east":
        f, t = [16 - z1, y0, x0], [16 - z0, y1, x1]
    elif d == "up":
        f, t = [x0, 16 - z1, y0], [x1, 16 - z0, y1]
    else:
        f, t = [x0, z0, y0], [x1, z1, y1]
    mp = FACE_MAP[d]
    faces = {mp.get(name, name): dict(face) for name, face in b["faces"].items()}
    if d in ("west", "east"):      # оси x и z поменялись местами: верх и низ надо повернуть, иначе текстура сожмётся
        for name in ("up", "down"):
            if name in faces:
                faces[name]["rotation"] = 90
    return dict(b, **{"from": f, "to": t, "faces": faces})

INV_DISPLAY = {
    "gui": {"rotation": [30, 225, 0], "scale": [0.9, 0.9, 0.9]},
    "fixed": {"scale": [0.9, 0.9, 0.9]},
    "ground": {"scale": [0.6, 0.6, 0.6], "translation": [0, 3, 0]},
    "thirdperson_righthand": {"rotation": [75, 45, 0], "scale": [0.5, 0.5, 0.5], "translation": [0, 2.5, 0]},
    "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]},
}

def multipart(id_):
    parts = [{"apply": {"model": f"kontur:block/{id_}_core"}}]
    rot = {"north": {}, "east": {"y": 90}, "south": {"y": 180}, "west": {"y": 270}, "up": {"x": 270}, "down": {"x": 90}}
    for d, r in rot.items():
        parts.append({"when": {d: "true"}, "apply": dict({"model": f"kontur:block/{id_}_side"}, **r)})
    return {"multipart": parts}

def common(id_, texture, core, side, inv, glass=False):
    extra = {"render_type": "minecraft:translucent"} if glass else {}
    tex = {"t": texture, "particle": texture}
    dump(A / f"models/block/{id_}_core.json", dict(extra, textures=tex, elements=core))
    dump(A / f"models/block/{id_}_side.json", dict(extra, textures=tex, elements=side))
    dump(A / f"models/block/{id_}_inventory.json", dict(extra, parent="minecraft:block/block", textures=tex,
                                                          display=INV_DISPLAY, elements=inv))
    dump(A / f"models/item/{id_}.json", {"parent": f"kontur:block/{id_}_inventory"})
    dump(A / f"blockstates/{id_}.json", multipart(id_))
    dump(D / f"loot_table/blocks/{id_}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": f"kontur:{id_}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": f"kontur:blocks/{id_}"})

def save_sheet(sheet, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.image().save(path)

lang = {"ru_ru": {}, "en_us": {}}
# старые общие текстуры труб больше не нужны
import shutil
shutil.rmtree(A / "textures/block/conduit", ignore_errors=True)

STRAIGHT = {("north", "south"): {}, ("east", "west"): {"y": 90}, ("up", "down"): {"x": 90}}
DIRS6 = ("north", "south", "east", "west", "up", "down")

def cable_blockstate(id_):
    """Ядро 6x6x6 рисуется, только если кабель не идёт прямо насквозь; при прямом проходе средний отрезок такого же сечения
    продолжает провод без утолщений и колец."""
    rot = {"north": {}, "east": {"y": 90}, "south": {"y": 180}, "west": {"y": 270}, "up": {"x": 270}, "down": {"x": 90}}
    combos = []
    for mask in range(64):
        st = {d: bool(mask >> i & 1) for i, d in enumerate(DIRS6)}
        on = tuple(d for d in DIRS6 if st[d])
        if len(on) == 2 and any(set(on) == set(p) for p in STRAIGHT):
            continue
        combos.append({d: "true" if st[d] else "false" for d in DIRS6})
    parts = [{"when": {"OR": combos}, "apply": {"model": f"kontur:block/{id_}_core"}}]
    for d, r in rot.items():
        parts.append({"when": {d: "true"}, "apply": dict({"model": f"kontur:block/{id_}_side"}, **r)})
    for pair, r in STRAIGHT.items():
        when = {d: ("true" if d in pair else "false") for d in DIRS6}
        parts.append({"when": when, "apply": dict({"model": f"kontur:block/{id_}_mid"}, **r)})
    return {"multipart": parts}

for id_, c in CABLES.items():
    t = c["tier"]
    sheet = Sheet()
    def cable_paint(kinds):
        return lambda w, h, f: paint_cable(w, h, t, kinds[f], seed=w * 31 + h)
    core_el = element(sheet, (5, 5, 5), (11, 11, 11), cable_paint({f: "core" for f in FACE_NAMES}))
    arm_el = element(sheet, (5, 5, 0), (11, 11, 5),
                     cable_paint({"north": "cap", "east": "u", "west": "u", "up": "v", "down": "v"}), omit=("south",))
    mid_el = element(sheet, (5, 5, 5), (11, 11, 11),
                     cable_paint({"east": "u", "west": "u", "up": "v", "down": "v"}), omit=("north", "south"))
    mid_ew = element(sheet, (5, 5, 5), (11, 11, 11),
                     cable_paint({"north": "u", "south": "u", "up": "u", "down": "u"}), omit=("east", "west"))
    sheet.pack()
    core = finish(sheet, [core_el])
    arm = finish(sheet, [arm_el])
    mid = finish(sheet, [mid_el])
    inv = finish(sheet, [mid_ew]) + [to_dir(arm[0], "west"), to_dir(arm[0], "east")]
    save_sheet(sheet, A / f"textures/block/{id_}.png")
    tex = {"t": f"kontur:block/{id_}", "particle": f"kontur:block/{id_}"}
    dump(A / f"models/block/{id_}_core.json", dict(textures=tex, elements=core))
    dump(A / f"models/block/{id_}_side.json", dict(textures=tex, elements=arm))
    dump(A / f"models/block/{id_}_mid.json", dict(textures=tex, elements=mid))
    dump(A / f"models/block/{id_}_inventory.json", dict(parent="minecraft:block/block", textures=tex, display=INV_DISPLAY,
                                                           elements=inv))
    dump(A / f"models/item/{id_}.json", {"parent": f"kontur:block/{id_}_inventory"})
    dump(A / f"blockstates/{id_}.json", cable_blockstate(id_))
    dump(D / f"loot_table/blocks/{id_}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": f"kontur:{id_}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": f"kontur:blocks/{id_}"})
    lang["ru_ru"][f"block.kontur.{id_}"] = c["name_ru"]; lang["en_us"][f"block.kontur.{id_}"] = c["name_en"]

def paint_pipe(w, h, tier, kind, glass, seed=0):
    """Труба в том же стиле, что кабель: цвет класса только по краю, остальное - тёмная заливка с градацией (у стеклянных
    труб - стекло, чтобы была видна жидкость). kind: 'ring' - кольцо по периметру, 'u'/'v' - линии вдоль трубы,
    'band' - узкий пояс воротника (весь цвет класса), 'cap' - торец воротника: кольцо и тёмное отверстие по центру."""
    t = TIER_COLORS[tier]
    out = {}
    for y in range(h):
        for x in range(w):
            if kind == "band":
                edge = True
            elif kind in ("ring", "cap"):
                edge = is_edge(x, y, w, h)
            elif kind == "u":
                edge = y in (0, h - 1)
            else:
                edge = x in (0, w - 1)
            if edge:
                out[(x, y)] = (*_tier_px(x, y, t, seed), 255)
                continue
            if kind == "cap":
                hole = w >= 6 and h >= 6 and 2 <= x <= w - 3 and 2 <= y <= h - 3
                c = _dark(x, y, 0.5 if hole else 1.0, seed)
                out[(x, y)] = (*c, 255)
            elif glass and kind != "ring_opaque":
                out[(x, y)] = (176, 214, 236, 54)
            else:
                out[(x, y)] = (*_dark(x, y, 1.0, seed), 255)
    if glass and kind == "ring" and w >= 6 and h >= 6:
        for (x, y) in ((2, 2), (3, 2), (2, 3)):
            out[(x, y)] = (246, 250, 255, 190)                # блики
        out[(w - 3, h - 3)] = (214, 236, 250, 120)
    return out

for id_, p in PIPES.items():
    t = p["tier"]
    g = p["glass"]
    sheet = Sheet()
    def pipe_paint(kinds):
        # воротник и торцы всегда непрозрачные: стекло только у корпуса трубы
        return lambda w, h, f: paint_pipe(w, h, t, kinds[f][0], g and kinds[f][1], seed=w * 31 + h)
    core_kinds = {f: ("ring", True) for f in FACE_NAMES}
    body_kinds = {"east": ("u", True), "west": ("u", True), "up": ("v", True), "down": ("v", True)}
    collar_kinds = {"north": ("cap", False), "south": ("ring", False), "east": ("band", False), "west": ("band", False),
                    "up": ("band", False), "down": ("band", False)}
    core_el = element(sheet, (4, 4, 4), (12, 12, 12), pipe_paint(core_kinds))
    if p["big"]:       # магистральные: патрубок 8x8 и широкий воротник
        arm_els = [element(sheet, (4, 4, 0), (12, 12, 4), pipe_paint(body_kinds), omit=("north", "south")),
                   element(sheet, (3, 3, 0), (13, 13, 2), pipe_paint(collar_kinds))]
    else:              # обычные: патрубок 6x6 и воротник 8x8
        arm_els = [element(sheet, (5, 5, 0), (11, 11, 4), pipe_paint(body_kinds), omit=("north", "south")),
                   element(sheet, (4, 4, 0), (12, 12, 2), pipe_paint(collar_kinds))]
    sheet.pack()
    core = finish(sheet, [core_el])
    arm = finish(sheet, arm_els)
    inv = list(core) + [to_dir(e, d) for d in ("west", "east") for e in arm]
    save_sheet(sheet, A / f"textures/block/conduit/{id_}.png")
    common(id_, f"kontur:block/conduit/{id_}", core, arm, inv, glass=p["glass"])
    lang["ru_ru"][f"block.kontur.{id_}"] = p["name_ru"]; lang["en_us"][f"block.kontur.{id_}"] = p["name_en"]

# рецепты ведутся прямо в репозитории (баланс правился вручную), здесь они не пишутся

# ---------------------------------------------------------------- теги и названия
tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text())
for id_ in list(CABLES) + list(PIPES):
    if f"kontur:{id_}" not in t["values"]:
        t["values"].append(f"kontur:{id_}")
t["values"].sort()
dump(tag, t)

lang["ru_ru"].update({
    "wrench.kontur.mode_set": "Режим ключа:",
    "wrench.kontur.pipe.auto": "автоматически", "wrench.kontur.pipe.push": "отдаёт внутрь", "wrench.kontur.pipe.pull": "забирает", "wrench.kontur.pipe.both": "забирает и отдаёт",
    "wrench.kontur.pipe.off": "выключено",
    "wrench.kontur.pipe_side": "Труба, сторона %s: %s",
    "wrench.kontur.pipe_network": "Сеть труб: %s шт., пропускает до %s за %s тиков, забирающих сторон %s, отдающих %s, перенесено за операцию %s",
    "wrench.kontur.cable_network": "Сеть кабелей: %s шт., предел по слабейшему (%s) %s FE/t, источников %s, потребителей %s, накопителей %s, переносится %s FE/t",
    "wrench.kontur.dir.up": "сверху", "wrench.kontur.dir.down": "снизу", "wrench.kontur.dir.north": "север",
    "wrench.kontur.dir.south": "юг", "wrench.kontur.dir.east": "восток", "wrench.kontur.dir.west": "запад",
})
lang["en_us"].update({
    "wrench.kontur.mode_set": "Wrench mode:",
    "wrench.kontur.pipe.auto": "automatic", "wrench.kontur.pipe.push": "pushes in", "wrench.kontur.pipe.pull": "pulls out", "wrench.kontur.pipe.both": "pulls and pushes",
    "wrench.kontur.pipe.off": "off",
    "wrench.kontur.pipe_side": "Pipe, %s side: %s",
    "wrench.kontur.pipe_network": "Pipe network: %s pipes, up to %s per %s ticks, pulling sides %s, pushing %s, moved last operation %s",
    "wrench.kontur.cable_network": "Cable network: %s cables, limited by the weakest (%s) to %s FE/t, sources %s, consumers %s, storages %s, moving %s FE/t",
    "wrench.kontur.dir.up": "top", "wrench.kontur.dir.down": "bottom", "wrench.kontur.dir.north": "north",
    "wrench.kontur.dir.south": "south", "wrench.kontur.dir.east": "east", "wrench.kontur.dir.west": "west",
})
from collections import OrderedDict
for lg, vals in lang.items():
    p = A / f"lang/{lg}.json"
    d = json.loads(p.read_text(), object_pairs_hook=OrderedDict)
    d.update(vals)
    dump(p, d)
print("ok")
