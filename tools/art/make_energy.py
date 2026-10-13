"""Ресурсы энергетики: покрытия панелей (текстуры, модели), названия, рецепты, лут, теги."""
import json
from collections import OrderedDict
from pathlib import Path
from PIL import Image

R = Path("/home/user/TechnoGenesis/src/main/resources")
A = R / "assets/kontur"
D = R / "data/kontur"

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------------- покрытия: пластина с сеткой элементов
OUT = (20, 24, 34)
COATS = {
    "coating_basic": ((30, 44, 104), (58, 84, 166), (116, 146, 226), (170, 190, 245)),
    "coating_aluminum": ((78, 88, 104), (136, 148, 166), (200, 210, 226), (240, 245, 252)),
    "coating_gold": ((130, 84, 16), (206, 148, 30), (250, 206, 70), (255, 240, 160)),
}
MASK = [
    "................",
    "................",
    "..oooooooooooo..",
    ".ohhhhhhhhhhhho.",
    ".ohmmmmmmmmmmdo.",
    ".ohmgmmgmmgmmdo.",
    ".ohmmmmmmmmmmdo.",
    ".ohmgmmgmmgmmdo.",
    ".ohmmmmmmmmmmdo.",
    ".ohmgmmgmmgmmdo.",
    ".ohmmmmmmmmmmdo.",
    ".oddddddddddddo.",
    "..oooooooooooo..",
    "................",
    "................",
    "................",
]
for name, (dark, mid, light, hi) in COATS.items():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pal = {"o": OUT, "d": dark, "m": mid, "h": light, "g": hi}
    for y, row in enumerate(MASK):
        for x, c in enumerate(row):
            if c in pal:
                im.putpixel((x, y), (*pal[c], 255))
    # перелив: чуть темнее вниз
    im.save(A / f"textures/item/{name}.png")
    dump(A / f"models/item/{name}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"kontur:item/{name}"}})

# ---------------------------------------------------------------- лут, теги
NEW_BLOCKS = ["wind_rotor", "thermal_generator", "steam_turbine", "solar_panel", "solar_panel_advanced", "solar_farm"]
for id_ in NEW_BLOCKS:
    dump(D / f"loot_table/blocks/{id_}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": f"kontur:{id_}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": f"kontur:blocks/{id_}"})
tag = R / "data/minecraft/tags/block/mineable/pickaxe.json"
t = json.loads(tag.read_text())
for id_ in NEW_BLOCKS:
    if f"kontur:{id_}" not in t["values"]:
        t["values"].append(f"kontur:{id_}")
t["values"].sort()
dump(tag, t)

# ---------------------------------------------------------------- рецепты
def shaped(name, pattern, key, result, count=1):
    dump(D / f"recipe/{name}.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
                                      "key": {k: {"item": v} for k, v in key.items()},
                                      "result": {"id": f"kontur:{result}", "count": count}})

def shapeless(name, ingredients, result, count=1):
    dump(D / f"recipe/{name}.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                      "ingredients": [{"item": i} for i in ingredients],
                                      "result": {"id": f"kontur:{result}", "count": count}})

F = "kontur:machine_frame"
W = "kontur:copper_wire"
shaped("wind_rotor", ["III", "IFI", "RWR"], {"I": "minecraft:iron_ingot", "F": F, "R": "minecraft:redstone", "W": W}, "wind_rotor")
shaped("thermal_generator", ["IMI", "CFC", "RWR"], {"I": "minecraft:iron_ingot", "M": "minecraft:magma_block", "C": "minecraft:copper_ingot",
                                                    "F": F, "R": "minecraft:redstone", "W": W}, "thermal_generator")
shaped("steam_turbine", ["IKI", "CFC", "RWR"], {"I": "minecraft:iron_ingot", "K": "minecraft:cauldron", "C": "minecraft:copper_ingot",
                                                "F": F, "R": "minecraft:redstone", "W": W}, "steam_turbine")
shaped("solar_panel", ["GGG", "CRC", "IFI"], {"G": "minecraft:glass", "C": "minecraft:copper_ingot", "R": "minecraft:redstone",
                                              "I": "minecraft:iron_ingot", "F": F}, "solar_panel")
