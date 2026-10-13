"""Электростанция: корпуса и контроллеры паротурбинного зала и градирни (с анимацией), ротор, рецепты, язык, обновление реактора."""
import json, math
from pathlib import Path
from PIL import Image
import make_assembled as MA
from make_assembled import A, D, T, K, wj, noise, plate, strip, item, shaped

def turbine_casing():
    """Кожух турбины: светлая сталь с рядом болтов стыкового фланца по середине."""
    from kontur_gen import model3d as M3
    im = M3.paint_face(("hull", ((176, 178, 184), 8)), 16, 16, 11)
    for x in (2, 5, 8, 11, 14):
        im.putpixel((x, 7), (70, 72, 80, 255)); im.putpixel((x, 8), (212, 214, 220, 255))
    for x in range(1, 15):
        if x not in (2, 5, 8, 11, 14):
            im.putpixel((x, 7), (118, 120, 128, 255))
    return im

def cooler_casing():
    """Корпус градирни: светло-серая панель со стойками жалюзи."""
    from kontur_gen import model3d as M3
    return M3.paint_face(("corrug", ((168, 174, 186),)), 16, 16, 21)

def blades(im, cx, cy, r, frame, n, col, hub):
    for k in range(n):
        a = math.radians(frame * (90 / n) + k * 360 / n)
        for rr in range(1, r + 1):
            x = int(round(cx + math.cos(a) * rr)); y = int(round(cy + math.sin(a) * rr))
            if 0 <= x < 16 and 0 <= y < 16:
                im.putpixel((x, y), (*col, 255))
                if rr > 2:
                    xx = int(round(cx + math.cos(a + 0.35) * rr)); yy = int(round(cy + math.sin(a + 0.35) * rr))
                    if 0 <= xx < 16 and 0 <= yy < 16:
                        im.putpixel((xx, yy), (*[max(0, c - 30) for c in col], 255))
    for dx in (0, 1):
        for dy in (0, 1):
            im.putpixel((cx + dx - 1, cy + dy - 1), (*hub, 255))

