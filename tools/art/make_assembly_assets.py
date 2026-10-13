"""Всё остальное для собираемых машин: призрачная проекция, блок ротора, крупные передние грани контроллеров, рецепты и язык."""
import json
from pathlib import Path
from PIL import Image
import make_assembled as MA
from make_assembled import A, D, T, K, wj, shaped, strip
from kontur_gen import model3d as M

# --- призрачные кубы
def ghost(rgb):
    im = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            edge = x in (0, 15) or y in (0, 15)
            im.putpixel((x, y), (*rgb, 220 if edge else 70))
    return im
ghost((110, 225, 255)).save(T / "assembly_ghost.png")
ghost((255, 90, 80)).save(T / "assembly_ghost_wrong.png")
ghost((255, 214, 80)).save(T / "assembly_ghost_port.png")
for name in ("assembly_ghost", "assembly_ghost_wrong", "assembly_ghost_port"):
    face = {"uv": [0, 0, 16, 16], "texture": "#all"}
    wj(A / f"models/block/{name}.json", {"render_type": "minecraft:translucent",
       "textures": {"all": f"kontur:block/{name}", "particle": f"kontur:block/{name}"},
       "elements": [{"from": [0.3, 0.3, 0.3], "to": [15.7, 15.7, 15.7],
                     "faces": {f: dict(face) for f in ("north", "south", "east", "west", "up", "down")}}]})

# --- блок ротора турбины
wj(A / "blockstates/turbine_rotor.json", {"variants": {"": {"model": "kontur:block/turbine_rotor"}}})
wj(A / "models/item/turbine_rotor.json", {"parent": "kontur:block/turbine_rotor", "display": {
    "gui": {"rotation": [30, 45, 0], "scale": [0.8, 0.8, 0.8]}}})
loot = json.loads((D / "loot_table/blocks/plasma_generator.json").read_text(encoding="utf8"))
(D / "loot_table/blocks/turbine_rotor.json").write_text(json.dumps(loot, ensure_ascii=False, indent=2).replace("plasma_generator", "turbine_rotor") + "\n", encoding="utf8")
tag = A.parent.parent / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text(encoding="utf8"))
if K + "turbine_rotor" not in t["values"]:
    t["values"].append(K + "turbine_rotor")
t["values"].sort()
tag.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
shaped("turbine_rotor", ["SWS", "DPD", "SWS"], {"S": K + "steel_ingot", "W": K + "winding", "D": K + "gear_drive",
       "P": K + "precision_drive"}, K + "turbine_rotor", 2)

# --- крупные (32x32) передние грани контроллеров
def fan_tile(frame, blade, n, bg=None):
    return M.paint_face(("fan", (blade, n, frame)), 32, 32, 3)

def furnace_tile(frame):
    """Передняя грань доменной печи 16x16: литой стальной лист того же узора, что у боков, и зев с пламенем."""
    im = M.paint_face(("cast", ((80, 76, 82),)), 16, 16, 5)
    for y in range(3, 15):
        for x in range(2, 14):
            if x in (2, 13) or y == 3:
                im.putpixel((x, y), (96, 100, 110, 255))
    im.paste(M.paint_face(("mouth", (frame,)), 10, 11, 1), (3, 4))
    return im

def save(name, frames, ticks):
    frames[0][0].save(T / f"{name}_front.png")
    strip([f[1] for f in frames], T / f"{name}_front_on.png", ticks)

save("cooling_tower", [(fan_tile(None, (196, 190, 176), 5), fan_tile(i, (196, 190, 176), 5)) for i in range(4)][:4], 2)
save("turbine_hall", [(fan_tile(None, (150, 158, 172), 8), fan_tile(i, (150, 158, 172), 8)) for i in range(4)][:4], 2)
save("blast_furnace", [(furnace_tile(None), furnace_tile(i)) for i in range(4)][:4], 4)

RU = {"block.kontur.turbine_rotor": "Блок ротора",
      "status.kontur.structure_ready": "Схема собрана: щёлкните ключом по контроллеру",
      "message.kontur.assembly_ready": "Схема собрана: щёлкните по контроллеру ключом, и машина примет готовый вид",
      "wrench.kontur.assembly_on": "Машина собрана", "wrench.kontur.assembly_off": "Машина разобрана на блоки",
      "wrench.kontur.assembly_is": "Машина собрана (Shift + ключ - разобрать)",
      "tooltip.kontur.machine.turbine_hall": "Собирается из корпуса турбины: коробка 3×7×3, в тоннель 1×5×1 ставятся пять блоков ротора, контроллер в центре передней стенки. Пар даёт до 12 800 FE/т (80 FE на мБ, до 160 мБ/т), отработавший пар уходит конденсатом. С ключом в руке видна проекция недостающих блоков, а по щелчку ключа машина принимает готовый вид"}
EN = {"block.kontur.turbine_rotor": "Rotor Block",
      "status.kontur.structure_ready": "Structure complete: click the controller with the wrench",
      "message.kontur.assembly_ready": "Structure complete: click the controller with the wrench and the machine takes its finished look",
      "wrench.kontur.assembly_on": "Machine assembled", "wrench.kontur.assembly_off": "Machine taken apart into blocks",
      "wrench.kontur.assembly_is": "Machine assembled (Shift + wrench to take apart)",
      "tooltip.kontur.machine.turbine_hall": "Built from turbine casing: a 3x7x3 box, five rotor blocks go into the 1x5x1 tunnel, the controller in the middle of the front wall. Steam gives up to 12,800 FE/t (80 FE per mB, up to 160 mB/t), spent steam leaves as condensate. With the wrench in hand you see a projection of the missing blocks, and a wrench click gives the finished look"}
for f, tbl in (("ru_ru.json", RU), ("en_us.json", EN)):
    p = A / "lang" / f
    d = json.loads(p.read_text(encoding="utf8"))
    d.update(tbl)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print("ok")
