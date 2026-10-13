#!/usr/bin/env python3
"""Проверка согласованности ресурсов и кода без запуска игры.

1. Перечисления Metal/Mineral в Java совпадают со списками генератора.
2. Все текстуры, на которые ссылаются модели, существуют; все модели из blockstates существуют.
3. Для каждого блока/предмета есть название в ru_ru и en_us.
4. Все предметы/блоки в рецептах и тегах существуют, рецепты машин разбираются по схеме кодека.
"""
import json
import re
import sys
from pathlib import Path

import os
ROOT = Path(os.environ.get("KONTUR_ROOT", "/home/user/TechnoGenesis"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kontur_gen.defs import *  # noqa: E402
from kontur_gen import data as G  # noqa: E402

errors = []


def err(msg):
    errors.append(msg)


# --- 1. Java <-> Python
jdir = ROOT / "src/main/java/dev/technogenesis/kontur"
metal_rows = re.findall(r"\b([A-Z]+)\((?:true|false), 0x([0-9A-F]{8})\)", (jdir / "material/Metal.java").read_text())
if [m.lower() for m, _ in metal_rows] != [m.id for m in METALS]:
    err(f"Metal.java {[m for m, _ in metal_rows]} != defs.py {[m.id for m in METALS]}")
for (name, argb), m in zip(metal_rows, METALS):
    if argb != "FF" + SOLUTION_RGB[m.id].lstrip("#").upper():
        err(f"цвет раствора {m.id}: Java {argb} != {SOLUTION_RGB[m.id]}")
mj = re.findall(r'^\s+([A-Z]+)\("([a-z_]+)", "([a-z_]+)", (?:Metal\.([A-Z]+)|null), (\d), ([\d.]+)f, (\d), (\d), (true|false)\)',
                (jdir / "material/Mineral.java").read_text(), re.M)
tool = {"stone": 0, "iron": 1, "diamond": 2}
if len(mj) != len(MINERALS):
    err(f"Mineral.java: найдено {len(mj)} из {len(MINERALS)}")
for (name, ore, raw, metal, tier, hard, xp0, xp1, nether), m in zip(mj, MINERALS):
    exp = (m.id.upper(), m.ore_id, m.raw_id, (m.metal or "").upper(), tool[m.tool], m.hardness, m.xp[0], m.xp[1], m.nether)
    got = (name, ore, raw, metal, int(tier), float(hard), int(xp0), int(xp1), nether == "true")
    if exp != got:
        err(f"Mineral {m.id}: Java {got} != defs.py {exp}")

# --- 2. модели и текстуры
assets = ROOT / "src/main/resources/assets/kontur"
tex = {p.relative_to(assets / "textures").with_suffix("").as_posix() for p in (assets / "textures").rglob("*.png")}
models = {p.relative_to(assets / "models").with_suffix("").as_posix() for p in (assets / "models").rglob("*.json")}
for p in (assets / "models").rglob("*.json"):
    d = json.loads(p.read_text())
    for k, v in d.get("textures", {}).items():
        if v.startswith("kontur:") and v[7:] not in tex:
            err(f"{p.name}: нет текстуры {v}")
    par = d.get("parent", "")
    if par.startswith("kontur:") and par[7:] not in models:
        err(f"{p.name}: нет родительской модели {par}")
for p in (assets / "blockstates").glob("*.json"):
    d = json.loads(p.read_text())
    refs = []
    for v in d.get("variants", {}).values():
        refs += [v["model"]] if isinstance(v, dict) else [x["model"] for x in v]
    for part in d.get("multipart", []):
        refs.append(part["apply"]["model"])
    for r in refs:
        if r.startswith("kontur:") and r[7:] not in models:
            err(f"{p.name}: нет модели {r}")
for p in (assets / "textures").rglob("*.mcmeta"):
    pass

# --- 3. язык
ru = json.loads((assets / "lang/ru_ru.json").read_text())
en = json.loads((assets / "lang/en_us.json").read_text())
blocks = set(G.all_block_ids()) | set(FLUIDS)
blocks |= {'machine_frame','turbine_rotor','turbine_casing','cooler_casing','turbine_hall','cooling_tower','fusion_casing','assembly_port','furnace_casing','blast_furnace','fusion_reactor','hydrogen_generator','alloy_furnace','water_splitter','gas_pipe','gas_pipe_heavy','extractor','electrolyzer','solvent_regenerator','attritor','steam_generator','autoclave','plasma_generator','plasma_furnace','vacuum_caster','item_pipe_express','item_pipe_ultra','fluid_pipe_heavy','fluid_pipe_ultra','wind_rotor','thermal_generator','steam_turbine','solar_panel','solar_panel_advanced','solar_farm','ceramic_cable','armored_cable','superconducting_cable','item_pipe','item_pipe_fast','fluid_pipe','fluid_pipe_fast'}
fluid_ids = set(FLUIDS) | {f"{m.id}_solution" for m in METALS} | {f"{m.id}_extract" for m in METALS} | {"solvent", "spent_solvent", "steam", "plasma", "hydrogen", "oxygen", "condensate"} | {f"{m.id}_melt" for m in METALS}
for fid in {f"{m.id}_solution" for m in METALS} | {f"{m.id}_extract" for m in METALS} | {"solvent", "spent_solvent", "steam", "plasma"} | {f"{m.id}_melt" for m in METALS}:
    for lang, nm in ((ru, "ru"), (en, "en")):
        if f"fluid_type.kontur.{fid}" not in lang:
            err(f"{nm}: нет fluid_type.kontur.{fid}")
items = {p.stem for p in (assets / "models/item").glob("*.json")}
for b in blocks:
    for lang, nm in ((ru, "ru"), (en, "en")):
        if f"block.kontur.{b}" not in lang:
            err(f"{nm}: нет block.kontur.{b}")
for i in items:
    if i in blocks:
        continue
    for lang, nm in ((ru, "ru"), (en, "en")):
        if f"item.kontur.{i}" not in lang:
            err(f"{nm}: нет item.kontur.{i}")
if set(ru) != set(en):
    err(f"ключи ru/en различаются: {sorted(set(ru) ^ set(en))[:5]}")

# --- 4. рецепты и теги
existing = blocks | items | {f"{m.id}_ingot" for m in NEW_METALS} | {"lithium_rod", "steel_ingot", "stainless_steel_ingot", "tungsten_carbide_ingot", "titanium_alloy_ingot", "magnetic_alloy_ingot", "nichrome_ingot"}
vanilla_ok = re.compile(r"^minecraft:")


def check_id(i, where):
    if i.startswith("#"):
        return
    if vanilla_ok.match(i):
        return
    if i.startswith("c:ores/"):
        tagdir = ROOT / "src/main/resources/data/c/tags/item/ores"
        if i[7:] in {"iron", "copper", "gold"} or (tagdir / f"{i[7:]}.json").exists():
            return
    if i.startswith("kontur:") and i[7:] in existing:
        return
    err(f"{where}: неизвестный id {i}")


data = ROOT / "src/main/resources/data/kontur"
for p in (data / "recipe").rglob("*.json"):
    d = json.loads(p.read_text())
    w = p.relative_to(data).as_posix()
    if d["type"].startswith("kontur:"):
        for k in ("results", "energy", "time"):
            if k not in d:
                err(f"{w}: нет поля {k}")
        for r in d["results"]:
            check_id(r["id"], w)
        for key_in in ("input", "input_b"):
            if key_in in d:
                ings = d[key_in]["ingredient"]
                for ing in (ings if isinstance(ings, list) else [ings]):
                    check_id(ing.get("item", ing.get("tag", "#")), w)
        for f in d.get("fluid_input", {}).get("fluids", []):
            if not (f.startswith("minecraft:") or f in {f"kontur:{x}" for x in fluid_ids}):
                err(f"{w}: неизвестная жидкость {f}")
        for fo in d.get("fluid_results", []):
            if not (fo["fluid"].startswith("minecraft:") or fo["fluid"] in {f"kontur:{x}" for x in fluid_ids}):
                err(f"{w}: неизвестная жидкость на выходе {fo['fluid']}")
        # потребление энергии не превышает паспортный предел машины
        limits = {"crushing": 16, "washing": 12, "separating": 16, "settling": 16, "milling": 32, "acid_synthesis": 32,
                  "leaching": 32, "filtering": 16, "precipitation": 32, "acid_regeneration": 64,
                  "extraction": 64, "electrolysis": 144, "solvent_regeneration": 64,
                  "attrition": 120, "autoclaving": 240, "steam_generation": 32,
                  "plasma_generation": 400, "plasma_smelting": 300, "vacuum_casting": 200, "water_splitting": 192, "alloying": 240, "blast_smelting": 480}
        kind = d["type"].split(":")[1]
        if d["energy"] / d["time"] > limits[kind] + 1e-9:
            err(f"{w}: {d['energy']}/{d['time']} FE/t выше предела {limits[kind]}")
    else:
        res = d.get("result", {})
        check_id(res.get("id", "minecraft:air"), w)
        ings = []
        if "key" in d:
            ings = list(d["key"].values())
        elif "ingredients" in d:
            ings = d["ingredients"]
        elif "ingredient" in d:
            ings = [d["ingredient"]]
        for ing in ings:
            check_id(ing.get("item", "#" + ing.get("tag", "")), w)
for p in (data / "loot_table").rglob("*.json"):
    s = p.read_text()
    for m in re.findall(r'"name": "(kontur:[a-z_]+)"', s):
        check_id(m, p.name)
n_rec = len(list((data / "recipe").rglob("*.json")))
print(f"рецептов: {n_rec}, моделей: {len(models)}, текстур: {len(tex)}, блоков: {len(blocks)}, предметов: {len(items)}")
if errors:
    print(f"НАЙДЕНО ОШИБОК: {len(errors)}")
    for e in errors[:40]:
        print(" -", e)
    sys.exit(1)
print("OK: ресурсы и перечисления согласованы")
