"""Ступень x5: рецепты (экстракция, электролиз, регенерация растворителя, растворитель в заводе кислоты), крафт машин,
лут, теги и названия. Остальные рецепты репозитория не трогаются."""
import json
from collections import OrderedDict
from pathlib import Path
import sys
sys.path.insert(0, '.')
from kontur_gen.defs import METALS

R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def rl(x):
    return f"kontur:{x}"

# Суммарно 24 000 FE на единицу сырья: экстракция 8 000 + электролиз 14 400 + регенерация растворителя 1 920 (с запасом на потери).
S5 = dict(
    extract=dict(energy=8000, time=125, solvent=500, extract=400, waste_chance=0.5),
    electro=dict(energy=14400, time=100, extract=400, ingots=2, spent=400),
    regen=dict(energy=1920, time=30, spent=500, solvent=400, salt_chance=0.25),
    solvent=dict(energy=1920, time=60, acid=250, solvent=500),
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
    cake = rl(f"{me.id}_cake_r2")
    ext = rl(f"{me.id}_extract")
    machine_recipe("extraction", me.id, cake, [res(rl(f"{me.id}_hard_slag"))],
                   S5["extract"]["energy"], S5["extract"]["time"],
                   fluid_in={"fluids": [rl("solvent")], "amount": S5["extract"]["solvent"]},
                   fluid_out=[{"fluid": ext, "amount": S5["extract"]["extract"]}])
    machine_recipe("electrolysis", me.id, None, [res(me.ingot_item, S5["electro"]["ingots"])],
                   S5["electro"]["energy"], S5["electro"]["time"],
                   fluid_in={"fluids": [ext], "amount": S5["electro"]["extract"]},
                   fluid_out=[{"fluid": rl("spent_solvent"), "amount": S5["electro"]["spent"]}])

machine_recipe("solvent_regeneration", "spent_solvent", None, [res(rl("salt"), 1, S5["regen"]["salt_chance"])],
               S5["regen"]["energy"], S5["regen"]["time"],
               fluid_in={"fluids": [rl("spent_solvent")], "amount": S5["regen"]["spent"]},
               fluid_out=[{"fluid": rl("solvent"), "amount": S5["regen"]["solvent"]}])
# растворитель делается в заводе кислоты: уголь (или древесный уголь) и серная кислота, т. е. в конечном счёте сера и уголь
for coal in ("coal", "charcoal"):
    machine_recipe("acid_synthesis", f"solvent_from_{coal}", f"minecraft:{coal}", [],
                   S5["solvent"]["energy"], S5["solvent"]["time"],
                   fluid_in={"fluids": [rl("sulfuric_acid")], "amount": S5["solvent"]["acid"]},
                   fluid_out=[{"fluid": rl("solvent"), "amount": S5["solvent"]["solvent"]}])

def shaped(name, pattern, key, result):
    dump(D / f"recipe/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()}, "result": {"id": result, "count": 1}})

shaped("extractor", ["GBG", "HFH", "IWI"],
       {"G": "minecraft:glass", "B": "minecraft:bucket", "H": "minecraft:hopper", "F": rl("machine_frame"),
        "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("extractor"))
shaped("electrolyzer", ["GCG", "RFR", "IWI"],
       {"G": rl("graphite"), "C": "minecraft:copper_ingot", "R": "minecraft:redstone", "F": rl("machine_frame"),
        "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("electrolyzer"))
shaped("solvent_regenerator", ["BKB", "HFH", "IWI"],
       {"B": "minecraft:bricks", "K": "minecraft:furnace", "H": "minecraft:hopper", "F": rl("machine_frame"),
        "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("solvent_regenerator"))

for mid in ("extractor", "electrolyzer", "solvent_regenerator"):
    dump(D / f"loot_table/blocks/{mid}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": rl(mid)}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": rl(f"blocks/{mid}")})

tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text())
for mid in ("extractor", "electrolyzer", "solvent_regenerator"):
    if rl(mid) not in t["values"]:
        t["values"].append(rl(mid))
t["values"].sort()
dump(tag, t)

lang = {
    "ru_ru": {
        "block.kontur.extractor": "Экстрактор", "block.kontur.electrolyzer": "Электролизёр",
        "block.kontur.solvent_regenerator": "Регенератор растворителя",
        "fluid_type.kontur.solvent": "Растворитель", "fluid_type.kontur.spent_solvent": "Отработанный растворитель",
    },
    "en_us": {
        "block.kontur.extractor": "Extractor", "block.kontur.electrolyzer": "Electrolyzer",
        "block.kontur.solvent_regenerator": "Solvent Regenerator",
        "fluid_type.kontur.solvent": "Solvent", "fluid_type.kontur.spent_solvent": "Spent Solvent",
    },
}
for me in METALS:
    lang["ru_ru"][f"fluid_type.kontur.{me.id}_extract"] = f"Экстракт ({me.ru})"
    lang["en_us"][f"fluid_type.kontur.{me.id}_extract"] = f"Extract ({me.en.lower()})"
for lg, vals in lang.items():
    p = A / f"lang/{lg}.json"
    d = json.loads(p.read_text(), object_pairs_hook=OrderedDict)
    d.update(vals)
    dump(p, d)
print("ok", sum(1 for _ in (D / "recipe").rglob("*.json")))
