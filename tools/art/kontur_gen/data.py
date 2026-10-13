"""Генерация JSON: модели, blockstates, язык, рецепты, лут, теги, генерация мира."""
import json
from pathlib import Path
from .defs import *

import os
ROOT = Path(os.environ.get("KONTUR_ROOT", "/home/user/TechnoGenesis"))
RES = ROOT / "src/main/resources"
ASSETS = RES / "assets" / MODID
DATA = RES / "data" / MODID
MC_TAGS = RES / "data" / "minecraft" / "tags"
C_TAGS = RES / "data" / "c" / "tags"


def wj(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rl(path):
    return f"{MODID}:{path}"


# ---------------------------------------------------------------- реестр id

MACHINES = {
    # id: (ru, en, анимированный фронт, ступень)
    "jaw_crusher": ("Щёковая дробилка", "Jaw Crusher"),
    "washing_drum": ("Вращающийся промывочный барабан", "Rotary Washing Drum"),
    "magnetic_separator": ("Магнитно-плотностной сепаратор", "Magnetic Density Separator"),
    "settling_tank": ("Отстойник", "Settling Tank"),
    "solid_fuel_generator": ("Твердотопливный электрогенератор", "Solid Fuel Generator"),
    "carbon_capacitor": ("Углеродный конденсатор", "Carbon Capacitor"),
    "tailings_mill": ("Роторная мельница остатков", "Rotary Remnant Mill"),
    "acid_plant": ("Завод серной кислоты", "Sulfuric Acid Plant"),
    "leaching_reactor": ("Реактор выщелачивания", "Leaching Reactor"),
    "filter_press": ("Промышленный фильтр-пресс", "Industrial Filter Press"),
    "precipitation_reactor": ("Осадительный реактор", "Precipitation Reactor"),
    "acid_regeneration_column": ("Колонна регенерации кислот", "Acid Regeneration Column"),
}
ANIMATED = ["jaw_crusher", "washing_drum", "magnetic_separator", "settling_tank", "tailings_mill", "acid_plant",
            "leaching_reactor", "filter_press", "precipitation_reactor", "acid_regeneration_column"]
CAPACITOR_LEVELS = 6  # charge 0..5

FORMS = [
    ("crushed_ore", "Дроблёная руда", "Crushed Ore"),
    ("washed_ore", "Промытая руда", "Washed Ore"),
    ("concentrate", "Концентрат", "Concentrate"),
    ("tailings_r1", "Рудный остаток", "Ore Remnants"),
    ("fine_tailings", "Рудная пыль", "Ore Dust"),
    ("wet_cake", "Кислотная масса", "Acid Slurry"),
    ("cake_r2", "Сухой остаток", "Dry Residue"),
    ("precipitate", "Металлический осадок", "Metal Sediment"),
    ("hard_slag", "Твёрдый шлак", "Hard Slag"),
    ("slag_dust", "Шлаковая пыль", "Slag Dust"),
    ("sintered_residue", "Спёкшийся остаток", "Sintered Residue"),
]

MISC_ITEMS = {
    "gangue": ("Щебень пустой породы", "Gangue Rubble"),
    "ash": ("Зола", "Ash"),
    "wet_sludge": ("Мокрый осадок", "Wet Sludge"),
    "mineral_fraction": ("Минеральная фракция", "Mineral Fraction"),
    "salt": ("Техническая соль", "Technical Salt"),
    "sulfur_powder": ("Серный порошок", "Sulfur Powder"),
    "crushed_spodumene": ("Дроблёный сподумен", "Crushed Spodumene"),
    "graphite": ("Графит", "Graphite"),
    "machine_frame": ("Рама механизма", "Machine Frame"),
}

METAL_RU_GEN = {  # родительный падеж для названий форм не нужен, используем скобки
}


def ore_blocks():
    """[(block_id, ru, en, mineral, kind)] kind: stone|deepslate|nether"""
    out = []
    for m in MINERALS:
        out.append((m.ore_id, m.ore_ru, m.ore_en, m, "stone"))
        out.append((f"deepslate_{m.ore_id}", m.deep_ru, f"Deepslate {m.ore_en}", m, "deepslate"))
        if m.nether:
            out.append((f"nether_{m.ore_id}", "Адская " + m.ore_ru[0].lower() + m.ore_ru[1:] if False else
                        "Нижняя руда самородной серы", f"Nether {m.ore_en}", m, "nether"))
    return out


def all_block_ids():
    ids = [b[0] for b in ore_blocks()]
    ids += ["ash_block", "aggregate_block", "copper_wire"]
    ids += list(MACHINES)
    return ids


# ---------------------------------------------------------------- модели

def cube_all(tex):
    return {"parent": "minecraft:block/cube_all", "textures": {"all": rl(f"block/{tex}")}}


def item_generated(tex):
    return {"parent": "minecraft:item/generated", "textures": {"layer0": rl(f"item/{tex}")}}


def simple_block(bid, tex=None):
    wj(ASSETS / f"models/block/{bid}.json", cube_all(tex or bid))
    wj(ASSETS / f"blockstates/{bid}.json", {"variants": {"": {"model": rl(f"block/{bid}")}}})
    wj(ASSETS / f"models/item/{bid}.json", {"parent": rl(f"block/{bid}")})


ROT = {"north": 0, "east": 90, "south": 180, "west": 270}


def machine_models():
    for mid in MACHINES:
        side = "carbon_side" if mid == "carbon_capacitor" else "machine_side"
        bottom = "carbon_side" if mid == "carbon_capacitor" else "machine_bottom"

        def model(front):
            return {"parent": "minecraft:block/orientable_with_bottom",
                    "textures": {"top": rl(f"block/{mid}_top"), "bottom": rl(f"block/{bottom}"),
                                 "side": rl(f"block/{side}"), "front": rl(f"block/{front}")}}

        variants = {}
        if mid == "carbon_capacitor":
            for lvl in range(CAPACITOR_LEVELS):
                wj(ASSETS / f"models/block/{mid}_{lvl}.json", model(f"{mid}_front_{lvl}"))
                for f, y in ROT.items():
                    v = {"model": rl(f"block/{mid}_{lvl}")}
                    if y:
                        v["y"] = y
                    variants[f"facing={f},charge={lvl}"] = v
            wj(ASSETS / f"models/item/{mid}.json", {"parent": rl(f"block/{mid}_0")})
        else:
            wj(ASSETS / f"models/block/{mid}.json", model(f"{mid}_front"))
            wj(ASSETS / f"models/block/{mid}_on.json", model(f"{mid}_front_on"))
            for act in ("false", "true"):
                for f, y in ROT.items():
                    v = {"model": rl(f"block/{mid}" + ("_on" if act == "true" else ""))}
                    if y:
                        v["y"] = y
                    variants[f"facing={f},active={act}"] = v
            wj(ASSETS / f"models/item/{mid}.json", {"parent": rl(f"block/{mid}")})
        wj(ASSETS / f"blockstates/{mid}.json", {"variants": variants})


def cable_models():
    tex = {"wire": rl("block/copper_wire"), "particle": rl("block/copper_wire")}

    def face(t="#wire"):
        return {"texture": t}

    def cuboid(frm, to, uv_all=True):
        faces = {d: {"texture": "#wire", "uv": [0, 0, 16, 16] if False else None} for d in
                 ("north", "south", "east", "west", "up", "down")}
        for d in faces:
            faces[d] = {"texture": "#wire"}
        return {"from": frm, "to": to, "faces": faces}

    wj(ASSETS / "models/block/copper_wire_core.json",
       {"textures": tex, "elements": [cuboid([5, 5, 5], [11, 11, 11])]})
    wj(ASSETS / "models/block/copper_wire_side.json",
       {"textures": tex, "elements": [cuboid([5.5, 5.5, 0], [10.5, 10.5, 5])]})
    wj(ASSETS / "models/block/copper_wire_inventory.json",
       {"textures": tex, "display": {
           "gui": {"rotation": [30, 225, 0], "scale": 0.9},
           "fixed": {"scale": 0.9}, "ground": {"scale": 0.6, "translation": [0, 3, 0]},
           "thirdperson_righthand": {"rotation": [75, 45, 0], "scale": 0.5, "translation": [0, 2.5, 0]},
           "firstperson_righthand": {"rotation": [0, 45, 0], "scale": 0.5}},
        "elements": [cuboid([5, 5, 5], [11, 11, 11]),
                     cuboid([0, 5.5, 5.5], [5, 10.5, 10.5]),
                     cuboid([11, 5.5, 5.5], [16, 10.5, 10.5])]})
    rot = {"north": {}, "east": {"y": 90}, "south": {"y": 180}, "west": {"y": 270},
           "up": {"x": 270}, "down": {"x": 90}}
    mp = [{"apply": {"model": rl("block/copper_wire_core")}}]
    for d, r in rot.items():
        a = {"model": rl("block/copper_wire_side"), **r}
        mp.append({"when": {d: "true"}, "apply": a})
    wj(ASSETS / "blockstates/copper_wire.json", {"multipart": mp})
    wj(ASSETS / "models/item/copper_wire.json", {"parent": rl("block/copper_wire_inventory")})


# ---------------------------------------------------------------- язык

def lang():
    ru, en = {}, {}

    def both(key, r, e):
        ru[key], en[key] = r, e

    both("itemGroup.kontur", "Контур", "Kontur")
    for bid, r, e, m, kind in ore_blocks():
        both(f"block.{MODID}.{bid}", r, e)
    for m in NEW_METALS:
        both(f"block.{MODID}.{m.id}_block", m.ru_block, f"Block of {m.en}")
        both(f"item.{MODID}.{m.id}_ingot", f"{m.ru_adj} слиток", f"{m.en} Ingot")
    both(f"block.{MODID}.ash_block", "Зольный блок", "Ash Block")
    both(f"block.{MODID}.aggregate_block", "Блок заполнителя", "Aggregate Block")
    both(f"block.{MODID}.copper_wire", "Медный провод", "Copper Wire")
    for mid, (r, e) in MACHINES.items():
        both(f"block.{MODID}.{mid}", r, e)
    for m in MINERALS:
        both(f"item.{MODID}.{m.raw_id}", m.raw_ru, m.raw_en)
    for me in METALS:
        both(f"metal.{MODID}.{me.id}", me.ru, me.en.lower())
        for fid, fr, fe in FORMS:
            both(f"item.{MODID}.{me.id}_{fid}", f"{fr} ({me.ru})", f"{fe} ({me.en})")
    for iid, (r, e) in MISC_ITEMS.items():
        both(f"item.{MODID}.{iid}", r, e)
    for me in METALS:
        both(f"fluid_type.{MODID}.{me.id}_solution", f"Раствор ({me.ru})", f"Solution ({me.en.lower()})")
    for fid, f in FLUIDS.items():
        both(f"fluid_type.{MODID}.{fid}", f["ru"], f["en"])
        both(f"block.{MODID}.{fid}", f["ru"], f["en"])
        both(f"item.{MODID}.{fid}_bucket", f["bucket_ru"], f["bucket_en"])

    # интерфейс
    g = [
        ("gui.kontur.energy", "Энергия", "Energy"),
        ("gui.kontur.energy_value", "%s / %s FE", "%s / %s FE"),
        ("gui.kontur.energy_rate", "до %s FE/t", "up to %s FE/t"),
        ("gui.kontur.generating", "Выработка: %s FE/t", "Generating: %s FE/t"),
        ("gui.kontur.fluid_empty", "Пусто", "Empty"),
        ("gui.kontur.fluid_value", "%s: %s / %s мБ", "%s: %s / %s mB"),
        ("gui.kontur.progress", "Прогресс: %s%%", "Progress: %s%%"),
        ("gui.kontur.config", "Настройка сторон", "Side configuration"),
        ("gui.kontur.config.title", "Стороны", "Sides"),
        ("gui.kontur.config.hint", "ЛКМ - далее, ПКМ - назад", "LMB - next, RMB - previous"),
        ("gui.kontur.side.front", "Передняя", "Front"),
        ("gui.kontur.side.back", "Задняя", "Back"),
        ("gui.kontur.side.left", "Левая", "Left"),
        ("gui.kontur.side.right", "Правая", "Right"),
        ("gui.kontur.side.top", "Верхняя", "Top"),
        ("gui.kontur.side.bottom", "Нижняя", "Bottom"),
        ("gui.kontur.mode.none", "Выключено", "Disabled"),
        ("gui.kontur.mode.input", "Только вход", "Input only"),
        ("gui.kontur.mode.output", "Только выход", "Output only"),
        ("gui.kontur.mode.all", "Вход и выход", "Input and output"),
        ("gui.kontur.type.items", "Предметы", "Items"),
        ("gui.kontur.type.fluids", "Жидкости", "Fluids"),
        ("gui.kontur.type.energy", "Энергия", "Energy"),
        ("gui.kontur.eject.items", "Авто-вывод предметов", "Auto-eject items"),
        ("gui.kontur.eject.fluids", "Авто-вывод жидкостей", "Auto-eject fluids"),
        ("gui.kontur.on", "Вкл", "On"),
        ("gui.kontur.off", "Выкл", "Off"),
        ("gui.kontur.status", "Состояние", "Status"),
        ("gui.kontur.burn", "Горение", "Burning"),
        ("status.kontur.idle", "Ожидание сырья", "Waiting for input"),
        ("status.kontur.running", "Работа", "Running"),
        ("status.kontur.no_energy", "Ожидание энергии", "Waiting for energy"),
        ("status.kontur.no_fluid", "Нехватка жидкости", "Not enough fluid"),
        ("status.kontur.output_full", "Заполнен выход предметов", "Item output is full"),
        ("status.kontur.fluid_output_full", "Заполнен жидкостный выход", "Fluid output is full"),
        ("status.kontur.no_fuel", "Нет топлива", "No fuel"),
        ("status.kontur.full", "Накопитель заполнен", "Storage is full"),
        ("status.kontur.charging", "Накопление", "Storing energy"),
        ("tooltip.kontur.capacitor", "Ёмкость: %s FE", "Capacity: %s FE"),
        ("tooltip.kontur.cable", "Пропускная способность: %s FE/t", "Throughput: %s FE/t"),
        ("tooltip.kontur.stage", "Ступень: %s", "Stage: %s"),
        ("tooltip.kontur.stage.x2", "×2 Механическое обогащение", "×2 Mechanical beneficiation"),
        ("tooltip.kontur.stage.power", "Энергетика", "Power"),
        ("tooltip.kontur.tailings", "Остаток ступени ×2: размолите в мельнице хвостов и выщелочите (ступень ×3)",
         "Stage ×2 residue: grind it in the tailings mill and leach it (stage ×3)"),
        ("tooltip.kontur.cake_r2", "Кек R2: хранится до вторичного выщелачивания (ступень ×5)",
         "R2 cake: keep it for secondary leaching (stage ×5)"),
        ("tooltip.kontur.metal", "Целевой металл: %s", "Target metal: %s"),
        ("jei.kontur.stats", "%s FE · %s с", "%s FE · %s s"),
        ("jei.kontur.chance", "Шанс: %s%%", "Chance: %s%%"),
        ("jei.kontur.info.tailings",
         "Хвосты R1 остаются после сепаратора ступени ×2. Не выбрасывайте их: мельница хвостов, реактор выщелачивания, фильтр-пресс и осадительный реактор (ступень ×3) дают из них ещё один слиток.",
         "R1 tailings are left over by the stage ×2 separator. Do not discard them: the tailings mill, leaching reactor, filter press and precipitation reactor (stage ×3) recover one more ingot from them."),
        ("jei.kontur.info.cake_r2",
         "Кек R2 остаётся после фильтр-пресса. Он нужен для ступени ×5 (вторичное выщелачивание), пока храните его.",
         "R2 cake is left over by the filter press. It feeds stage ×5 (secondary leaching); keep it in storage for now."),
        ("tooltip.kontur.input_hint", "Нужны техническая или обычная вода", "Needs technical or plain water"),
    ]
    for k, r, e in g:
        both(k, r, e)
    return ru, en


# ---------------------------------------------------------------- рецепты

def item_ing(i):
    return {"tag": i[1:]} if i.startswith("#") else {"item": i}


def shaped(name, pattern, key, result, count=1):
    wj(DATA / f"recipe/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
        "key": {k: item_ing(v) for k, v in key.items()},
        "result": {"id": result, "count": count}})


