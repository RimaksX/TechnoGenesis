"""Модули, покрытия панелей и радиаторы: по правилам ключа - тёмный контур, свет сверху-слева, 5 тонов материала, плавный
переход тона по всей форме (в том числе по рамке и фону детали), а не плоская заливка с деталями."""
from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
OUT = (22, 26, 36)

def tone(ramp, light):
    i = int(round(max(0.0, min(1.0, light)) * (len(ramp) - 1)))
    return ramp[i]

def diag(x, y, box):
    """Освещённость 1..0 по диагонали от верхнего левого угла рамки box=(x0,y0,x1,y1) к нижнему правому."""
    x0, y0, x1, y1 = box
    t = ((x - x0) / max(1, x1 - x0) + (y - y0) / max(1, y1 - y0)) / 2
    return 1.0 - 0.9 * t - 0.02

def finish(px, name):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pts = set(px)
    for (x, y), c in px.items():
        im.putpixel((x, y), (*c, 255))
    for (x, y) in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in pts and 0 <= n[0] < 16 and 0 <= n[1] < 16:
                im.putpixel(n, (*OUT, 255))
    im.save(ITEM / f"{name}.png")

def edge_light(x, y, x0, y0, x1, y1):
    """Добавка к освещённости у края формы: верх и лево светлее, низ и право темнее."""
    d = 0.0
    if y == y0: d += 0.22
    if x == x0: d += 0.18
    if y == y1: d -= 0.22
    if x == x1: d -= 0.18
    return d

# ---------------------------------------------------------------- модули
PCB = [(14, 36, 34), (24, 62, 52), (38, 92, 72), (62, 128, 98), (106, 176, 138)]
GOLD = [(96, 62, 16), (150, 102, 26), (206, 152, 44), (250, 206, 84), (255, 240, 168)]
DIES = {
    "worker": [(10, 44, 28), (22, 84, 52), (50, 160, 88), (110, 220, 140), (190, 255, 210)],
    "industrial": [(70, 38, 6), (140, 82, 12), (222, 152, 30), (250, 204, 76), (255, 240, 160)],
    "peak": [(14, 40, 100), (28, 70, 168), (60, 128, 232), (130, 190, 255), (206, 236, 255)],
}

def module(name, die, pips):
    px = {}
    box = (3, 3, 12, 12)
    for y in range(3, 13):
        for x in range(3, 13):
            px[(x, y)] = tone(PCB, diag(x, y, box) + edge_light(x, y, *box) * 0.8)
    # контакты по краям: те же 5 тонов золота, светлее сверху и слева
    for i in range(4, 12, 2):
        for (x, y, l) in ((i, 2, 0.88), (i, 13, 0.18), (2, i, 0.74), (13, i, 0.3)):
            px[(x, y)] = tone(GOLD, l - (0.1 if i > 7 else 0))
    # дорожки светлее платы на тон
    for (x, y) in ((10, 5), (10, 6), (9, 7), (10, 8)):
        px[(x, y)] = tone(PCB, diag(x, y, box) + 0.34)
    # кристалл 4x4 с собственным переходом
    dbox = (5, 5, 8, 8)
    for y in range(5, 9):
        for x in range(5, 9):
            px[(x, y)] = tone(die, diag(x, y, dbox) * 0.9 + 0.08 + edge_light(x, y, *dbox) * 0.5)
    # метки класса под кристаллом
    for i in range(pips):
        px[(6 + i * 2, 10)] = tone(die, 0.95)
        px[(6 + i * 2, 11)] = tone(die, 0.3)
    finish(px, f"module_{name}")

# ---------------------------------------------------------------- покрытия
FRAMES = {
    "coating_basic": [(30, 36, 52), (58, 68, 90), (94, 106, 132), (140, 154, 180), (196, 208, 230)],
    "coating_aluminum": [(66, 78, 100), (108, 122, 148), (156, 170, 194), (204, 216, 236), (242, 248, 255)],
    "coating_gold": [(88, 56, 14), (140, 92, 22), (196, 142, 36), (244, 196, 70), (255, 234, 150)],
}
CELLS = {
    "coating_basic": [(8, 14, 44), (16, 30, 84), (30, 54, 130), (56, 90, 180), (104, 140, 226)],
    "coating_aluminum": [(30, 46, 86), (56, 84, 134), (88, 124, 182), (134, 170, 218), (190, 216, 246)],
    "coating_gold": [(64, 38, 8), (112, 70, 16), (164, 112, 28), (214, 160, 48), (250, 206, 98)],
}

