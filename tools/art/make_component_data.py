"""Рецепты деталей и обновлённые рецепты машин, названия и подсказки."""
import json
from pathlib import Path
R = Path("/home/user/TechnoGenesis/src/main/resources/data/kontur/recipe")
L = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/lang")
K = "kontur:"

def item(i):
    return {"item": i if ":" in i else "minecraft:" + i}

def wj(path, d):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

def shaped(name, pattern, key, result, count=1):
    wj(R / f"{name}.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern,
                            "key": {k: item(v) for k, v in key.items()}, "result": {"id": result, "count": count}})

def shapeless(name, ings, result, count=1):
    wj(R / f"{name}.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                            "ingredients": [item(i) for i in ings], "result": {"id": result, "count": count}})

def machine(kind, name, inp, fluid, amount, results, energy, time, fluid_results=None):
    d = {"type": K + kind, "results": [{"id": K + r, "count": c} for r, c in results], "energy": energy, "time": time,
         "input": {"ingredient": item(inp), "count": 1},
         "fluid_input": {"fluids": [K + fluid], "amount": amount}}
    if fluid_results:
        d["fluid_results"] = fluid_results
    wj(R / kind / f"{name}.json", d)

# ---- детали
shaped("circuit_blank", ["PPP", "CCC"], {"P": "paper", "C": "clay_ball"}, K + "circuit_blank", 2)
shapeless("circuit_board_by_hand", [K + "circuit_blank", K + "copper_wire", K + "copper_wire", "redstone"], K + "circuit_board")
machine("leaching", "circuit_board_etching", K + "circuit_blank", "sulfuric_acid", 100, [("circuit_board", 2)], 2400, 80)
shaped("control_circuit", ["CRC", "NBN", "CRC"], {"C": K + "copper_wire", "R": "redstone", "N": K + "nickel_ingot",
       "B": K + "circuit_board"}, K + "control_circuit")
shaped("processor_blank", ["QGQ", "CBC", "QGQ"], {"Q": "quartz", "G": "gold_ingot", "C": K + "control_circuit",
       "B": K + "cobalt_ingot"}, K + "processor_blank")
machine("autoclaving", "processor_sintering", K + "processor_blank", "steam", 1000, [("processor", 1)], 24000, 100)
machine("plasma_smelting", "plasma_controller_coating", K + "processor", "plasma", 500, [("plasma_controller", 1)], 30000, 100)
shaped("winding", ["WWW", "WIW", "WWW"], {"W": K + "copper_wire", "I": "iron_ingot"}, K + "winding", 2)
machine("extraction", "magnet_impregnation", K + "magnetic_alloy_ingot", "solvent", 200, [("magnet", 1)], 6400, 100)
shaped("power_module", ["WMW", "NCN", "WMW"], {"W": K + "winding", "M": K + "magnet", "N": K + "manganese_ingot",
       "C": K + "control_circuit"}, K + "power_module")
shaped("gear_drive", ["IGI", "GPG", "IGI"], {"I": "iron_ingot", "G": K + "graphite", "P": "piston"}, K + "gear_drive", 2)
shaped("precision_drive", ["MDM", "SKS", "MDM"], {"M": K + "molybdenum_ingot", "D": K + "gear_drive",
       "S": K + "stainless_steel_ingot", "K": K + "circuit_board"}, K + "precision_drive")
shaped("valve_block", ["SGS", "DHD", "SGS"], {"S": K + "stainless_steel_ingot", "G": "glass", "D": K + "gear_drive",
       "H": "hopper"}, K + "valve_block", 2)
shaped("heat_plate", ["TMT", "KKK", "TMT"], {"T": K + "tungsten_carbide_ingot", "M": K + "nichrome_ingot",
       "K": K + "titanium_alloy_ingot"}, K + "heat_plate", 2)

# ---- машины: рама + детали, ряд снизу показывает ступень
F = K + "machine_frame"
def mach(name, pattern, key, count=1):
    key = dict(key); key["F"] = F
    shaped(name, pattern, key, K + name, count)

W, D, C, V, P, M, X, H, Z = (K + "winding", K + "gear_drive", K + "control_circuit", K + "valve_block",
                             K + "precision_drive", K + "power_module", K + "processor", K + "heat_plate",
                             K + "plasma_controller")
# x2
mach("jaw_crusher", ["IPI", "WFW", "IDI"], {"I": "iron_ingot", "P": "piston", "W": W, "D": D})
mach("washing_drum", ["ICI", "BFB", "WDW"], {"I": "iron_ingot", "C": "cauldron", "B": "bucket", "W": W, "D": D})
mach("magnetic_separator", ["IMI", "WFW", "IDI"], {"I": "iron_ingot", "M": "iron_block", "W": W, "D": D})
mach("settling_tank", ["GCG", "GFG", "WDW"], {"G": "glass", "C": "cauldron", "W": W, "D": D})
# энергетика
mach("solid_fuel_generator", ["IWI", "BFB", "IDI"], {"I": "iron_ingot", "W": W, "B": "furnace", "D": D})
mach("steam_turbine", ["IKI", "WFW", "RDR"], {"I": "iron_ingot", "K": "cauldron", "W": W, "R": "redstone", "D": D})
mach("thermal_generator", ["IMI", "WFW", "RDR"], {"I": "iron_ingot", "M": "magma_block", "W": W, "R": "redstone", "D": D})
mach("water_pump", ["IBI", "PFP", "WDW"], {"I": "iron_ingot", "B": "bucket", "P": "piston", "W": W, "D": D})
mach("wind_rotor", ["III", "DFD", "RWR"], {"I": "iron_ingot", "R": "redstone", "W": W, "D": D})
mach("carbon_capacitor", ["GRG", "GFG", "CWC"], {"G": K + "graphite", "R": "redstone_block", "C": "copper_ingot", "W": W})
mach("solar_panel_advanced", ["QQQ", "BFB", "ICI"], {"Q": "quartz", "B": K + "solar_panel", "I": "iron_ingot", "C": C})
shaped("solar_farm", ["AAA", "AAA", "CFC"], {"A": K + "solar_panel_advanced", "C": C, "F": F}, K + "solar_farm")
mach("miner", ["IPI", "WFW", "CMC"], {"I": "iron_ingot", "P": "piston", "W": W, "C": C, "M": K + "module_worker"})
# x3
mach("tailings_mill", ["IGI", "HFH", "WDC"], {"I": "iron_ingot", "G": "grindstone", "H": "hopper", "W": W, "D": D, "C": C})
mach("acid_plant", ["GKG", "BFB", "WCV"], {"G": "glass", "K": "cauldron", "B": "bricks", "W": W, "C": C, "V": V})
mach("leaching_reactor", ["BGB", "NFN", "WCV"], {"B": "bricks", "G": "glass", "N": K + "nickel_ingot", "W": W, "C": C, "V": V})
mach("filter_press", ["IPI", "SFS", "WDC"], {"I": "iron_ingot", "P": "piston", "S": "smooth_stone", "W": W, "D": D, "C": C})
mach("precipitation_reactor", ["GBG", "BFB", "WCV"], {"G": "glass", "B": "bucket", "W": W, "C": C, "V": V})
mach("acid_regeneration_column", ["BGB", "HFH", "WCV"], {"B": "bricks", "G": "glass_bottle", "H": "hopper", "W": W, "C": C, "V": V})
# x5
mach("extractor", ["GBG", "HFH", "WPC"], {"G": "glass", "B": "bucket", "H": "hopper", "W": W, "P": P, "C": C})
mach("electrolyzer", ["GNG", "RFR", "MCM"], {"G": K + "graphite", "N": "copper_ingot", "R": "redstone", "M": M, "C": C})
mach("solvent_regenerator", ["BKB", "HFH", "VPC"], {"B": "bricks", "K": "furnace", "H": "hopper", "V": V, "P": P, "C": C})
# x8
mach("attritor", ["IGI", "SFS", "PMP"], {"I": "iron_ingot", "G": "grindstone", "S": "smooth_stone", "P": P, "M": M})
mach("steam_generator", ["BKB", "BFB", "VHC"], {"B": "bricks", "K": "cauldron", "V": V, "H": H, "C": C})
mach("autoclave", ["IBI", "BFB", "VHM"], {"I": "iron_ingot", "B": "iron_block", "V": V, "H": H, "M": M})
# x12
mach("plasma_generator", ["TDT", "RFR", "HXM"], {"T": K + "tungsten_carbide_ingot", "D": "diamond", "R": "redstone_block", "H": H, "X": X, "M": M})
mach("plasma_furnace", ["TBT", "DFD", "HXM"], {"T": K + "tungsten_carbide_ingot", "B": "blast_furnace", "D": "diamond", "H": H, "X": X, "M": M})
mach("vacuum_caster", ["MGM", "TFT", "HZH"], {"M": K + "molybdenum_ingot", "G": "glass", "T": K + "titanium_alloy_ingot", "H": H, "Z": Z})
# модули и радиаторы
shaped("module_worker", ["IRI", "RWR", "IRI"], {"I": "iron_ingot", "R": "redstone", "W": W}, K + "module_worker")
shaped("module_industrial", ["GCG", "RMR", "GCG"], {"G": "gold_ingot", "C": C, "R": "redstone", "M": K + "module_worker"}, K + "module_industrial")
shaped("module_peak", ["DPD", "BMB", "DPD"], {"D": "diamond", "P": M, "B": "redstone_block", "M": K + "module_industrial"}, K + "module_peak")
shaped("radiator_titanium", ["TTT", "TRT", "THT"], {"T": K + "titanium_alloy_ingot", "R": K + "radiator_aluminum", "H": H}, K + "radiator_titanium")

# ---- язык
RU = {
    "circuit_blank": ("Заготовка платы", "Основа для платы. Травится в кислоте в реакторе выщелачивания: из одной заготовки две платы"),
    "circuit_board": ("Печатная плата", "Основа любой электроники. В кислоте выходит вдвое больше, чем вручную"),
    "control_circuit": ("Схема управления", "Электроника машин ступеней ×3 и выше"),
    "processor_blank": ("Заготовка процессора", "Спекается в автоклаве под паром и становится процессором"),
    "processor": ("Процессор", "Для машин ступеней ×8 и ×12. Делается в автоклаве из заготовки процессора"),
    "plasma_controller": ("Плазменный контроллер", "Процессор, закалённый плазмой в плазменной печи. Нужен вакуумному кристаллизатору"),
    "winding": ("Обмотка", "Медная обмотка для моторов и генераторов"),
    "magnet": ("Магнит", "Кобальт, пропитанный растворителем в экстракторе. Идёт в силовые модули"),
    "power_module": ("Силовой модуль", "Мощная силовая часть: электролизёр, аттритор, плазменные машины"),
    "gear_drive": ("Привод", "Шестерни с графитовой смазкой: вращают барабаны, дробилки и турбины"),
    "precision_drive": ("Точный привод", "Для экстрактора, регенератора растворителя и аттритора"),
    "valve_block": ("Клапанный блок", "Хромовые клапаны для химических машин и парогенератора"),
    "heat_plate": ("Жаропрочная плита", "Вольфрам, молибден и титан: для автоклава и плазменных машин"),
}
EN = {
    "circuit_blank": ("Board Blank", "Base for a board. Etch it in acid in the leaching reactor: one blank gives two boards"),
    "circuit_board": ("Circuit Board", "Base of any electronics. Acid etching gives twice as many as hand crafting"),
    "control_circuit": ("Control Circuit", "Electronics for stage x3 machines and above"),
    "processor_blank": ("Processor Blank", "Sintered in an autoclave under steam to become a processor"),
    "processor": ("Processor", "For stage x8 and x12 machines. Made in an autoclave from a processor blank"),
    "plasma_controller": ("Plasma Controller", "A processor hardened by plasma in the plasma furnace. Needed by the vacuum caster"),
    "winding": ("Winding", "Copper winding for motors and generators"),
    "magnet": ("Magnet", "Cobalt impregnated with solvent in the extractor. Goes into power modules"),
    "power_module": ("Power Module", "Heavy power section: electrolyzer, attritor, plasma machines"),
    "gear_drive": ("Drive Unit", "Gears with graphite grease: turn drums, crushers and turbines"),
    "precision_drive": ("Precision Drive", "For the extractor, solvent regenerator and attritor"),
    "valve_block": ("Valve Block", "Chromium valves for chemical machines and the steam generator"),
    "heat_plate": ("Heat-Resistant Plate", "Tungsten, molybdenum and titanium: for the autoclave and plasma machines"),
}
for f, tbl in (("ru_ru.json", RU), ("en_us.json", EN)):
    p = L / f
    d = json.loads(p.read_text(encoding="utf8"))
    for k, (name, tip) in tbl.items():
        d[f"item.kontur.{k}"] = name
        d[f"tooltip.kontur.component.{k}"] = tip
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
