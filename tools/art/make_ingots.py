import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
VAN = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/art_tools/.vanilla/item")
LEVELS = [53, 88, 94, 114, 130, 168, 216, 255]       # тона ванильного железного слитка
PAL = {
 "aluminum":   [(62,72,88),(106,120,140),(112,126,146),(140,156,174),(170,184,200),(200,212,224),(226,234,242),(250,252,255)],
 "chromium":   [(40,64,76),(78,112,128),(84,118,134),(110,148,164),(140,180,196),(176,212,224),(210,236,244),(246,255,255)],
 "cobalt":     [(14,22,70),(24,44,120),(28,50,128),(34,64,160),(46,86,196),(74,120,226),(120,162,244),(190,214,255)],
 "manganese":  [(58,26,60),(100,48,100),(108,54,106),(132,70,126),(160,92,150),(190,122,176),(218,158,204),(246,206,236)],
 "molybdenum": [(22,28,38),(48,58,72),(54,64,80),(68,80,98),(88,102,122),(114,130,152),(150,166,186),(196,210,226)],
 "nickel":     [(74,66,48),(120,110,84),(128,118,92),(150,140,110),(178,168,136),(204,196,164),(228,222,194),(252,250,230)],
 "titanium":   [(30,30,44),(62,64,84),(68,70,92),(88,92,116),(112,118,144),(140,146,172),(172,178,202),(214,220,238)],
 "tungsten":   [(18,20,18),(40,44,40),(46,50,46),(58,62,58),(76,80,76),(98,102,96),(126,130,122),(168,172,162)],
}
src = np.array(Image.open(VAN / "iron_ingot.png").convert("RGBA"))
def recolor(pal):
    out = src.copy()
    for y in range(16):
        for x in range(16):
            if src[y, x, 3] == 0:
                continue
            v = int(src[y, x, 0])
            i = min(range(len(LEVELS)), key=lambda k: abs(LEVELS[k] - v))
            out[y, x, :3] = pal[i]
    return Image.fromarray(out)
if __name__ == "__main__":
    for m, pal in PAL.items():
        recolor(pal).save(ROOT / f"{m}_ingot.png")
    sheet = Image.new("RGBA", (9 * 100, 100), (70, 72, 80, 255))
    ims = [Image.open(VAN / "iron_ingot.png").convert("RGBA")] + [Image.open(ROOT / f"{m}_ingot.png").convert("RGBA") for m in PAL]
    for i, im in enumerate(ims):
        im = im.resize((96, 96), 0); sheet.paste(im, (i * 100 + 2, 2), im)
    sheet.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/ingots_new.png")