def coating(name):
    frame, cell = FRAMES[name], CELLS[name]
    px = {}
    box = (1, 3, 14, 12)
    cols = [(2, 4), (6, 8), (10, 12)]
    rows = [(4, 6), (8, 10)]
    cellmap = {}
    for (x0, x1) in cols:
        for (y0, y1) in rows:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    cellmap[(x, y)] = (x0, y0, x1, y1)
    for y in range(3, 13):
        for x in range(1, 15):
            L = diag(x, y, box)
            if x in (1, 14) or y in (3, 12):                    # рамка: свой переход и фаска
                px[(x, y)] = tone(frame, L + edge_light(x, y, 1, 3, 14, 12) * 0.7)
            elif (x, y) in cellmap:
                cx0, cy0, cx1, cy1 = cellmap[(x, y)]
                v = L * 0.85 + 0.05 + edge_light(x, y, cx0, cy0, cx1, cy1) * 0.45
                if x == cx0 + 1:
                    v += 0.28                                   # шина по центру элемента
                px[(x, y)] = tone(cell, v)
            else:                                               # зазоры: самый тёмный тон, но тоже с переходом
                px[(x, y)] = tone(cell, L * 0.3 - 0.05)
    finish(px, name)

# ---------------------------------------------------------------- радиаторы
RAD = {
    "copper": [(52, 26, 18), (102, 52, 30), (160, 90, 46), (210, 130, 70), (246, 188, 120)],
    "aluminum": [(46, 56, 78), (88, 102, 128), (136, 152, 178), (186, 200, 222), (234, 242, 254)],
    "titanium": [(30, 36, 56), (58, 68, 96), (94, 108, 144), (142, 158, 194), (200, 214, 242)],
}
FINS = {"copper": [3, 7, 11], "aluminum": [2, 5, 8, 11], "titanium": [2, 5, 8, 11]}

def radiator(name):
    ramp = RAD[name]
    px = {}
    top = 2
    box = (2, top, 13, 13)
    fins = set()
    for fx in FINS[name]:
        for y in range(3 if name == "titanium" else 2, 11):    # у титанового сверху тепловая трубка
            for x in (fx, fx + 1):
                fins.add((x, y))
    for (x, y) in fins:                                         # рёбра: свет слева, тень справа, светлее у верха
        fx = min(f for f in FINS[name] if f <= x)
        v = diag(x, y, box) * 0.8 + 0.14 + (0.2 if x == fx else -0.14)
        px[(x, y)] = tone(ramp, v)
    for y in range(11, 14):                                     # основание
        for x in range(2, 14):
            v = diag(x, y, box) * 0.8 + 0.1 + {11: 0.26, 12: 0.0, 13: -0.26}[y] + edge_light(x, y, 2, 11, 13, 13) * 0.3
            px[(x, y)] = tone(ramp, v)
    if name == "titanium":                                      # тепловая трубка поверх рёбер
        for x in range(2, 14):
            px[(x, 2)] = tone(ramp, diag(x, 2, box) * 0.8 + 0.3 + (0.12 if x % 2 == 0 else -0.06))
    finish(px, f"radiator_{name}")

if __name__ == "__main__":
    for n, d in DIES.items():
        module(n, d, {"worker": 1, "industrial": 2, "peak": 3}[n])
    for n in FRAMES:
        coating(n)
    for n in RAD:
        radiator(n)
    names = ["wrench", "module_worker", "module_industrial", "module_peak", "coating_basic", "coating_aluminum", "coating_gold",
             "radiator_copper", "radiator_aluminum", "radiator_titanium"]
    sh = Image.new("RGBA", (16 * len(names), 16), (70, 72, 80, 255))
    for i, n in enumerate(names):
        sh.alpha_composite(Image.open(ITEM / f"{n}.png").convert("RGBA"), (16 * i, 0))
    sh.resize((sh.width * 11, sh.height * 11), Image.NEAREST).save(
        "/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/items_v2.png")
