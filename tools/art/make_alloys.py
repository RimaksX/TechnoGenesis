"""Слитки сплавов: тот же ванильный силуэт, свои палитры."""
import json
from pathlib import Path
from PIL import Image
import make_ingots as MI
PAL = {
 "steel":            [(26,30,38),(58,64,76),(64,70,84),(84,92,108),(108,118,136),(140,150,168),(176,186,204),(222,230,244)],
 "stainless_steel":  [(52,62,64),(110,122,124),(118,130,132),(146,158,160),(176,188,190),(206,216,218),(232,240,240),(255,255,255)],
 "tungsten_carbide": [(14,12,22),(34,30,48),(40,36,56),(54,48,74),(72,66,96),(96,88,124),(128,120,156),(170,162,196)],
 "titanium_alloy":   [(28,40,60),(52,78,110),(58,86,120),(74,110,150),(96,138,182),(124,168,212),(160,200,240),(210,236,255)],
 "magnetic_alloy":   [(52,16,22),(104,32,40),(112,38,46),(140,52,60),(172,70,78),(204,98,104),(230,138,140),(252,196,196)],
 "nichrome":         [(62,46,34),(118,90,66),(126,98,72),(152,122,92),(180,150,116),(208,180,144),(232,208,176),(252,240,216)],
}
M = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/models/item")
for name, pal in PAL.items():
    MI.recolor(pal).save(MI.ROOT / f"{name}_ingot.png")
    (M / f"{name}_ingot.json").write_text('{\n  "parent": "minecraft:item/generated",\n  "textures": {\n    "layer0": "kontur:item/%s_ingot"\n  }\n}\n' % name)
sheet = Image.new("RGBA", (6 * 100, 100), (70, 72, 80, 255))
for i, name in enumerate(PAL):
    im = Image.open(MI.ROOT / f"{name}_ingot.png").convert("RGBA").resize((96, 96), 0)
    sheet.paste(im, (i * 100 + 2, 2), im)
sheet.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/alloys.png")
