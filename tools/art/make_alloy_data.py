"""Этап сплавов: рецепты сплавной печи и слитков, правки старых рецептов под сплавы, лут, теги, язык."""
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

def alloy(name, a, na, b, nb, out, nout, energy):
    wj(RC / "alloying" / f"{name}.json", {
        "type": K + "alloying", "results": [{"id": K + out, "count": nout}], "energy": energy, "time": 100,
        "input": {"ingredient": item(a), "count": na}, "input_b": {"ingredient": item(b), "count": nb}})

alloy("steel", "iron_ingot", 2, K + "graphite", 1, "steel_ingot", 2, 12000)
alloy("stainless_steel", K + "steel_ingot", 2, K + "chromium_ingot", 1, "stainless_steel_ingot", 2, 18000)
alloy("tungsten_carbide", K + "tungsten_ingot", 2, K + "graphite", 1, "tungsten_carbide_ingot", 2, 24000)
alloy("titanium_alloy", K + "titanium_ingot", 2, K + "aluminum_ingot", 1, "titanium_alloy_ingot", 2, 20000)
alloy("magnetic_alloy", K + "cobalt_ingot", 2, K + "nickel_ingot", 1, "magnetic_alloy_ingot", 2, 18000)
alloy("nichrome", K + "nickel_ingot", 2, K + "chromium_ingot", 1, "nichrome_ingot", 2, 15000)

def shaped(name, pattern, key, result, count=1):
    wj(RC / f"{name}.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
                             "key": {k: item(v) for k, v in key.items()}, "result": {"id": result, "count": count}})

shaped("alloy_furnace", ["BGB", "WFW", "DCD"], {"B": "bricks", "G": K + "graphite", "W": K + "winding",
       "F": K + "machine_frame", "D": K + "gear_drive", "C": K + "control_circuit"}, K + "alloy_furnace")

# старые рецепты: сталь и сплавы вместо чистых металлов
def patch(name, repl):
    p = RC / f"{name}.json"
    s = p.read_text(encoding="utf8")
    for a, b in repl.items():
        assert a in s, (name, a)
        s = s.replace(a, b)
    p.write_text(s, encoding="utf8")

patch("drill_tip_steel", {"kontur:chromium_ingot": "kontur:steel_ingot"})
patch("drill_tip_carbide", {"kontur:tungsten_ingot": "kontur:tungsten_carbide_ingot"})
patch("armored_cable", {"minecraft:iron_ingot": "kontur:steel_ingot"})

# лут и тег кирки
loot = json.loads((R / "data/kontur/loot_table/blocks/settling_tank.json").read_text(encoding="utf8"))
(R / "data/kontur/loot_table/blocks/alloy_furnace.json").write_text(
    json.dumps(loot, ensure_ascii=False, indent=2).replace("settling_tank", "alloy_furnace") + "\n", encoding="utf8")
tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text(encoding="utf8"))
if "kontur:alloy_furnace" not in t["values"]:
    t["values"].append("kontur:alloy_furnace")
t["values"].sort()
tag.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

RU = {"block.kontur.alloy_furnace": "Сплавная печь", "tooltip.kontur.stage.alloy": "Сплавы",
      "item.kontur.steel_ingot": "Стальной слиток", "item.kontur.stainless_steel_ingot": "Слиток нержавеющей стали",
      "item.kontur.tungsten_carbide_ingot": "Слиток твёрдого сплава", "item.kontur.titanium_alloy_ingot": "Слиток титанового сплава",
      "item.kontur.magnetic_alloy_ingot": "Слиток магнитного сплава", "item.kontur.nichrome_ingot": "Слиток нихрома"}
EN = {"block.kontur.alloy_furnace": "Alloy Furnace", "tooltip.kontur.stage.alloy": "Alloys",
      "item.kontur.steel_ingot": "Steel Ingot", "item.kontur.stainless_steel_ingot": "Stainless Steel Ingot",
      "item.kontur.tungsten_carbide_ingot": "Tungsten Carbide Ingot", "item.kontur.titanium_alloy_ingot": "Titanium Alloy Ingot",
      "item.kontur.magnetic_alloy_ingot": "Magnetic Alloy Ingot", "item.kontur.nichrome_ingot": "Nichrome Ingot"}
for f, tbl in (("ru_ru.json", RU), ("en_us.json", EN)):
    p = L / f
    d = json.loads(p.read_text(encoding="utf8"))
    d.update(tbl)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
