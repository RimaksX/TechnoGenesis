"""Ступень x12: спёкшийся остаток (спрайты), рецепты генератора плазмы, плазменной печи, вакуумного кристаллизатора,
автоклав дополнительно выдаёт спёкшийся остаток; крафт машин, лут, теги, названия."""
import json, sys
from collections import OrderedDict
from pathlib import Path
sys.path.insert(0, '.')
from PIL import Image
import make_forms as F
from kontur_gen.defs import METALS

R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def rl(x):
    return f"kontur:{x}"

# ---------------------------------------------------------------- спрайты: спёкшийся остаток = плотная обожжённая плитка
def sintered(metal):
    old = F.BASES["cake"]
    F.BASES["cake"] = (150, 104, 84)
    try:
        return F.cake(metal)
    finally:
        F.BASES["cake"] = old

for me in METALS:
    sintered(me).save(A / f"textures/item/{me.id}_sintered_residue.png")
    dump(A / f"models/item/{me.id}_sintered_residue.json", {"parent": "minecraft:item/generated",
                                                           "textures": {"layer0": f"kontur:item/{me.id}_sintered_residue"}})

# ---------------------------------------------------------------- рецепты
S12 = dict(
    plasma=dict(energy=20000, time=50, steam=1000, plasma=1000),
    smelt=dict(energy=30000, time=100, plasma=1000, melt=500),
    cast=dict(energy=20000, time=100, melt=500, ingots=4),
)

def res(item, count=1, chance=1.0):
    r = {"id": item, "count": count}
    if chance < 1.0:
        r["chance"] = chance
    return r

def machine_recipe(kind, name, ing, results, energy, time, fluid_in=None, fluid_out=None):
    d = {"type": rl(kind), "results": results, "energy": energy, "time": time}
    if ing:
        d["input"] = {"ingredient": {"item": ing}, "count": 1}
    if fluid_in:
        d["fluid_input"] = fluid_in
    if fluid_out:
        d["fluid_results"] = fluid_out
    dump(D / f"recipe/{kind}/{name}.json", d)

machine_recipe("plasma_generation", "steam", None, [], S12["plasma"]["energy"], S12["plasma"]["time"],
               fluid_in={"fluids": [rl("steam")], "amount": S12["plasma"]["steam"]},
               fluid_out=[{"fluid": rl("plasma"), "amount": S12["plasma"]["plasma"]}])
for me in METALS:
    resid, melt = rl(f"{me.id}_sintered_residue"), rl(f"{me.id}_melt")
    machine_recipe("plasma_smelting", me.id, resid, [res(rl("gangue"), 1, 0.5)], S12["smelt"]["energy"], S12["smelt"]["time"],
                   fluid_in={"fluids": [rl("plasma")], "amount": S12["smelt"]["plasma"]},
                   fluid_out=[{"fluid": melt, "amount": S12["smelt"]["melt"]}])
    machine_recipe("vacuum_casting", me.id, None, [res(me.ingot_item, S12["cast"]["ingots"])],
                   S12["cast"]["energy"], S12["cast"]["time"],
                   fluid_in={"fluids": [melt], "amount": S12["cast"]["melt"]})
    # автоклав: три слитка и спёкшийся остаток своего металла
    p = D / f"recipe/autoclaving/{me.id}.json"
    d = json.loads(p.read_text())
    d["results"] = [res(me.ingot_item, 3), res(resid)]
    dump(p, d)

def shaped(name, pattern, key, result):
    dump(D / f"recipe/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()}, "result": {"id": result, "count": 1}})

shaped("plasma_generator", ["TDT", "RFR", "IWI"],
       {"T": rl("tungsten_ingot"), "D": "minecraft:diamond", "R": "minecraft:redstone_block", "F": rl("machine_frame"),
        "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("plasma_generator"))
shaped("plasma_furnace", ["TBT", "DFD", "IWI"],
       {"T": rl("tungsten_ingot"), "B": "minecraft:blast_furnace", "D": "minecraft:diamond", "F": rl("machine_frame"),
        "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("plasma_furnace"))
shaped("vacuum_caster", ["MGM", "TFT", "IWI"],
       {"M": rl("molybdenum_ingot"), "G": "minecraft:glass", "T": rl("titanium_ingot"), "F": rl("machine_frame"),
        "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("vacuum_caster"))

for mid in ("plasma_generator", "plasma_furnace", "vacuum_caster"):
    dump(D / f"loot_table/blocks/{mid}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": rl(mid)}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": rl(f"blocks/{mid}")})

tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text())
for mid in ("plasma_generator", "plasma_furnace", "vacuum_caster"):
    if rl(mid) not in t["values"]:
        t["values"].append(rl(mid))
t["values"].sort()
dump(tag, t)

lang = {
    "ru_ru": {
        "block.kontur.plasma_generator": "Генератор плазмы", "block.kontur.plasma_furnace": "Плазменная печь",
        "block.kontur.vacuum_caster": "Вакуумный кристаллизатор",
        "fluid_type.kontur.plasma": "Плазма",
        "tooltip.kontur.stage.x12": "×12 Плазменная переработка",
        "tooltip.kontur.sintered_residue": "Спёкшийся остаток: остаётся после автоклава, в нём ещё есть металл. Генератор плазмы, плазменная печь и вакуумный кристаллизатор (ступень ×12, плазменная переработка) дадут из него ещё четыре слитка",
        "jei.kontur.info.sintered_residue": "Спёкшийся остаток выпадает из автоклава (ступень ×8). Ступень ×12 «Плазменная переработка» делает из него четыре слитка: плазменная печь плавит остаток в плазме (плазму делает генератор плазмы из пара) и получает расплав металла, а вакуумный кристаллизатор отливает из расплава слитки.",
    },
    "en_us": {
        "block.kontur.plasma_generator": "Plasma Generator", "block.kontur.plasma_furnace": "Plasma Furnace",
        "block.kontur.vacuum_caster": "Vacuum Caster",
        "fluid_type.kontur.plasma": "Plasma",
        "tooltip.kontur.stage.x12": "×12 Plasma Processing",
        "tooltip.kontur.sintered_residue": "Sintered residue: left over by the autoclave and still holds metal. The plasma generator, plasma furnace and vacuum caster (stage ×12, plasma processing) turn it into four more ingots",
        "jei.kontur.info.sintered_residue": "Sintered residue drops out of the autoclave (stage ×8). Stage ×12, Plasma Processing, turns it into four ingots: the plasma furnace melts the residue in plasma (the plasma generator makes plasma from steam) to get molten metal, and the vacuum caster casts ingots from the melt.",
    },
}
for me in METALS:
    lang["ru_ru"][f"item.kontur.{me.id}_sintered_residue"] = f"Спёкшийся остаток ({me.ru})"
    lang["en_us"][f"item.kontur.{me.id}_sintered_residue"] = f"Sintered Residue ({me.en})"
    lang["ru_ru"][f"fluid_type.kontur.{me.id}_melt"] = f"Расплав ({me.ru})"
    lang["en_us"][f"fluid_type.kontur.{me.id}_melt"] = f"Melt ({me.en.lower()})"
for lg, vals in lang.items():
    p = A / f"lang/{lg}.json"
    d = json.loads(p.read_text(), object_pairs_hook=OrderedDict)
    d.update(vals)
    dump(p, d)
print("ok")
