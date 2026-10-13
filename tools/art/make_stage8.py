"""Ступень x8: спрайты твёрдого шлака и шлаковой пыли, модели предметов, рецепты (аттритор, автоклав, парогенератор),
крафт машин, лут, теги, названия; экстрактор теперь выдаёт твёрдый шлак. Остальное в репозитории не трогается."""
import json, math, random, sys
from collections import OrderedDict
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
from PIL import Image
import make_forms as F
from kontur_gen.defs import METALS

R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"
F.BASES["slag"] = (64, 60, 70)
F.BASES["slagdust"] = (112, 106, 116)

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def rl(x):
    return f"kontur:{x}"

# ---------------------------------------------------------------- спрайты

def soft_sparks(a, pts, tint, core=0.9, halo=0.28):
    """Искра: центр чуть светлее/цветнее тона, вокруг мягкий переход (смешивание с цветом руды), без резкого пятна."""
    import numpy as _np
    base = a.copy()
    for (x, y) in pts:
        if not (0 <= x < 16 and 0 <= y < 16) or base[y, x, 3] == 0:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16 and base[ny, nx, 3] and a[ny, nx, 3]:
                cur = tuple(int(v) for v in a[ny, nx, :3])
                F.setpx(a, nx, ny, F.clampc(tuple(cur[i] * (1 - halo) + tint[i] * halo for i in range(3))))
    for (x, y) in pts:
        if 0 <= x < 16 and 0 <= y < 16 and base[y, x, 3]:
            cur = tuple(int(v) for v in a[y, x, :3])
            F.setpx(a, x, y, F.clampc(tuple(cur[i] * (1 - core) + tint[i] * core for i in range(3))))

def hard_slag(metal):
    """Тёмные оплавленные глыбы с металлическими искрами цвета руды."""
    rp = F.ramp(metal, "slag", 0.28)
    a = F.new()
    for (cx, cy, rw, rh, base, seed) in ((4.8, 11.2, 3.4, 2.8, 3, 12), (11.2, 11.4, 3.6, 2.9, 3, 15), (8.0, 8.0, 3.8, 3.2, 4, 18),
                                         (5.0, 5.8, 2.5, 2.2, 4, 14), (11.2, 5.6, 2.6, 2.3, 5, 16)):
        layer = F.new()
        F.rock(layer, cx, cy, rw, rh, base, rp, seed)
        layer = F.outline(layer, rp[0])
        mask = layer[..., 3] > 0
        a[mask] = layer[mask]
    soft_sparks(a, ((6, 9), (10, 10), (8, 6), (12, 5)), F.ore_tint(metal))
    return Image.fromarray(a)

def slag_dust(metal):
    """Тёмная сверхтонкая пыль с мелкими металлическими искрами."""
    rp = F.ramp(metal, "slagdust", 0.22)
    a = F.new()
    blobs = [(7.6, 9.4, 6.2, 3.4), (5.2, 7.6, 3.6, 2.6), (10.4, 7.2, 3.8, 2.8), (8.0, 5.4, 2.8, 2.2)]
    for y in range(16):
        for x in range(16):
            best = 9.0
            for (cx, cy, rw, rh) in blobs:
                best = min(best, ((x + 0.5 - cx) / rw) ** 2 + ((y + 0.5 - cy) / rh) ** 2)
            if best <= 1.0:
                depth = 1.0 - best
                t = 2 + int(depth * 3.0) + (1 if (x + y) % 2 == 0 and depth < 0.5 else 0)
                t -= 1 if y > 9 else 0
                F.setpx(a, x, y, rp[max(1, min(7, t))])
            elif best <= 1.35 and (x + y) % 2 == 0:
                F.setpx(a, x, y, rp[1])
    soft_sparks(a, ((6, 8), (9, 10), (11, 7), (5, 10)), F.ore_tint(metal))
    return Image.fromarray(a)

SPRITES = {"hard_slag": hard_slag, "slag_dust": slag_dust}
for me in METALS:
    for name, fn in SPRITES.items():
        fn(me).save(A / f"textures/item/{me.id}_{name}.png")
        dump(A / f"models/item/{me.id}_{name}.json", {"parent": "minecraft:item/generated",
                                                      "textures": {"layer0": f"kontur:item/{me.id}_{name}"}})

# ---------------------------------------------------------------- рецепты
S8 = dict(
    attrition=dict(energy=12000, time=100),
    autoclave=dict(energy=24000, time=100, steam=1000, ingots=3),
    steam=dict(energy=3200, time=100, water=1000, steam=1000),
)

def machine_recipe(kind, name, ing, results, energy, time, fluid_in=None, fluid_out=None):
    d = {"type": rl(kind), "results": results, "energy": energy, "time": time}
    if ing:
        d["input"] = {"ingredient": {"item": ing}, "count": 1}
    if fluid_in:
        d["fluid_input"] = fluid_in
    if fluid_out:
        d["fluid_results"] = fluid_out
    dump(D / f"recipe/{kind}/{name}.json", d)

