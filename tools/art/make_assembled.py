"""Собираемые игроком машины: термоядерный реактор и доменная печь. Текстуры корпусов и контроллеров (с анимацией), плазма,
литиевый стержень, модели, блокстейты, лут, рецепты, язык."""
import json, math
from pathlib import Path
from PIL import Image
import make_components as MC
R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"
T = A / "textures/block"
K = "kontur:"

def wj(path, d):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

def noise(x, y, k):
    h = (x * 73856093) ^ (y * 19349663) ^ (k * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h >> 9) % 5) - 2

BASE = (60, 62, 68)

def plate(k=1, base=BASE):
    im = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            c = [v + noise(x, y, k) for v in base]
            if y == 0 or x == 0:
                c = [v + 30 for v in base]
            elif y == 15 or x == 15:
                c = [v - 26 for v in base]
            elif y in (2, 13) and 2 <= x <= 13 or x in (2, 13) and 2 <= y <= 13:
                c = [v - 12 if (x + y) % 2 else v - 8 for v in base]
            im.putpixel((x, y), (*[max(0, min(255, int(v))) for v in c], 255))
    for (x, y) in ((3, 3), (12, 3), (3, 12), (12, 12)):
        im.putpixel((x, y), (130, 134, 142, 255)); im.putpixel((x + 1 if x < 8 else x - 1, y), (92, 96, 104, 255))
        im.putpixel((x, y + 1 if y < 8 else y - 1), (92, 96, 104, 255))
    return im

VIO = [(255, 238, 196), (255, 168, 80), (190, 92, 40), (70, 36, 24)]       # тёплое свечение окна реактора

def fusion_plate():
    """Корпус реактора: стальная плита с медной полосой обмотки по середине (рисунок бесшовный)."""
    im = plate(1, (78, 82, 94))
    for y in range(5, 11):
        for x in range(1, 15):
            k = 1.1 if (x % 3 == 1) else 0.86
            im.putpixel((x, y), (int(190 * k), int(108 * k), int(66 * k), 255))
    for x in range(1, 15):
        im.putpixel((x, 4), (46, 48, 56, 255)); im.putpixel((x, 11), (46, 48, 56, 255))
    return im

