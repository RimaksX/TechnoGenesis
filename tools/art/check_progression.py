"""Проверка проходимости: от ванильных предметов и сырой руды до каждого предмета Контура должен вести путь без замкнутых кругов."""
import json, re, glob, os
R = "/home/user/TechnoGenesis/src/main/resources/data/kontur/recipe"
J = "/home/user/TechnoGenesis/src/main/java/dev/technogenesis/kontur"
kinds = open(f"{J}/machine/MachineKind.java", encoding="utf8").read()
rk = open(f"{J}/registry/KonturRecipes.java", encoding="utf8").read()
const_to_name = dict(re.findall(r'Kind (\w+) = new Kind\("(\w+)"\)', rk))
type_to_machine = {}
for mid, const in re.findall(r'\w+\("(\w+)", (?:true|false), (?:true|false), KonturRecipes\.(\w+),', kinds):
    type_to_machine[const_to_name[const]] = mid

def nid(x):
    return x if ":" in x else "minecraft:" + x

recipes = []
for f in glob.glob(R + "/**/*.json", recursive=True):
    d = json.load(open(f, encoding="utf8"))
    t = d["type"]
    if t.startswith("kontur:"):
        name = t.split(":")[1]
        ins = []
        if "input" in d:
            ing = d["input"]["ingredient"]
            ins.append([i.get("item") or "#" + i.get("tag") for i in (ing if isinstance(ing, list) else [ing])])
        if "input_b" in d:
            ing = d["input_b"]["ingredient"]
            ins.append([i.get("item") or "#" + i.get("tag") for i in (ing if isinstance(ing, list) else [ing])])
        fl_in = d.get("fluid_input", {}).get("fluids", [])
        recipes.append(dict(kind="machine", machine="kontur:" + type_to_machine[name], ins=ins, fin=fl_in,
                            outs=[r["id"] for r in d["results"]], fouts=[x["fluid"] for x in d.get("fluid_results", [])],
                            file=os.path.relpath(f, R)))
    elif t in ("minecraft:crafting_shaped", "minecraft:crafting_shapeless"):
        ings = list(d["key"].values()) if "key" in d else d["ingredients"]
        ins = [[i.get("item") or "#" + i.get("tag")] for i in ings]
        recipes.append(dict(kind="craft", ins=ins, outs=[d["result"]["id"]], fin=[], fouts=[], file=os.path.relpath(f, R)))
    elif t in ("minecraft:smelting", "minecraft:blasting", "minecraft:smoking"):
        ing = d["ingredient"]
        ins = [[i.get("item") or "#" + i.get("tag") for i in (ing if isinstance(ing, list) else [ing])]]
        res = d["result"]
        recipes.append(dict(kind="smelt", ins=ins, outs=[res["id"] if isinstance(res, dict) else res], fin=[], fouts=[],
                            file=os.path.relpath(f, R)))

have = set()
fluids = {"minecraft:water", "minecraft:lava"}
def ok(options):
    return any(o.startswith("#") or o.startswith("minecraft:") or o in have for o in options)
for rm in ["raw_bauxite", "raw_garnierite", "raw_wolframite", "raw_chromite", "raw_pyrolusite", "raw_cobaltite", "raw_molybdenite",
           "raw_rutile", "raw_graphite", "raw_halite", "raw_sulfur", "raw_spodumene"]:
    have.add("kontur:" + rm)
changed = True
while changed:
    changed = False
    for r in recipes:
        if not all(ok(o) for o in r["ins"]):
            continue
        if r["fin"] and not any(f in fluids for f in r["fin"]):
            continue
        if r["kind"] == "machine" and r["machine"] not in have:
            continue
        for o in r["outs"]:
            if o not in have:
                have.add(o); changed = True
        for f in r["fouts"]:
            if f not in fluids:
                fluids.add(f); changed = True
allout = {o for r in recipes for o in r["outs"]} | {f for r in recipes for f in r["fouts"]}
missing = sorted(o for o in allout if o.startswith("kontur:") and o not in have and o not in fluids)
print("всего рецептов:", len(recipes), "достижимо предметов Контура:", sum(1 for h in have if h.startswith("kontur:")))
print("недостижимо:", missing if missing else "нет")