def res(item, count=1, chance=1.0):
    r = {"id": item, "count": count}
    if chance < 1.0:
        r["chance"] = chance
    return r

for me in METALS:
    slag, dust = rl(f"{me.id}_hard_slag"), rl(f"{me.id}_slag_dust")
    machine_recipe("attrition", me.id, slag, [res(dust)], S8["attrition"]["energy"], S8["attrition"]["time"])
    machine_recipe("autoclaving", me.id, dust, [res(me.ingot_item, S8["autoclave"]["ingots"])],
                   S8["autoclave"]["energy"], S8["autoclave"]["time"],
                   fluid_in={"fluids": [rl("steam")], "amount": S8["autoclave"]["steam"]})
    # экстрактор: вместо минеральной фракции теперь твёрдый шлак своего металла
    p = D / f"recipe/extraction/{me.id}.json"
    d = json.loads(p.read_text())
    d["results"] = [res(slag)]
    dump(p, d)

for coal in ("coal", "charcoal"):
    machine_recipe("steam_generation", coal, f"minecraft:{coal}", [], S8["steam"]["energy"], S8["steam"]["time"],
                   fluid_in={"fluids": ["minecraft:water", rl("technical_water")], "amount": S8["steam"]["water"]},
                   fluid_out=[{"fluid": rl("steam"), "amount": S8["steam"]["steam"]}])

def shaped(name, pattern, key, result):
    dump(D / f"recipe/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()}, "result": {"id": result, "count": 1}})

shaped("attritor", ["IGI", "SFS", "IWI"],
       {"I": "minecraft:iron_ingot", "G": "minecraft:grindstone", "S": "minecraft:smooth_stone", "F": rl("machine_frame"),
        "W": rl("copper_wire")}, rl("attritor"))
shaped("steam_generator", ["BCB", "BFB", "IWI"],
       {"B": "minecraft:bricks", "C": "minecraft:cauldron", "F": rl("machine_frame"), "I": "minecraft:iron_ingot",
        "W": rl("copper_wire")}, rl("steam_generator"))
shaped("autoclave", ["IBI", "BFB", "IWI"],
       {"I": "minecraft:iron_ingot", "B": "minecraft:iron_block", "F": rl("machine_frame"), "W": rl("copper_wire")},
       rl("autoclave"))

for mid in ("attritor", "steam_generator", "autoclave"):
    dump(D / f"loot_table/blocks/{mid}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": rl(mid)}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": rl(f"blocks/{mid}")})

tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text())
for mid in ("attritor", "steam_generator", "autoclave"):
    if rl(mid) not in t["values"]:
        t["values"].append(rl(mid))
t["values"].sort()
dump(tag, t)

lang = {
    "ru_ru": {
        "block.kontur.attritor": "Аттритор", "block.kontur.steam_generator": "Парогенератор", "block.kontur.autoclave": "Автоклав",
        "fluid_type.kontur.steam": "Пар",
        "tooltip.kontur.stage.x8": "×8 Переработка под давлением",
        "tooltip.kontur.hard_slag": "Твёрдый шлак: остаётся после экстрактора, в нём ещё есть металл. Аттритор и автоклав (ступень ×8, переработка под давлением) дадут из него ещё три слитка",
        "jei.kontur.info.hard_slag": "Твёрдый шлак остаётся после экстрактора (ступень ×5). Ступень ×8 «Переработка под давлением» делает из него три слитка: аттритор измельчает шлак в пыль, а автоклав варит пыль в паре под давлением. Пар делает парогенератор из воды и угля.",
    },
    "en_us": {
        "block.kontur.attritor": "Attritor", "block.kontur.steam_generator": "Steam Generator", "block.kontur.autoclave": "Autoclave",
        "fluid_type.kontur.steam": "Steam",
        "tooltip.kontur.stage.x8": "×8 Pressure Processing",
        "tooltip.kontur.hard_slag": "Hard slag: left over by the extractor and still holds metal. The attritor and autoclave (stage ×8, pressure processing) turn it into three more ingots",
        "jei.kontur.info.hard_slag": "Hard slag is left over by the extractor (stage ×5). Stage ×8, Pressure Processing, turns it into three ingots: the attritor grinds the slag into dust, and the autoclave cooks the dust in steam under pressure. The steam generator makes steam from water and coal.",
    },
}
for me in METALS:
    lang["ru_ru"][f"item.kontur.{me.id}_hard_slag"] = f"Твёрдый шлак ({me.ru})"
    lang["ru_ru"][f"item.kontur.{me.id}_slag_dust"] = f"Шлаковая пыль ({me.ru})"
    lang["en_us"][f"item.kontur.{me.id}_hard_slag"] = f"Hard Slag ({me.en})"
    lang["en_us"][f"item.kontur.{me.id}_slag_dust"] = f"Slag Dust ({me.en})"
for lg, vals in lang.items():
    p = A / f"lang/{lg}.json"
    d = json.loads(p.read_text(), object_pairs_hook=OrderedDict)
    d.update(vals)
    dump(p, d)
print("ok")
