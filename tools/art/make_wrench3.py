from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
# пиксель в пиксель по образцу (B - контур, D - тёмная тень, d/m/L - тёмный/средний/светлый тон), затем зеркало по горизонтали
REF = [
"..........BBBB..",
".........BLLLmB.",
"........BLmmddmB",
"........BmmBDDDB",
"........BdmD....",
".......BdmmLBBB.",
".......DdddmLLD.",
"......BmmdBDDD..",
".....BLmdDD.....",
"....BLmmD.......",
"...BLmmD........",
".BBmmdD.........",
"DLmmdD..........",
"DLBmD...........",
"DmmdD...........",
".DDD............",
]
assert all(len(r) == 16 for r in REF) and len(REF) == 16
PAL = {"D": (22, 26, 36), "B": (46, 54, 72), "d": (88, 100, 124), "m": (134, 150, 176), "L": (196, 212, 234)}
im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
for y, row in enumerate(REF):
    for x, c in enumerate(row[::-1]):      # зеркало по горизонтали: головка слева сверху
        if c in PAL:
            im.putpixel((x, y), (*PAL[c], 255))
im.save(ITEM / "wrench.png")
big = Image.new("RGBA", (16 * 12 + 20 + 40, 16 * 12 + 20), (139, 139, 139, 255))
big.alpha_composite(im.resize((192, 192), 0), (10, 10))
big.alpha_composite(im, (214, 10)); big.alpha_composite(im.resize((32, 32), 0), (214, 40))
big.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/wrench_big.png")