def turbine_front(frame, on):
    im = turbine_casing()
    for y in range(3, 14):                                     # круглое окно ротора
        for x in range(3, 14):
            d = math.hypot(x - 8, y - 8.5)
            if d <= 5.2:
                im.putpixel((x, y), (96, 100, 112, 255) if d > 4.4 else (14, 18, 24, 255))
    blades(im, 8, 8, 4, frame if on else 0, 4, (176, 184, 198) if on else (120, 126, 138), (230, 236, 244))
    for k, c in enumerate(((70, 190, 110), (230, 190, 70), (210, 70, 60))):
        lit = (on and k == 0) or (not on and k == 2)
        im.putpixel((5 + k * 3, 14), (*(c if lit else tuple(v // 3 for v in c)), 255))
    return im

def tower_front(frame, on):
    im = cooler_casing()
    for y in range(2, 14):
        for x in range(2, 14):
            if x in (2, 13) or y in (2, 13):
                im.putpixel((x, y), (96, 100, 108, 255))
            else:
                im.putpixel((x, y), (30, 34, 40, 255) if (y % 2) else (46, 50, 58, 255))      # жалюзи
    blades(im, 8, 8, 4, frame if on else 0, 3, (200, 206, 216) if on else (140, 146, 156), (240, 244, 250))
    for k, c in enumerate(((70, 190, 110), (230, 190, 70), (210, 70, 60))):
        lit = (on and k == 0) or (not on and k == 2)
        im.putpixel((5 + k * 3, 14), (*(c if lit else tuple(v // 3 for v in c)), 255))
    return im

turbine_casing().save(T / "turbine_casing.png")
cooler_casing().save(T / "cooler_casing.png")
turbine_front(0, False).save(T / "turbine_hall_front.png")
strip([turbine_front(i, True) for i in range(4)], T / "turbine_hall_front_on.png", 2)
tower_front(0, False).save(T / "cooling_tower_front.png")
strip([tower_front(i, True) for i in range(4)], T / "cooling_tower_front_on.png", 2)

MA.cube("turbine_casing", "turbine_casing")
MA.cube("cooler_casing", "cooler_casing")
MA.controller("turbine_hall", "turbine_casing")
MA.controller("cooling_tower", "cooler_casing")

# ротор: вал и две пары лопаток на каждый блок тоннеля
rotor = Image.new("RGBA", (16, 16))
for y in range(16):
    for x in range(16):
        v = 150 - y * 3 + noise(x, y, 31) * 2
        rotor.putpixel((x, y), (v, v + 4, v + 12, 255))
rotor.save(T / "turbine_rotor.png")
def box(frm, to):
    return {"from": frm, "to": to, "faces": {f: {"uv": [0, 0, 16, 16], "texture": "#0"} for f in ("north", "south", "east", "west", "up", "down")}}
wj(A / "models/block/turbine_rotor.json", {"textures": {"0": "kontur:block/turbine_rotor", "particle": "kontur:block/turbine_rotor"},
   "elements": [box([7, 7, 0], [9, 9, 16]), box([1, 7.6, 3.5], [15, 8.4, 5]), box([7.6, 1, 3.5], [8.4, 15, 5]),
                box([2, 7.6, 11], [14, 8.4, 12.5]), box([7.6, 2, 11], [8.4, 14, 12.5])]})

# лут, тег кирки
loot = json.loads((D / "loot_table/blocks/plasma_generator.json").read_text(encoding="utf8"))
ids = ("turbine_casing", "cooler_casing", "turbine_hall", "cooling_tower")
for id_ in ids:
    (D / f"loot_table/blocks/{id_}.json").write_text(json.dumps(loot, ensure_ascii=False, indent=2).replace("plasma_generator", id_) + "\n", encoding="utf8")
tag = A.parent.parent / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text(encoding="utf8"))
for id_ in ids:
    if K + id_ not in t["values"]:
        t["values"].append(K + id_)
t["values"].sort()
tag.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

# рецепты
shaped("turbine_casing", ["SSS", "WFW", "SSS"], {"S": K + "steel_ingot", "W": K + "winding", "F": K + "machine_frame"}, K + "turbine_casing", 6)
shaped("turbine_hall", ["PWP", "MFM", "VCV"], {"P": K + "precision_drive", "W": K + "winding", "M": K + "power_module",
       "F": K + "turbine_casing", "V": K + "valve_block", "C": K + "control_circuit"}, K + "turbine_hall")
shaped("cooler_casing", ["SSS", "SFS", "SSS"], {"S": "smooth_stone", "F": K + "machine_frame"}, K + "cooler_casing", 6)
shaped("cooling_tower", ["VBV", "DFD", "WCW"], {"V": K + "valve_block", "B": "bucket", "D": K + "gear_drive",
       "F": K + "cooler_casing", "W": K + "winding", "C": K + "control_circuit"}, K + "cooling_tower")

RU = {"block.kontur.turbine_casing": "Корпус турбины", "block.kontur.turbine_hall": "Паротурбинный зал",
      "block.kontur.cooler_casing": "Корпус градирни", "block.kontur.cooling_tower": "Градирня",
      "fluid_type.kontur.condensate": "Конденсат",
      "status.kontur.scram": "Аварийная остановка: реактор остывает",
      "gui.kontur.reactor_heat": "Температура реактора: %s%%",
      "gui.kontur.reactor_scram": "Остановлен: включится, остыв ниже 40%",
      "tooltip.kontur.stage.fusion": "Термоядерный энергоблок",
      "tooltip.kontur.machine.fusion_reactor": "Собирается из корпуса: коробка 5×5×4 с пустой камерой 3×3×2, контроллер в центре передней стенки на втором ряду, порты в любом месте стенки. Горит водород и плазма с литиевым стержнем, вода уносит тепло и становится паром (до 100 мБ/т). Без воды перегрев и аварийная остановка. Ток даёт турбина",
      "tooltip.kontur.machine.turbine_hall": "Собирается из корпуса турбины: коробка 3×7×3 с тоннелем ротора 1×5×1, контроллер в центре передней стенки. Пар даёт до 12 800 FE/т (80 FE на мБ, до 160 мБ/т), отработавший пар уходит конденсатом",
      "tooltip.kontur.machine.cooling_tower": "Собирается из корпуса градирни: башня 3×3×6 с шахтой 1×1×4, контроллер в центре передней стенки. Остужает конденсат до воды (95%, до 200 мБ/т), вентиляторы берут 150 FE/т"}
EN = {"block.kontur.turbine_casing": "Turbine Casing", "block.kontur.turbine_hall": "Steam Turbine Hall",
      "block.kontur.cooler_casing": "Cooling Tower Casing", "block.kontur.cooling_tower": "Cooling Tower",
      "fluid_type.kontur.condensate": "Condensate",
      "status.kontur.scram": "Emergency stop: the reactor is cooling down",
      "gui.kontur.reactor_heat": "Reactor temperature: %s%%",
      "gui.kontur.reactor_scram": "Stopped: restarts below 40%",
      "tooltip.kontur.stage.fusion": "Fusion Power Plant",
      "tooltip.kontur.machine.fusion_reactor": "Built from casing: a 5x5x4 box with an empty 3x3x2 chamber, the controller in the middle of the front wall on the second row, ports anywhere on the wall. Burns hydrogen and plasma with a lithium rod; water carries the heat away and turns to steam (up to 100 mB/t). No water means overheating and an emergency stop. The turbine makes the power",
      "tooltip.kontur.machine.turbine_hall": "Built from turbine casing: a 3x7x3 box with a 1x5x1 rotor tunnel, the controller in the middle of the front wall. Steam gives up to 12,800 FE/t (80 FE per mB, up to 160 mB/t), spent steam leaves as condensate",
      "tooltip.kontur.machine.cooling_tower": "Built from cooling tower casing: a 3x3x6 tower with a 1x1x4 shaft, the controller in the middle of the front wall. Cools condensate to water (95%, up to 200 mB/t), the fans take 150 FE/t"}
for f, tbl in (("ru_ru.json", RU), ("en_us.json", EN)):
    p = A / "lang" / f
    d = json.loads(p.read_text(encoding="utf8"))
    d.update(tbl)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print("ok")
