"""Текстуры радиаторов 16x16: ребристый теплоотвод на основании."""
from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
OUT = (22, 24, 31)
RAMPS = {
    "copper": [(96, 52, 30), (150, 86, 48), (204, 124, 66), (238, 170, 100)],
    "aluminum": [(86, 96, 108), (130, 142, 156), (178, 190, 204), (222, 230, 240)],
    "titanium": [(58, 66, 86), (92, 102, 128), (132, 144, 172), (180, 192, 220)],
}
FINS = {"copper": [3, 7, 11], "aluminum": [2, 5, 8, 11], "titanium": [2, 5, 8, 11]}

def build(name):
    ramp = RAMPS[name]
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = {}
    for fx in FINS[name]:
        for y in range(3, 11):
            for x in (fx, fx + 1):
                px[(x, y)] = ramp[3] if x == fx and y < 9 else ramp[2] if x == fx else ramp[1]
    for y in range(11, 14):                               # основание
        for x in range(2, 14):
            px[(x, y)] = ramp[3] if y == 11 else ramp[1] if y == 12 else ramp[0]
    if name == "titanium":                                # тепловая трубка поверх рёбер
        for x in range(2, 14):
            px[(x, 2)] = ramp[3] if x % 2 == 0 else ramp[2]
    pts = set(px)
    for (x, y), c in px.items():
        im.putpixel((x, y), (*c, 255))
    for (x, y) in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in pts and 0 <= n[0] < 16 and 0 <= n[1] < 16:
                im.putpixel(n, (*OUT, 255))
    im.save(ITEM / f"radiator_{name}.png")

for n in RAMPS:
    build(n)
big = Image.new("RGBA", (16 * 3, 16), (60, 62, 68, 255))
for i, n in enumerate(RAMPS):
    big.alpha_composite(Image.open(ITEM / f"radiator_{n}.png"), (16 * i, 0))
big.resize((16 * 3 * 12, 16 * 12), Image.NEAREST).save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/rad.png")