shaped("solar_panel_advanced", ["QQQ", "BFB", "IWI"], {"Q": "minecraft:quartz", "B": "kontur:solar_panel", "F": F,
                                                       "I": "minecraft:iron_ingot", "W": W}, "solar_panel_advanced")
shaped("solar_farm", ["AAA", "AAA", "IFI"], {"A": "kontur:solar_panel_advanced", "I": "minecraft:iron_ingot", "F": F}, "solar_farm")
shaped("coating_basic", ["GQG", "QLQ", "GQG"], {"G": "minecraft:glass", "Q": "minecraft:quartz", "L": "minecraft:lapis_lazuli"},
       "coating_basic", 1)
shapeless("coating_aluminum", ["kontur:coating_basic", "kontur:aluminum_ingot", "kontur:aluminum_ingot"], "coating_aluminum")
shapeless("coating_gold", ["kontur:coating_aluminum", "minecraft:gold_ingot", "minecraft:gold_ingot", "minecraft:gold_ingot"],
          "coating_gold")

# ---------------------------------------------------------------- названия
ru = {
    "block.kontur.wind_rotor": "Ветряной ротор", "block.kontur.thermal_generator": "Тепловой генератор",
    "block.kontur.steam_turbine": "Паровая турбина", "block.kontur.solar_panel": "Солнечная панель",
    "block.kontur.solar_panel_advanced": "Улучшенная солнечная панель", "block.kontur.solar_farm": "Солнечная ферма",
    "item.kontur.coating_basic": "Кремниевое покрытие", "item.kontur.coating_aluminum": "Алюминиевое покрытие",
    "item.kontur.coating_gold": "Золотое покрытие",
    "status.kontur.no_sky": "Небо закрыто", "status.kontur.no_sun": "Нет солнечного света",
    "status.kontur.no_heat": "Нужна лава снизу и вода сбоку", "status.kontur.no_water": "Нет воды",
    "status.kontur.full": "Буфер заполнен",
    "gui.kontur.gen_peak": "Базовая выработка: %s FE/t", "gui.kontur.coating_slot": "Слот покрытия панели",
    "gui.kontur.coating_line": "%s: %s%% выработки",
    "tooltip.kontur.coating.efficiency": "Выработка панели: %s%%",
    "tooltip.kontur.coating.hint": "Ставится в слот покрытия улучшенной панели или солнечной фермы",
    "message.kontur.farm_no_space": "Для солнечной фермы нужно свободное место 3x2",
}
en = {
    "block.kontur.wind_rotor": "Wind Rotor", "block.kontur.thermal_generator": "Thermal Generator",
    "block.kontur.steam_turbine": "Steam Turbine", "block.kontur.solar_panel": "Solar Panel",
    "block.kontur.solar_panel_advanced": "Advanced Solar Panel", "block.kontur.solar_farm": "Solar Farm",
    "item.kontur.coating_basic": "Silicon Coating", "item.kontur.coating_aluminum": "Aluminum Coating",
    "item.kontur.coating_gold": "Gold Coating",
    "status.kontur.no_sky": "Sky is blocked", "status.kontur.no_sun": "No sunlight",
    "status.kontur.no_heat": "Needs lava below and water beside", "status.kontur.no_water": "No water",
    "status.kontur.full": "Buffer full",
    "gui.kontur.gen_peak": "Base output: %s FE/t", "gui.kontur.coating_slot": "Panel coating slot",
    "gui.kontur.coating_line": "%s: %s%% output",
    "tooltip.kontur.coating.efficiency": "Panel output: %s%%",
    "tooltip.kontur.coating.hint": "Goes into the coating slot of the advanced panel or the solar farm",
    "message.kontur.farm_no_space": "The solar farm needs a free 3x2 area",
}
for lg, vals in (("ru_ru", ru), ("en_us", en)):
    p = A / f"lang/{lg}.json"
    d = json.loads(p.read_text(), object_pairs_hook=OrderedDict)
    d.update(vals)
    dump(p, d)
print("ok")
