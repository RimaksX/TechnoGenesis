from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
# o - внешний контур, D - тёмная тень, d/m/L - сталь (тёмная, средняя, светлая), g/h/i - накладка рукояти
MAP = [
"...........ooooo",
"..........oLLLmo",
".........oLmmddo",
".........oLmmooo",
"........oLdmo...",
"........odmmLooo",
".......oddmmLLLo",
".......ommdddoo.",
"......oLmddDo...",
".....oLmmdDo....",
"....oLmmdDo.....",
"...ohhdDo.......",
"..ohiihDo.......",
".oDihhdDo.......",
".DhhhdDo........",
"..DDDDo.........",
]
assert all(len(r) == 16 for r in MAP) and len(MAP) == 16
PAL = {
    "o": (20, 24, 34), "D": (30, 36, 50),
    "d": (74, 86, 108), "m": (126, 142, 168), "L": (200, 214, 236),
    "g": (150, 78, 22), "h": (214, 124, 40), "i": (255, 190, 90),
}
im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
for y, row in enumerate(MAP):
    for x, c in enumerate(row):
        if c in PAL:
            im.putpixel((x, y), (*PAL[c], 255))
im.save(ITEM / "wrench.png")
big = Image.new("RGBA", (16 * 12 + 20 + 40, 16 * 12 + 20), (139, 139, 139, 255))
big.alpha_composite(im.resize((192, 192), 0), (10, 10))
big.alpha_composite(im, (214, 10)); big.alpha_composite(im.resize((32, 32), 0), (214, 40))
big.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/wrench_big.png")
