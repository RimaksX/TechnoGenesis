"""Этап газов: рецепты (разделитель воды, кислородное дутьё автоклава, водородная плазма, трубы, машина), лут, теги, язык."""
import json
from pathlib import Path
R = Path("/home/user/TechnoGenesis/src/main/resources")
RC = R / "data/kontur/recipe"
L = R / "assets/kontur/lang"
K = "kontur:"

def wj(path, d):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

def item(i):
    return {"item": i if ":" in i else "minecraft:" + i}

def shaped(name, pattern, key, result, count=1):
    wj(RC / f"{name}.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
                             "key": {k: item(v) for k, v in key.items()}, "result": {"id": result, "count": count}})

# водный разделитель: вода или техническая вода -> водород и кислород
wj(RC / "water_splitting/water.json", {
    "type": K + "water_splitting", "results": [], "energy": 19200, "time": 100,
    "fluid_input": {"fluids": ["minecraft:water", K + "technical_water"], "amount": 1000},
    "fluid_results": [{"fluid": K + "hydrogen", "amount": 1000}, {"fluid": K + "oxygen", "amount": 500}]})

# автоклав: кислородное дутьё вместо пара даёт на слиток больше
for f in sorted((RC / "autoclaving").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf8"))
    if "sintering" in f.stem or "oxygen" in f.stem:
        continue
    d["fluid_input"] = {"fluids": [K + "oxygen"], "amount": 500}
    d["results"][0]["count"] += 1
    wj(RC / "autoclaving" / f"{f.stem}_oxygen.json", d)

# генератор плазмы: водород дешевле пара
wj(RC / "plasma_generation/plasma_from_hydrogen.json", {
    "type": K + "plasma_generation", "results": [], "energy": 14000, "time": 50,
    "fluid_input": {"fluids": [K + "hydrogen"], "amount": 500},
    "fluid_results": [{"fluid": K + "plasma", "amount": 1000}]})

# трубы и машина
shaped("gas_pipe", ["III", "V V", "III"], {"I": K + "steel_ingot", "V": K + "valve_block"}, K + "gas_pipe", 6)
shaped("gas_pipe_heavy", ["TPT", "PRP", "TPT"], {"T": K + "titanium_alloy_ingot", "P": K + "gas_pipe", "R": "redstone_block"},
       K + "gas_pipe_heavy", 4)
shaped("water_splitter", ["GNG", "GFG", "WCV"], {"G": K + "graphite", "N": K + "nickel_ingot", "F": K + "machine_frame",
       "W": K + "winding", "C": K + "control_circuit", "V": K + "valve_block"}, K + "water_splitter")

shaped("hydrogen_generator", ["IKI", "WFW", "DVC"], {"I": "iron_ingot", "K": "bucket", "W": K + "winding",
       "F": K + "machine_frame", "D": K + "gear_drive", "V": K + "valve_block", "C": K + "control_circuit"},
       K + "hydrogen_generator")

# лут и тег кирки для машины
loot = json.loads((R / "data/kontur/loot_table/blocks/plasma_generator.json").read_text(encoding="utf8"))
txt = json.dumps(loot, ensure_ascii=False, indent=2).replace("plasma_generator", "water_splitter")
(R / "data/kontur/loot_table/blocks/water_splitter.json").write_text(txt + "\n", encoding="utf8")
(R / "data/kontur/loot_table/blocks/hydrogen_generator.json").write_text(
    json.dumps(loot, ensure_ascii=False, indent=2).replace("plasma_generator", "hydrogen_generator") + "\n", encoding="utf8")
tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text(encoding="utf8"))
for id_ in ("water_splitter", "hydrogen_generator"):
    if f"kontur:{id_}" not in t["values"]:
        t["values"].append(f"kontur:{id_}")
t["values"].sort()
tag.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

# язык
RU = {"block.kontur.water_splitter": "Разделитель воды", "block.kontur.hydrogen_generator": "Водородный генератор", "fluid_type.kontur.hydrogen": "Водород",
      "fluid_type.kontur.oxygen": "Кислород", "tooltip.kontur.stage.gas": "Газы"}
EN = {"block.kontur.water_splitter": "Water Splitter", "block.kontur.hydrogen_generator": "Hydrogen Generator", "fluid_type.kontur.hydrogen": "Hydrogen",
      "fluid_type.kontur.oxygen": "Oxygen", "tooltip.kontur.stage.gas": "Gases"}
for f, tbl in (("ru_ru.json", RU), ("en_us.json", EN)):
    p = L / f
    d = json.loads(p.read_text(encoding="utf8"))
    d.update(tbl)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
