import sys, json
sys.path.insert(0, '.')
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from kontur_gen import multi as MU, machines3d as MM, model3d as M, preview3d as P
OUT = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/renders")
OUT.mkdir(exist_ok=True)
names = json.load(open("/home/user/TechnoGenesis/src/main/resources/assets/kontur/lang/ru_ru.json"))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
SIZES = {"washing_drum": "2×1×1", "jaw_crusher": "2×1×1", "magnetic_separator": "2×1×1", "tailings_mill": "2×1×1",
         "steam_turbine": "2×1×1", "settling_tank": "2×2×1", "steam_generator": "1×1×2", "solid_fuel_generator": "1×1×2",
         "acid_plant": "2×2×2", "leaching_reactor": "2×2×2", "precipitation_reactor": "2×2×2", "attritor": "2×2×2",
         "plasma_generator": "2×2×2", "water_splitter": "2×2×2", "filter_press": "3×2×1", "extractor": "3×2×1", "vacuum_caster": "3×2×1",
         "electrolyzer": "3×2×2", "autoclave": "3×2×2", "plasma_furnace": "2×3×2", "acid_regeneration_column": "1×1×3",
         "solvent_regenerator": "2×1×3", "solar_farm": "3×2×1"}
views = ((-26, 16), (32, 24))

def sheet(mid, model, dims):
    els, imgs, place = M.build(model, frames=4)
    X, Y, Z = dims
    ext = max(X, Y, Z) * 0.80
    px = max(6, int(520 / (2 * ext)))
    tiles = [P.render(model, imgs[1], place, yaw=y, pitch=p, px=px, extent=ext, bg=(62, 64, 72), center=(X / 2, Y / 2, Z / 2)) for (y, p) in views]
    w, h = tiles[0].size
    img = Image.new("RGB", (w * 2, h + 44), (46, 48, 54))
    for i, t in enumerate(tiles):
        img.paste(t, (i * w, 44))
    d = ImageDraw.Draw(img)
    title = names.get("block.kontur." + mid, mid)
    d.text((14, 8), title, fill=(236, 238, 242), font=font)
    d.text((w * 2 - 14 - d.textlength(SIZES.get(mid, "1×1×1"), font=small), 14), SIZES.get(mid, "1×1×1"), fill=(160, 166, 176), font=small)
    img.save(OUT / f"{mid}.png")
    return OUT / f"{mid}.png"

order = ["jaw_crusher", "washing_drum", "magnetic_separator", "settling_tank", "tailings_mill", "acid_plant", "leaching_reactor",
         "filter_press", "precipitation_reactor", "acid_regeneration_column", "extractor", "electrolyzer", "solvent_regenerator",
         "attritor", "steam_generator", "autoclave", "plasma_generator", "plasma_furnace", "vacuum_caster", "water_splitter",
         "solid_fuel_generator", "steam_turbine", "thermal_generator", "water_pump", "carbon_capacitor", "wind_rotor",
         "miner", "solar_panel", "solar_panel_advanced"]
only = sys.argv[1:]
done = []
for mid in order:
    if only and mid not in only:
        continue
    if mid in MU.BIG:
        m = MU.BIG[mid](); dims = (m.X, m.Y, m.Z)
    else:
        m = MM.ALL[mid](5) if mid == "carbon_capacitor" else MM.ALL[mid](); dims = (16, 16, 16)
        if mid == "wind_rotor":
            m = MM.wind_rotor(blades=True)
    done.append(sheet(mid, m, dims)); print(mid)
if not only or "solar_farm" in only:
    m = MU.BIG["solar_farm"]()
    sheet("solar_farm", m, (m.X, m.Y, m.Z)); print("solar_farm")