def fusion_front(frame, on):
    im = plate(2)
    for y in range(4, 12):
        for x in range(4, 12):
            edge = x in (4, 11) or y in (4, 11)
            im.putpixel((x, y), (96, 100, 110, 255) if edge else (14, 16, 24, 255))
    ring = [(6, 5), (7, 5), (8, 5), (9, 5), (10, 6), (10, 7), (10, 8), (10, 9), (9, 10), (8, 10), (7, 10), (6, 10),
            (5, 9), (5, 8), (5, 7), (5, 6)]
    for i, (x, y) in enumerate(ring):
        lit = on and (i + frame * 4) % 16 < 7                      # бегущий по кольцу сгусток
        im.putpixel((x, y), (*(VIO[0] if lit and (i + frame * 4) % 16 == 3 else VIO[1] if lit else VIO[3]), 255))
    core = VIO[0] if on and frame % 2 == 0 else VIO[1] if on else VIO[3]
    for (x, y) in ((7, 7), (8, 7), (7, 8), (8, 8)):
        im.putpixel((x, y), (*core, 255))
    for k, c in enumerate(((70, 190, 110), (230, 190, 70), (210, 70, 60))):
        lit = (on and k == 0) or (not on and k == 2)
        im.putpixel((5 + k * 3, 13), (*(c if lit else tuple(v // 3 for v in c)), 255))
    return im

def port():
    im = plate(3)
    for y in range(5, 11):
        for x in range(5, 11):
            edge = x in (5, 10) or y in (5, 10)
            im.putpixel((x, y), (200, 204, 210, 255) if edge else (22, 24, 28, 255))
    for (x, y) in ((6, 6), (9, 6), (6, 9), (9, 9)):
        im.putpixel((x, y), (70, 176, 184, 255))
    return im

from kontur_gen import model3d as M3

def furnace_casing():
    """Стальной сварной лист 16x16 литейного корпуса: швы и заклёпки, рисунок бесшовный."""
    return M3.paint_face(("cast", ((80, 76, 82),)), 16, 16, 5)

def furnace_top():
    """Верх стального блока: панельная плита."""
    return M3.paint_face(("tread", ((92, 98, 112),)), 16, 16, 5)

def blast_front(frame, on):
    im = furnace_casing()
    # стальная рамка и зев печи
    for y in range(3, 14):
        for x in range(3, 13):
            edge = x in (3, 12) or y in (3, 4)
            if edge:
                im.putpixel((x, y), (74, 78, 88, 255) if y > 3 else (112, 116, 126, 255))
    for y in range(5, 14):
        for x in range(4, 12):
            im.putpixel((x, y), (16, 12, 12, 255))
    if on:
        flames = [(6, 12), (7, 12), (8, 12), (9, 12), (5, 12), (10, 12), (6, 11), (7, 11), (8, 11), (9, 11), (7, 10), (8, 10)]
        shift = frame % 2
        for (x, y) in flames:
            c = (255, 190, 70) if y == 12 else (240, 120, 30) if y == 11 else (200, 70, 20)
            im.putpixel((x, y - (shift if y == 10 else 0)), (*c, 255))
        for (x, y) in ((7, 9 - shift), (8, 9 + shift - 1)):
            im.putpixel((x, y), (255, 220, 120, 255))
    else:
        for (x, y) in ((6, 12), (7, 12), (8, 12), (9, 12)):
            im.putpixel((x, y), (60, 30, 24, 255))
    return im

def strip(frames, path, ticks=6):
    w, h = frames[0].size
    sh = Image.new("RGBA", (w, h * len(frames)))
    for i, f in enumerate(frames):
        sh.paste(f, (0, h * i))
    sh.save(path)
    wj(Path(str(path) + ".mcmeta"), {"animation": {"frametime": ticks}})

fusion_plate().save(T / "fusion_casing.png")
fusion_front(0, False).save(T / "fusion_reactor_front.png")
strip([fusion_front(i, True) for i in range(4)], T / "fusion_reactor_front_on.png", 5)
port().save(T / "assembly_port.png")
furnace_casing().save(T / "furnace_casing.png")
furnace_top().save(T / "furnace_casing_top.png")
blast_front(0, False).save(T / "blast_furnace_front.png")
strip([blast_front(i, True) for i in range(4)], T / "blast_furnace_front_on.png", 4)
for old in ("fusion_controller_front.png", "fusion_controller_front_on.png"):
    if (T / old).exists():
        (T / old).unlink()

# литиевый стержень (предмет)
def rod():
    i = MC.Img()
    c = math.sqrt(0.5)
    def inside(x, y, o):
        u = ((x - o - 7.5) + (7.5 - (y - o))) * c
        v = ((y - o - 7.5) + (x - o - 7.5)) * c
        return u, v
    face = {}
    side = set()
    for y in range(16):
        for x in range(16):
            u, v = inside(x, y, 0)
            if abs(u) <= 7.2 and abs(v) <= 1.9:
                face[(x, y)] = (u, v)
            u, v = inside(x, y, 1)
            if abs(u) <= 7.2 and abs(v) <= 1.9:
                side.add((x, y))
    for p in side - set(face):
        i.p(*p, MC.STEEL[4])
    for (x, y), (u, v) in face.items():
        t = (v + 1.9) / 3.8
        if abs(u) > 6.0:
            col = MC.COPPER[1] if t < 0.5 else MC.COPPER[2]               # торцевые колпачки
        elif abs(u) < 2.6:
            col = MC.VIO[0] if t < 0.3 else MC.VIO[1] if t < 0.7 else MC.VIO[2]   # окно с литием
        else:
            col = MC.STEEL[0] if t < 0.25 else MC.STEEL[1] if t < 0.55 else MC.STEEL[2] if t < 0.85 else MC.STEEL[3]
        i.p(x, y, col)
    return i
rod().save("lithium_rod")
wj(A / "models/item/lithium_rod.json", {"parent": "minecraft:item/generated", "textures": {"layer0": "kontur:item/lithium_rod"}})

# модели и блокстейты
def cube(name, tex):
    wj(A / f"models/block/{name}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"kontur:block/{tex}"}})
    wj(A / f"blockstates/{name}.json", {"variants": {"": {"model": f"kontur:block/{name}"}}})
    wj(A / f"models/item/{name}.json", {"parent": f"kontur:block/{name}"})
cube("fusion_casing", "fusion_casing")
wj(A / "models/block/furnace_casing.json", {"parent": "minecraft:block/cube_column", "textures": {
    "end": "kontur:block/furnace_casing_top", "side": "kontur:block/furnace_casing"}})
wj(A / "blockstates/furnace_casing.json", {"variants": {"": {"model": "kontur:block/furnace_casing"}}})
wj(A / "models/item/furnace_casing.json", {"parent": "kontur:block/furnace_casing"})
cube("assembly_port", "assembly_port")

def controller(name, side, top=None):
    for suffix in ("", "_on"):
        wj(A / f"models/block/{name}{suffix}.json", {"parent": "minecraft:block/orientable", "textures": {
            "top": f"kontur:block/{top or side}", "side": f"kontur:block/{side}", "front": f"kontur:block/{name}_front{suffix}"}})
    variants = {}
    for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        for act, suffix in (("false", ""), ("true", "_on")):
            v = {"model": f"kontur:block/{name}{suffix}"}
            if y:
                v["y"] = y
            variants[f"facing={f},active={act}"] = v
    wj(A / f"blockstates/{name}.json", {"variants": variants})
    wj(A / f"models/item/{name}.json", {"parent": f"kontur:block/{name}"})
controller("fusion_reactor", "fusion_casing")
controller("blast_furnace", "furnace_casing", "furnace_casing_top")
for old in ("fusion_controller.json", "fusion_controller_on.json"):
    if (A / "models/block" / old).exists():
        (A / "models/block" / old).unlink()

# лут и тег кирки
loot = json.loads((D / "loot_table/blocks/plasma_generator.json").read_text(encoding="utf8"))
ids = ("fusion_casing", "furnace_casing", "assembly_port", "fusion_reactor", "blast_furnace")
for id_ in ids:
    (D / f"loot_table/blocks/{id_}.json").write_text(
        json.dumps(loot, ensure_ascii=False, indent=2).replace("plasma_generator", id_) + "\n", encoding="utf8")
tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text(encoding="utf8"))
for id_ in ids:
    if K + id_ not in t["values"]:
        t["values"].append(K + id_)
t["values"].sort()
tag.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

# рецепты
def item(i):
    return {"item": i if ":" in i else "minecraft:" + i}
def shaped(name, pattern, key, result, count=1):
    wj(D / f"recipe/{name}.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
                                   "key": {k: item(v) for k, v in key.items()}, "result": {"id": result, "count": count}})
shaped("fusion_casing", ["SSS", "HFH", "SSS"], {"S": K + "stainless_steel_ingot", "H": K + "heat_plate", "F": K + "machine_frame"},
       K + "fusion_casing", 6)
shaped("furnace_casing", ["BBB", "BFB", "BBB"], {"B": "brick", "F": K + "machine_frame"}, K + "furnace_casing", 8)
shaped("assembly_port", ["SVS", "WCW", "SSS"], {"S": K + "stainless_steel_ingot", "V": K + "valve_block", "W": K + "winding",
       "C": K + "control_circuit"}, K + "assembly_port", 2)
shaped("fusion_reactor", ["HZH", "MFM", "XCX"], {"H": K + "heat_plate", "Z": K + "plasma_controller", "M": K + "power_module",
       "F": K + "fusion_casing", "X": K + "processor", "C": K + "control_circuit"}, K + "fusion_reactor")
shaped("blast_furnace", ["CHC", "DFD", "VKV"], {"C": K + "furnace_casing", "H": K + "heat_plate", "D": K + "gear_drive",
       "F": K + "machine_frame", "V": K + "valve_block", "K": K + "control_circuit"}, K + "blast_furnace")
wj(D / "recipe/alloying/lithium_rod.json", {
    "type": K + "alloying", "results": [{"id": K + "lithium_rod", "count": 2}], "energy": 20000, "time": 100,
    "input": {"ingredient": item(K + "crushed_spodumene"), "count": 4},
    "input_b": {"ingredient": item(K + "stainless_steel_ingot"), "count": 1}})
def blast(name, a, na, b, nb, out, nout):
    wj(D / f"recipe/blast_smelting/{name}.json", {
        "type": K + "blast_smelting", "results": [{"id": K + out, "count": nout}], "energy": 48000, "time": 100,
        "input": {"ingredient": item(a), "count": na}, "input_b": {"ingredient": item(b), "count": nb},
        "fluid_input": {"fluids": [K + "oxygen"], "amount": 500}})
blast("steel", "iron_ingot", 8, K + "graphite", 2, "steel_ingot", 10)
blast("stainless_steel", K + "steel_ingot", 8, K + "chromium_ingot", 3, "stainless_steel_ingot", 10)

RU = {"block.kontur.fusion_casing": "Корпус реактора", "block.kontur.furnace_casing": "Огнеупорный корпус",
      "block.kontur.assembly_port": "Порт корпуса", "block.kontur.fusion_reactor": "Термоядерный реактор",
      "block.kontur.blast_furnace": "Доменная печь", "item.kontur.lithium_rod": "Литиевый стержень",
      "tooltip.kontur.stage.fusion": "Термоядерная энергетика",
      "status.kontur.structure_missing": "Не собрано: не хватает блоков корпуса",
      "status.kontur.structure_blocked": "В камере посторонний блок",
      "message.kontur.assembly_problem": "Не собрано: неверных блоков %s. Первый: %s вправо, %s вглубь, %s вверх от контроллера",
      "tooltip.kontur.machine.fusion_reactor": "Собирается из корпуса: коробка 5×5×4 с пустой камерой 3×3×2, контроллер в центре передней стенки на втором ряду, порты в любом месте стенки. Нужны водород, плазма и вода по газовым трубам и трубам жидкостей и литиевый стержень (5 минут). 8000 FE/т",
      "tooltip.kontur.machine.blast_furnace": "Собирается из огнеупорного корпуса: башня 5×5×6 с шахтой 3×3×4, контроллер в центре передней стенки на втором ряду, порты в любом месте стенки. 8 железа, 2 графита и кислород дают 10 стали",
      "tooltip.kontur.lithium_rod": "Топливо термоядерного реактора: горит 5 минут"}
EN = {"block.kontur.fusion_casing": "Reactor Casing", "block.kontur.furnace_casing": "Refractory Casing",
      "block.kontur.assembly_port": "Casing Port", "block.kontur.fusion_reactor": "Fusion Reactor",
      "block.kontur.blast_furnace": "Blast Furnace", "item.kontur.lithium_rod": "Lithium Rod",
      "tooltip.kontur.stage.fusion": "Fusion Power",
      "status.kontur.structure_missing": "Incomplete: casing blocks are missing",
      "status.kontur.structure_blocked": "A foreign block is inside the chamber",
      "message.kontur.assembly_problem": "Incomplete: %s wrong blocks. First: %s right, %s deep, %s up from the controller",
      "tooltip.kontur.machine.fusion_reactor": "Built from casing: a 5x5x4 box with an empty 3x3x2 chamber, the controller in the middle of the front wall on the second row, ports anywhere on the wall. Needs hydrogen, plasma and water through gas and fluid pipes and a lithium rod (5 minutes). 8000 FE/t",
      "tooltip.kontur.machine.blast_furnace": "Built from refractory casing: a 5x5x6 tower with a 3x3x4 shaft, the controller in the middle of the front wall on the second row, ports anywhere on the wall. 8 iron, 2 graphite and oxygen make 10 steel",
      "tooltip.kontur.lithium_rod": "Fusion reactor fuel: burns for 5 minutes"}
for f, tbl in (("ru_ru.json", RU), ("en_us.json", EN)):
    p = A / "lang" / f
    d = json.loads(p.read_text(encoding="utf8"))
    for k in ("message.kontur.fusion_problem",):
        d.pop(k, None)
    d.update(tbl)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print("ok")