def shapeless(name, ings, result, count=1):
    wj(DATA / f"recipe/{name}.json", {
        "type": "minecraft:crafting_shapeless", "category": "misc",
        "ingredients": [item_ing(i) for i in ings], "result": {"id": result, "count": count}})


def cooking(kind, name, ing, result, xp, time):
    wj(DATA / f"recipe/{name}.json", {
        "type": f"minecraft:{kind}", "category": "misc", "ingredient": item_ing(ing),
        "result": {"id": result}, "experience": xp, "cookingtime": time})


def machine_recipe(kind, name, ing, count, results, energy, time, fluid_in=None, fluid_out=None):
    d = {"type": rl(kind), "results": results, "energy": energy, "time": time}
    if ing:
        d["input"] = {"ingredient": item_ing(ing), "count": count}
    if fluid_in:
        d["fluid_input"] = fluid_in
    if fluid_out:
        d["fluid_results"] = fluid_out
    wj(DATA / f"recipe/{kind}/{name}.json", d)


def res(item, count=1, chance=1.0):
    r = {"id": item, "count": count}
    if chance < 1.0:
        r["chance"] = chance
    return r


def recipes():
    st = STAGE2
    # --- ступень ×2 для всех металлов
    for me in METALS:
        raw = me.raw_item or None
        if not me.vanilla:
            mn = next(m for m in MINERALS if m.metal == me.id)
            raw = rl(mn.raw_id)
        crushed = rl(f"{me.id}_crushed_ore")
        washed = rl(f"{me.id}_washed_ore")
        conc = rl(f"{me.id}_concentrate")
        tail = rl(f"{me.id}_tailings_r1")
        machine_recipe("crushing", f"{me.id}_ore", raw, 1,
                       [res(crushed), res(rl("gangue"), 1, 0.5)], st["crush"]["energy"], st["crush"]["time"])
        machine_recipe("washing", f"{me.id}_ore", crushed, 1,
                       [res(washed), res(rl("wet_sludge"), 1, 0.25)], st["wash"]["energy"], st["wash"]["time"],
                       fluid_in={"fluids": ["minecraft:water", rl("technical_water")], "amount": st["wash"]["water"]},
                       fluid_out=[{"fluid": rl("polluted_water"), "amount": st["wash"]["polluted"]}])
        machine_recipe("separating", f"{me.id}_ore", washed, 1,
                       [res(conc, 2), res(tail), res(rl("mineral_fraction"), 1, 0.5)],
                       st["separate"]["energy"], st["separate"]["time"])
        cooking("smelting", f"smelting/{me.id}_from_concentrate", conc, me.ingot_item, 0.7, 200)
        cooking("blasting", f"blasting/{me.id}_from_concentrate", conc, me.ingot_item, 0.7, 100)
        if not me.vanilla:
            cooking("smelting", f"smelting/{me.id}_from_raw", rl(mn.raw_id), me.ingot_item, 0.7, 200)
            cooking("blasting", f"blasting/{me.id}_from_raw", rl(mn.raw_id), me.ingot_item, 0.7, 100)
            for bid in (mn.ore_id, f"deepslate_{mn.ore_id}"):
                cooking("smelting", f"smelting/{me.id}_from_{bid}", rl(bid), me.ingot_item, 0.7, 200)
                cooking("blasting", f"blasting/{me.id}_from_{bid}", rl(bid), me.ingot_item, 0.7, 100)
            shaped(f"{me.id}_block", ["III", "III", "III"], {"I": rl(f"{me.id}_ingot")}, rl(f"{me.id}_block"))
            shapeless(f"{me.id}_ingot_from_block", [rl(f"{me.id}_block")], rl(f"{me.id}_ingot"), 9)
    # --- неметаллические руды
    for m in MINERALS:
        if m.metal:
            continue
        counts = {"graphite": 1, "salt": 2, "sulfur_powder": 2, "crushed_spodumene": 1}
        if m.id == "graphite":
            cooking("smelting", "smelting/graphite_from_raw", rl(m.raw_id), rl("graphite"), 0.5, 200)
            cooking("blasting", "blasting/graphite_from_raw", rl(m.raw_id), rl("graphite"), 0.5, 100)
            for bid in (m.ore_id, f"deepslate_{m.ore_id}"):
                cooking("smelting", f"smelting/graphite_from_{bid}", rl(bid), rl("graphite"), 0.5, 200)
            continue
        machine_recipe("crushing", f"{m.id}", rl(m.raw_id), 1,
                       [res(rl(m.product), counts[m.product]), res(rl("gangue"), 1, 0.5)],
                       st["crush"]["energy"], st["crush"]["time"])
    # --- отстойник
    machine_recipe("settling", "polluted_water", None, 0, [res(rl("wet_sludge"), 1, 0.25)],
                   st["settle"]["energy"], st["settle"]["time"],
                   fluid_in={"fluids": [rl("polluted_water")], "amount": st["settle"]["polluted"]},
                   fluid_out=[{"fluid": rl("technical_water"), "amount": st["settle"]["technical"]}])
    # --- ступень ×3: химическое извлечение из хвостов R1
    s3 = STAGE3
    water = ["minecraft:water", rl("technical_water")]
    for me in METALS:
        tail, fine = rl(f"{me.id}_tailings_r1"), rl(f"{me.id}_fine_tailings")
        wet, cake = rl(f"{me.id}_wet_cake"), rl(f"{me.id}_cake_r2")
        prec, sol = rl(f"{me.id}_precipitate"), rl(f"{me.id}_solution")
        machine_recipe("milling", me.id, tail, 1, [res(fine), res(rl("mineral_fraction"), 1, 0.3)],
                       s3["mill"]["energy"], s3["mill"]["time"])
        machine_recipe("leaching", me.id, fine, 1, [res(wet)], s3["leach"]["energy"], s3["leach"]["time"],
                       fluid_in={"fluids": [rl("sulfuric_acid")], "amount": s3["leach"]["acid"]},
                       fluid_out=[{"fluid": sol, "amount": s3["leach"]["solution"]}])
        machine_recipe("filtering", me.id, wet, 1, [res(cake)], s3["press"]["energy"], s3["press"]["time"],
                       fluid_out=[{"fluid": sol, "amount": s3["press"]["solution"]}])
        machine_recipe("precipitation", me.id, rl("salt"), 1, [res(prec)], s3["precip"]["energy"],
                       s3["precip"]["time"],
                       fluid_in={"fluids": [sol], "amount": s3["precip"]["solution"]},
                       fluid_out=[{"fluid": rl("spent_acid"), "amount": s3["precip"]["spent"]}])
        cooking("smelting", f"smelting/{me.id}_from_precipitate", prec, me.ingot_item, 0.7, 200)
        cooking("blasting", f"blasting/{me.id}_from_precipitate", prec, me.ingot_item, 0.7, 100)
    machine_recipe("acid_synthesis", "sulfur", rl("sulfur_powder"), 1, [], s3["acid"]["energy"], s3["acid"]["time"],
                   fluid_in={"fluids": water, "amount": s3["acid"]["water"]},
                   fluid_out=[{"fluid": rl("sulfuric_acid"), "amount": s3["acid"]["acid"]}])
    machine_recipe("acid_regeneration", "spent_acid", None, 0, [res(rl("salt"), 1, s3["regen"]["salt_chance"])],
                   s3["regen"]["energy"], s3["regen"]["time"],
                   fluid_in={"fluids": [rl("spent_acid")], "amount": s3["regen"]["spent"]},
                   fluid_out=[{"fluid": rl("sulfuric_acid"), "amount": s3["regen"]["acid"]}])
    # --- ремесло: материалы
    shaped("machine_frame", ["IBI", "B B", "IBI"], {"I": "minecraft:iron_ingot", "B": "minecraft:stone_bricks"},
           rl("machine_frame"), 2)
    shaped("ash_block", ["AA", "AA"], {"A": rl("ash")}, rl("ash_block"))
    shaped("aggregate_block_from_gangue", ["GG", "GG"], {"G": rl("gangue")}, rl("aggregate_block"), 2)
    shaped("aggregate_block_from_fraction", ["GG", "GG"], {"G": rl("mineral_fraction")}, rl("aggregate_block"), 2)
    shapeless("sludge_to_clay", [rl("wet_sludge"), rl("wet_sludge")], "minecraft:clay_ball", 1)
    shaped("copper_wire", ["CCC", "RRR", "CCC"], {"C": "minecraft:copper_ingot", "R": "minecraft:redstone"},
           rl("copper_wire"), 6)
    # --- машины
    shaped("jaw_crusher", ["IPI", "RFR", "IWI"],
           {"I": "minecraft:iron_ingot", "P": "minecraft:piston", "R": "minecraft:redstone",
            "F": rl("machine_frame"), "W": rl("copper_wire")}, rl("jaw_crusher"))
    shaped("washing_drum", ["ICI", "BFB", "IWI"],
           {"I": "minecraft:iron_ingot", "C": "minecraft:cauldron", "B": "minecraft:bucket",
            "F": rl("machine_frame"), "W": rl("copper_wire")}, rl("washing_drum"))
    shaped("magnetic_separator", ["IMI", "RFR", "IWI"],
           {"I": "minecraft:iron_ingot", "M": "minecraft:iron_block", "R": "minecraft:redstone",
            "F": rl("machine_frame"), "W": rl("copper_wire")}, rl("magnetic_separator"))
    shaped("settling_tank", ["GCG", "GFG", "IWI"],
           {"G": "minecraft:glass", "C": "minecraft:cauldron", "F": rl("machine_frame"),
            "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("settling_tank"))
    shaped("solid_fuel_generator", ["IWI", "BFB", "ICI"],
           {"I": "minecraft:iron_ingot", "W": rl("copper_wire"), "B": "minecraft:furnace",
            "F": rl("machine_frame"), "C": "minecraft:copper_ingot"}, rl("solid_fuel_generator"))
    shaped("carbon_capacitor", ["GRG", "GFG", "CWC"],
           {"G": rl("graphite"), "R": "minecraft:redstone_block", "F": rl("machine_frame"),
            "C": "minecraft:copper_ingot", "W": rl("copper_wire")}, rl("carbon_capacitor"))


    shaped("tailings_mill", ["IGI", "HFH", "IWI"],
           {"I": "minecraft:iron_ingot", "G": "minecraft:grindstone", "H": "minecraft:hopper",
            "F": rl("machine_frame"), "W": rl("copper_wire")}, rl("tailings_mill"))
    shaped("acid_plant", ["GCG", "BFB", "IWI"],
           {"G": "minecraft:glass", "C": "minecraft:cauldron", "B": "minecraft:bricks",
            "F": rl("machine_frame"), "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("acid_plant"))
    shaped("leaching_reactor", ["BGB", "CFC", "IWI"],
           {"B": "minecraft:bricks", "G": "minecraft:glass", "C": "minecraft:copper_ingot",
            "F": rl("machine_frame"), "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("leaching_reactor"))
    shaped("filter_press", ["IPI", "SFS", "IWI"],
           {"I": "minecraft:iron_ingot", "P": "minecraft:piston", "S": "minecraft:smooth_stone",
            "F": rl("machine_frame"), "W": rl("copper_wire")}, rl("filter_press"))
    shaped("precipitation_reactor", ["GBG", "BFB", "IWI"],
           {"G": "minecraft:glass", "B": "minecraft:bucket", "F": rl("machine_frame"),
            "I": "minecraft:iron_ingot", "W": rl("copper_wire")}, rl("precipitation_reactor"))
    shaped("acid_regeneration_column", ["BGB", "HFH", "IWI"],
           {"B": "minecraft:bricks", "G": "minecraft:glass_bottle", "H": "minecraft:hopper",
            "F": rl("machine_frame"), "I": "minecraft:iron_ingot", "W": rl("copper_wire")},
           rl("acid_regeneration_column"))


# ---------------------------------------------------------------- лут

def survives():
    return [{"condition": "minecraft:survives_explosion"}]


def loot_self(bid):
    wj(DATA / f"loot_table/blocks/{bid}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
                   "entries": [{"type": "minecraft:item", "name": rl(bid)}], "conditions": survives()}],
        "random_sequence": rl(f"blocks/{bid}")})


def loot_ore(bid, m):
    silk = [{"condition": "minecraft:match_tool", "predicate": {"predicates": {
        "minecraft:enchantments": [{"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}]
    funcs = []
    if m.drops != (1, 1):
        funcs.append({"function": "minecraft:set_count", "add": False,
                      "count": {"type": "minecraft:uniform", "min": float(m.drops[0]), "max": float(m.drops[1])}})
    funcs += [{"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune",
               "formula": "minecraft:ore_drops"}, {"function": "minecraft:explosion_decay"}]
    wj(DATA / f"loot_table/blocks/{bid}.json", {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{
            "type": "minecraft:alternatives", "children": [
                {"type": "minecraft:item", "name": rl(bid), "conditions": silk},
                {"type": "minecraft:item", "name": rl(m.raw_id), "functions": funcs}]}]}],
        "random_sequence": rl(f"blocks/{bid}")})


# ---------------------------------------------------------------- теги

def tag(path, values):
    wj(path, {"replace": False, "values": sorted(set(values))})


def tags():
    ores = ore_blocks()
    pick, stone, iron, dia = [], [], [], []
    for bid, r, e, m, kind in ores:
        pick.append(rl(bid))
        {"stone": stone, "iron": iron, "diamond": dia}[m.tool].append(rl(bid))
    for m in NEW_METALS:
        pick.append(rl(f"{m.id}_block"))
        iron.append(rl(f"{m.id}_block"))
    pick += [rl("aggregate_block")] + [rl(x) for x in MACHINES] + [rl("copper_wire")]
    tag(MC_TAGS / "block/mineable/shovel.json", [rl("ash_block")])
    stone += [rl("aggregate_block")]
    tag(MC_TAGS / "block/mineable/pickaxe.json", pick)
    tag(MC_TAGS / "block/needs_stone_tool.json", stone)
    tag(MC_TAGS / "block/needs_iron_tool.json", iron)
    tag(MC_TAGS / "block/needs_diamond_tool.json", dia)
    # common-теги
    all_ores = [rl(b[0]) for b in ores]
    tag(C_TAGS / "block/ores.json", all_ores)
    tag(C_TAGS / "item/ores.json", all_ores)
    tag(C_TAGS / "block/ores_in_ground/stone.json", [rl(b[0]) for b in ores if b[4] == "stone"])
    tag(C_TAGS / "block/ores_in_ground/deepslate.json", [rl(b[0]) for b in ores if b[4] == "deepslate"])
    tag(C_TAGS / "block/ores_in_ground/netherrack.json", [rl(b[0]) for b in ores if b[4] == "nether"])
    tag(C_TAGS / "item/ores_in_ground/stone.json", [rl(b[0]) for b in ores if b[4] == "stone"])
    tag(C_TAGS / "item/ores_in_ground/deepslate.json", [rl(b[0]) for b in ores if b[4] == "deepslate"])
    tag(C_TAGS / "item/ores_in_ground/netherrack.json", [rl(b[0]) for b in ores if b[4] == "nether"])
    for m in MINERALS:
        group = [rl(m.ore_id), rl(f"deepslate_{m.ore_id}")] + ([rl(f"nether_{m.ore_id}")] if m.nether else [])
        tag(C_TAGS / f"block/ores/{m.id}.json", group)
        tag(C_TAGS / f"item/ores/{m.id}.json", group)
        tag(C_TAGS / f"item/raw_materials/{m.id}.json", [rl(m.raw_id)])
    tag(C_TAGS / "item/raw_materials.json", [rl(m.raw_id) for m in MINERALS])
    for me in NEW_METALS:
        tag(C_TAGS / f"item/ingots/{me.id}.json", [rl(f"{me.id}_ingot")])
        tag(C_TAGS / f"block/storage_blocks/{me.id}.json", [rl(f"{me.id}_block")])
        tag(C_TAGS / f"item/storage_blocks/{me.id}.json", [rl(f"{me.id}_block")])
    tag(C_TAGS / "item/ingots.json", [rl(f"{m.id}_ingot") for m in NEW_METALS])
    tag(C_TAGS / "block/storage_blocks.json", [rl(f"{m.id}_block") for m in NEW_METALS])
    tag(C_TAGS / "item/storage_blocks.json", [rl(f"{m.id}_block") for m in NEW_METALS])
    # теги контура: сырьё машин
    for form, _, _ in FORMS:
        tag(DATA / f"tags/item/{form}.json", [rl(f"{m.id}_{form}") for m in METALS])
    # биомы
    for m in MINERALS:
        tag(DATA / f"tags/worldgen/biome/has_{m.id}.json", list(m.biomes))


# ---------------------------------------------------------------- мир

def worldgen():
    def targets(m, nether=False):
        if nether:
            return [{"target": {"predicate_type": "minecraft:tag_match", "tag": "minecraft:base_stone_nether"},
                     "state": {"Name": rl(f"nether_{m.ore_id}")}}]
        return [
            {"target": {"predicate_type": "minecraft:tag_match", "tag": "minecraft:stone_ore_replaceables"},
             "state": {"Name": rl(m.ore_id)}},
            {"target": {"predicate_type": "minecraft:tag_match", "tag": "minecraft:deepslate_ore_replaceables"},
             "state": {"Name": rl(f"deepslate_{m.ore_id}")}}]

    for m in MINERALS:
        for nether in ([False, True] if m.nether else [False]):
            name = f"ore_{m.id}" + ("_nether" if nether else "")
            wj(DATA / f"worldgen/configured_feature/{name}.json", {
                "type": "minecraft:ore", "config": {
                    "size": m.size, "discard_chance_on_air_exposure": 0.0 if not nether else 0.0,
                    "targets": targets(m, nether)}})
            y0, y1 = (m.y_min, m.y_max) if not nether else (10, 110)
            placement = []
            if m.rarity:
                placement.append({"type": "minecraft:rarity_filter", "chance": m.rarity})
            placement += [
                {"type": "minecraft:count", "count": m.count if not nether else 4},
                {"type": "minecraft:in_square"},
                {"type": "minecraft:height_range", "height": {
                    "type": "minecraft:uniform", "min_inclusive": {"absolute": y0}, "max_inclusive": {"absolute": y1}}},
                {"type": "minecraft:biome"}]
            wj(DATA / f"worldgen/placed_feature/{name}.json", {"feature": rl(name), "placement": placement})
            wj(DATA / f"neoforge/biome_modifier/add_{name}.json", {
                "type": "neoforge:add_features",
                "biomes": "#minecraft:is_nether" if nether else f"#{MODID}:has_{m.id}",
                "features": rl(name), "step": "underground_ores"})
