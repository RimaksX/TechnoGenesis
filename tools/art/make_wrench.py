from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
OUT = (20, 22, 30)
STEEL = [(52, 58, 72), (84, 93, 110), (122, 133, 152), (166, 178, 198), (212, 222, 238)]
GRIP = [(110, 46, 22), (170, 76, 28), (222, 116, 42), (250, 168, 78)]

# силуэт: ключ по диагонали, головка справа сверху с раскрытым зевом
SIL = [
".........##..##.",
"........###..###",
"........###..###",
"........#######.",
".......########.",
".......#######..",
"......######....",
".....####.......",
"....###.........",
"...###..........",
"..###...........",
".###............",
".##.............",
"................",
"................",
"................",
]
# проверка: каждая строка 16
assert all(len(r) == 16 for r in SIL) and len(SIL) == 16
pts = {(x, y) for y, r in enumerate(SIL) for x, c in enumerate(r) if c == "#"}
im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
def has(x, y): return (x, y) in pts
for (x, y) in pts:
    up = not has(x, y - 1); left = not has(x - 1, y); down = not has(x, y + 1); right = not has(x + 1, y)
    k = 2
    if up or left: k += 1
    if (up and left): k += 1
    if down or right: k -= 1
    if (down and right): k -= 1
    # плавный перелив по диагонали: светлее сверху-слева, темнее снизу-справа
    k += 1 if (x + y) < 14 else -1 if (x + y) > 19 else 0
    k = max(0, min(4, k))
    col = STEEL[k]
    # рукоять: нижняя часть - оранжевая накладка
    if x <= 4 and y >= 9:
        gk = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3}[k]
        col = GRIP[gk]
    im.putpixel((x, y), (*col, 255))
for (x, y) in pts:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (x + dx, y + dy)
        if n not in pts and 0 <= n[0] < 16 and 0 <= n[1] < 16:
            im.putpixel(n, (*OUT, 255))
for (x, y, c) in ((9, 4, STEEL[4]), (10, 4, STEEL[3]), (12, 5, STEEL[0]), (11, 5, STEEL[1])):
    if (x, y) in pts:
        im.putpixel((x, y), (*c, 255))
im.save(ITEM / "wrench.png")
big = Image.new("RGBA", (16 * 12 + 20 + 16 * 3, 16 * 12 + 20), (139, 139, 139, 255))
big.alpha_composite(im.resize((192, 192), 0), (10, 10))
big.alpha_composite(im, (214, 10)); big.alpha_composite(im.resize((32, 32), 0), (214, 40))
big.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/wrench_big.png")
