"""Текстуры деталей для крафта машин 16x16 в стиле модулей и ключа: диагональная подсветка, фаски, контактные штырьки."""
import math
from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
MODELS = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/models/item")
OUT = (22, 26, 36)
# рампы от светлого к тёмному
PCB = [(106, 176, 138), (62, 128, 98), (38, 92, 72), (24, 62, 52), (14, 36, 34)]
GOLD = [(255, 240, 168), (250, 206, 84), (150, 102, 26), (96, 62, 16)]
CHIP = [(96, 106, 130), (66, 74, 92), (44, 50, 64), (28, 32, 42), (14, 16, 22)]
STEEL = [(226, 232, 244), (174, 184, 202), (124, 134, 154), (84, 92, 110), (50, 56, 70)]
COPPER = [(255, 196, 120), (226, 138, 70), (172, 92, 44), (116, 58, 30), (72, 34, 20)]
RED = [(255, 160, 130), (224, 76, 64), (172, 44, 44), (110, 26, 30)]
BLUE = [(190, 230, 255), (110, 170, 240), (54, 106, 196), (30, 62, 134)]
VIO = [(240, 214, 255), (186, 130, 244), (128, 68, 200), (74, 34, 128)]
ORANGE = [(255, 232, 140), (255, 170, 56), (226, 106, 24), (134, 54, 12)]
TAN = [(240, 218, 160), (208, 178, 116), (166, 138, 86), (122, 98, 60), (84, 66, 40)]
BAYER = [[0, 2], [3, 1]]

class Img:
    def __init__(self):
        self.px = {}

    def p(self, x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            self.px[(x, y)] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.p(x, y, c)

    def grad(self, x0, y0, x1, y1, ramp, lo=0.0, hi=1.0, vertical=False):
        """Диагональный градиент от светлого верхнего левого угла с шахматным смешением."""
        n = len(ramp)
        span = max(1, (x1 - x0) + (y1 - y0))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = ((y - y0) * 2 if vertical else (x - x0) + (y - y0)) / (span if not vertical else max(1, (y1 - y0) * 2))
                t = lo + (hi - lo) * min(1.0, max(0.0, t))
                f = t * (n - 1)
                i = int(f)
                frac = f - i
                if i < n - 1 and frac > (BAYER[y % 2][x % 2] + 0.5) / 4:
                    i += 1
                self.p(x, y, ramp[min(i, n - 1)])

    def box(self, x0, y0, x1, y1, ramp, rim=True):
        """Блок с градиентом и фаской: свет сверху-слева, тень снизу-справа."""
        self.grad(x0, y0, x1, y1, ramp, 0.25, 0.9)
        if rim:
            self.rect(x0, y0, x1, y0, ramp[0])
            self.rect(x0, y0, x0, y1, ramp[0] if len(ramp) < 5 else ramp[1])
            self.rect(x0, y1, x1, y1, ramp[-1])
            self.rect(x1, y0 + 1, x1, y1, ramp[-1] if len(ramp) < 5 else ramp[-2])

    def pins(self, x0, y0, x1, y1, step=2, gold=GOLD, sides="tblr", ends=True):
        for s in sides:
            if s in "tb":
                y = y0 - 1 if s == "t" else y1 + 1
                for x in range(x0 + 1, x1, step):
                    self.p(x, y, gold[1]); self.p(x, y - 1 if s == "t" else y + 1, gold[2]) if ends and False else None
            else:
                x = x0 - 1 if s == "l" else x1 + 1
                for y in range(y0 + 1, y1, step):
                    self.p(x, y, gold[1])
        return self

    def save(self, name, sym=False):
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            im.putpixel((x, y), (*c, 255))
        outline_selective(im, set(self.px), sym)
        im.save(ITEM / f"{name}.png")

def outline_selective(im, filled, sym=False):
    """Контур как у Create: не чёрный, а тёмный оттенок цвета соседней детали; сверху-слева светлее."""
    for y in range(16):
        for x in range(16):
            if (x, y) in filled:
                continue
            near = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y + dy) in filled]
            if not near:
                continue
            cols = [im.getpixel(n)[:3] for n in near]
            r = sum(c[0] for c in cols) / len(cols)
            g = sum(c[1] for c in cols) / len(cols)
            b = sum(c[2] for c in cols) / len(cols)
            k = 0.5 if any(n in ((x, y + 1),) if sym else n in ((x + 1, y), (x, y + 1)) for n in near) else 0.34   # свет сверху-слева (у симметричных - только сверху)
            im.putpixel((x, y), (int(r * k + 6), int(g * k * 0.96 + 6), int(b * k * 1.08 + 14), 255))

def pcb(i, ramp=PCB, box=(2, 3, 13, 12)):
    i.box(*box, ramp)

def trace(i, pts, c):
    """Ломаная дорожка по точкам (шаги по вертикали/горизонтали/диагонали)."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay))
        for k in range(n + 1):
            i.p(round(ax + (bx - ax) * k / max(1, n)), round(ay + (by - ay) * k / max(1, n)), c)

def pad(i, x, y, c=None):
    c = c or GOLD
    i.p(x, y, c[0]); i.p(x + 1, y, c[1]); i.p(x, y + 1, c[1]); i.p(x + 1, y + 1, c[2])

def ic(i, x0, y0, x1, y1, pins_side="lr", step=2, pin=GOLD):
    for s in pins_side:
        if s in "lr":
            x = x0 - 1 if s == "l" else x1 + 1
            for y in range(y0 + 1, y1, step):
                i.p(x, y, pin[1])
        else:
            y = y0 - 1 if s == "t" else y1 + 1
            for x in range(x0 + 1, x1, step):
                i.p(x, y, pin[1])
    i.box(x0, y0, x1, y1, CHIP)

def circuit_blank():
    i = Img()
    i.box(1, 3, 14, 12, TAN[:4])
    for x, y in ((3, 5), (12, 5), (3, 10), (12, 10)):
        i.p(x, y, TAN[4])
    for x in range(5, 11, 2):
        i.p(x, 7, TAN[3]); i.p(x + 1, 8, TAN[3])
    return i

def circuit_board():
    i = Img(); pcb(i)
    t = GOLD[1]
    c = COPPER[1]
    trace(i, [(3, 5), (6, 5), (7, 6), (7, 9), (10, 9), (12, 7)], c)
    trace(i, [(3, 8), (5, 8), (6, 9), (6, 11)], c)
    trace(i, [(9, 4), (9, 6), (11, 6)], c)
    trace(i, [(12, 10), (9, 10), (8, 11)], c)
    for x, y in ((3, 5), (3, 8), (12, 7), (9, 4), (12, 10), (6, 11), (8, 11)):
        i.p(x, y, GOLD[0])
    for x, y in ((5, 6), (10, 8), (4, 10)):
        i.p(x, y, PCB[4])
    for x in (4, 6, 8, 10, 12):
        i.p(x, 12, GOLD[1])
    return i

def control_circuit():
    i = Img(); pcb(i)
    trace(i, [(3, 5), (5, 5), (6, 6)], COPPER[1])
    trace(i, [(3, 10), (5, 10), (6, 9)], COPPER[1])
    trace(i, [(12, 5), (10, 5), (9, 6)], COPPER[1])
    trace(i, [(12, 10), (10, 10), (9, 9)], COPPER[1])
    ic(i, 6, 6, 9, 9, "lr", 1)
    i.p(6, 6, CHIP[0]); i.p(7, 7, BLUE[1]); i.p(8, 7, BLUE[2])
    i.p(3, 4, RED[0]); i.p(4, 4, RED[1])
    i.rect(11, 3, 12, 3, TAN[1]); i.p(11, 3, TAN[0])
    for x in (4, 6, 8, 10, 12):
        i.p(x, 12, GOLD[1])
    return i

def processor_blank():
    i = Img()
    i.box(3, 3, 12, 12, TAN)
    i.box(5, 5, 10, 10, STEEL)
    i.grad(6, 6, 9, 9, BLUE, 0.1, 0.9)
    for k in (4, 6, 8, 10):
        i.p(k, 4, GOLD[1]); i.p(k, 11, GOLD[2]); i.p(4, k, GOLD[1]); i.p(11, k, GOLD[2])
    for x, y in ((3, 3),):
        i.p(x, y, TAN[0])
    return i

def processor():
    i = Img()
    ic(i, 3, 3, 12, 12, "tblr", 2)
    i.box(5, 5, 10, 10, STEEL)
    i.rect(6, 6, 9, 9, BLUE[2])
    i.rect(6, 6, 9, 6, BLUE[0]); i.rect(6, 6, 6, 9, BLUE[1])
    i.rect(9, 7, 9, 9, BLUE[3]); i.rect(7, 9, 9, 9, BLUE[3])
    i.p(7, 7, BLUE[0]); i.p(8, 7, BLUE[1])
    i.p(4, 4, CHIP[0]); i.p(11, 11, GOLD[1]); i.p(10, 11, CHIP[4])
    return i

def plasma_controller():
    i = Img()
    ic(i, 3, 3, 12, 12, "tblr", 2, pin=VIO)
    i.box(5, 5, 10, 10, CHIP)
    i.rect(6, 6, 9, 9, VIO[3])
    i.rect(7, 7, 8, 8, VIO[1])
    i.p(7, 7, VIO[0]); i.p(6, 6, VIO[2]); i.p(9, 9, VIO[2]); i.p(9, 6, VIO[2]); i.p(6, 9, VIO[2])
    i.p(4, 4, VIO[1]); i.p(11, 4, VIO[1]); i.p(4, 11, VIO[1]); i.p(11, 11, VIO[1])
    return i

def winding():
    """Катушка: две стальные щеки с осью, между ними три витка медного провода (светлая середина, тёмные швы), выводы вниз. Симметрична."""
    i = Img()
    for y in range(2, 14):
        edge = STEEL[0] if y == 2 else STEEL[4] if y == 13 else None
        for x, k in ((2, 1), (3, 2), (12, 2), (13, 1)):
            i.p(x, y, edge if edge is not None else STEEL[k] if y < 8 else STEEL[min(4, k + 1)])
    i.p(1, 7, STEEL[1]); i.p(1, 8, STEEL[3]); i.p(14, 7, STEEL[1]); i.p(14, 8, STEEL[3])
    i.p(2, 7, STEEL[4]); i.p(2, 8, STEEL[4]); i.p(13, 7, STEEL[4]); i.p(13, 8, STEEL[4])
    shade = [0, 1, 1, 2, 2, 2, 3, 3, 4, 4]
    for y in range(3, 13):
        for x in range(4, 12):
            k = shade[y - 3]
            if x in (6, 9):
                k = min(4, k + 2)                       # шов между витками
            elif x in (5, 8, 10, 7) and False:
                pass
            i.p(x, y, COPPER[k])
    for x in (4, 5, 7, 8, 10, 11):                      # блик на каждом витке
        i.p(x, 4, COPPER[0])
    for x in (5, 10):                                   # выводы вниз
        i.p(x, 13, COPPER[2]); i.p(x, 14, COPPER[1])
    i.p(5, 14, STEEL[1]); i.p(10, 14, STEEL[1])
    return i

def magnet():
    """Брусковый магнит по диагонали: красная и синяя половины, серебряная середина и наконечники, виден торец."""
    i = Img()
    c = math.sqrt(0.5)
    def inside(x, y, ox, oy):
        u = ((x - ox - 7.5) + (7.5 - (y - oy))) * c      # вдоль бруска (вниз-влево -> вверх-вправо)
        v = ((y - oy - 7.5) + (x - ox - 7.5)) * c        # поперёк (верх-слева -> вниз-справа)
        return u, v
    HALF, W = 7.0, 2.7
    side = set(); face = {}
    for y in range(16):
        for x in range(16):
            u, v = inside(x, y, 1, 1)
            if abs(u) <= HALF and abs(v) <= W:
                side.add((x, y))
            u, v = inside(x, y, 0, 0)
            if abs(u) <= HALF and abs(v) <= W:
                face[(x, y)] = (u, v)
    for (x, y) in side - set(face):
        i.p(x, y, STEEL[4])
    for (x, y), (u, v) in face.items():
        t = (v + W) / (2 * W)                       # 0 - свет сверху, 1 - тень снизу
        ramp = None
        if u > 1.6:
            ramp = BLUE
        elif u < -1.6:
            ramp = RED
        if abs(u) > HALF - 1.1:                     # наконечники
            ramp = STEEL
            i.p(x, y, STEEL[0] if t < 0.35 else STEEL[1] if t < 0.7 else STEEL[2])
            continue
        if ramp is None:                            # серебряная середина
            i.p(x, y, STEEL[0] if t < 0.25 else STEEL[1] if t < 0.6 else STEEL[2])
            continue
        i.p(x, y, ramp[0] if t < 0.22 else ramp[1] if t < 0.55 else ramp[2] if t < 0.85 else ramp[3])
    return i

def power_module():
    i = Img()
    i.box(1, 4, 14, 13, STEEL)
    i.rect(2, 5, 6, 12, CHIP[3])
    for y in (6, 8, 10):
        i.rect(3, y, 5, y, ORANGE[1]); i.p(3, y, ORANGE[0])
    i.rect(8, 5, 13, 12, CHIP[3])
    i.rect(8, 5, 13, 5, CHIP[1])
    for x, y in ((11, 6), (10, 7), (10, 8), (11, 8), (12, 8), (11, 9), (10, 10), (11, 11)):
        i.p(x, y, ORANGE[0] if x == 11 else ORANGE[1])
    i.p(7, 5, STEEL[4]); i.p(7, 12, STEEL[4])
    for x in (4, 5, 10, 11):
        i.rect(x, 2, x, 3, COPPER[1]); i.p(x, 2, COPPER[0])
    i.p(1, 4, STEEL[0]); i.p(14, 13, STEEL[4])
    return i

def gear_drive():
    """Шестерня, зеркально-симметричная: 8 раздельных прямоугольных зубьев (один строго сверху), круглое тело, четыре отверстия и ступица.
    Зубья прямые и узкие, между ними просвет в два пикселя, чтобы силуэт читался в мелком формате."""
    i = Img()
    cx = cy = 7.5
    face = set()
    for y in range(16):
        for x in range(16):
            dx, dy = x - cx, y - cy
            if math.hypot(dx, dy) <= 4.1:
                face.add((x, y))
                continue
            for k in range(8):
                a = math.radians(-90 + 45 * k)
                ux, uy = math.cos(a), math.sin(a)
                along = dx * ux + dy * uy
                perp = abs(-dx * uy + dy * ux)
                if 3.0 <= along <= 6.4 and perp <= 1.35:
                    face.add((x, y))
                    break
    tooth_px = {p for p in face if math.hypot(p[0] - cx, p[1] - cy) > 4.1}
    for (x, y) in face:
        dx, dy = x - cx, y - cy
        k = 1 if dy < -1.5 else 2 if dy < 2.0 else 3                    # свет сверху, тень снизу: одинаково слева и справа
        if (x, y) in tooth_px:
            k = 0 if dy < 1.0 else 1
        if (x, y - 1) not in face:
            k = 0                                                       # верхняя кромка
        elif (x, y + 1) not in face:
            k = 3 if (x, y) not in tooth_px else 2                      # нижняя кромка
        if 3.0 <= math.hypot(dx, dy) < 3.7 and (x, y) not in tooth_px:
            k = min(4, k + 1)                                           # канавка у края тела
        i.p(x, y, STEEL[k])
    for hx, hy in ((5, 5), (10, 5), (5, 10), (10, 10)):                 # четыре отверстия
        i.p(hx, hy, STEEL[4])
    for y in range(6, 10):                                              # медная ступица 4x4 без углов
        for x in range(6, 10):
            if (x, y) in ((6, 6), (9, 6), (6, 9), (9, 9)):
                continue
            i.p(x, y, COPPER[0] if y == 6 else COPPER[1] if y == 7 else COPPER[2] if y == 8 else COPPER[3])
    for x, y in ((7, 7), (8, 7), (7, 8), (8, 8)):
        i.p(x, y, STEEL[1] if y == 7 else STEEL[3])                     # осевой болт
    return i

def precision_drive():
    i = Img()
    # цилиндр двигателя горизонтально: вертикальный градиент
    i.grad(2, 4, 10, 12, BLUE, 0.0, 1.0, vertical=True)
    i.rect(2, 4, 10, 4, BLUE[0]); i.rect(2, 12, 10, 12, BLUE[3])
    i.grad(1, 5, 2, 11, COPPER, 0.0, 1.0, vertical=True)
    i.rect(5, 5, 5, 11, BLUE[3])                                  # шов корпуса
    i.rect(3, 6, 4, 6, GOLD[0]); i.rect(3, 10, 4, 10, GOLD[2])    # энкодер
    i.rect(11, 7, 14, 9, STEEL[2]); i.rect(11, 7, 14, 7, STEEL[0]); i.rect(11, 9, 14, 9, STEEL[4])
    for x in (12, 14):
        i.p(x, 6, STEEL[1]); i.p(x, 10, STEEL[3])
    i.rect(8, 13, 9, 14, RED[1]); i.p(8, 13, RED[0])               # силовой провод
    i.p(6, 13, COPPER[2]); i.p(7, 14, COPPER[2])
    return i

def valve_block():
    i = Img()
    # труба с фланцами и корпус клапана
    i.grad(1, 9, 14, 12, STEEL, 0.0, 1.0, vertical=True)
    i.rect(1, 8, 2, 13, STEEL[2]); i.rect(1, 8, 1, 13, STEEL[0]); i.rect(2, 8, 2, 13, STEEL[3])
    i.rect(13, 8, 14, 13, STEEL[2]); i.rect(13, 8, 13, 13, STEEL[1]); i.rect(14, 8, 14, 13, STEEL[4])
    i.box(5, 6, 10, 13, STEEL)
    i.rect(7, 3, 8, 5, STEEL[3]); i.rect(7, 3, 7, 5, STEEL[1])        # шток
    i.rect(3, 1, 12, 2, RED[1]); i.rect(3, 1, 12, 1, RED[0]); i.rect(3, 2, 12, 2, RED[2])  # маховик
    i.p(2, 2, RED[3]); i.p(13, 2, RED[3])
    for x, y in ((1, 9), (1, 12), (14, 9), (14, 12)):
        i.p(x, y, STEEL[4])
    return i

def heat_plate():
    i = Img()
    i.box(1, 2, 14, 13, CHIP)
    i.grad(3, 4, 12, 11, [(58, 64, 80), (44, 50, 64), (30, 34, 46)], 0.0, 1.0)
    for x in (4, 7, 10):
        i.rect(x, 5, x + 1, 10, ORANGE[2])
        i.rect(x, 5, x, 10, ORANGE[1])
        i.rect(x, 7, x, 8, ORANGE[0])
        i.p(x + 1, 10, ORANGE[3])
    for x, y in ((2, 3), (13, 3), (2, 12), (13, 12)):
        i.p(x, y, STEEL[1])
    return i

NAMES = ["circuit_blank", "circuit_board", "control_circuit", "processor_blank", "processor", "plasma_controller",
         "winding", "magnet", "power_module", "gear_drive", "precision_drive", "valve_block", "heat_plate"]
for name in NAMES:
    globals()[name]().save(name, sym=name in ("gear_drive", "winding"))
    (MODELS / f"{name}.json").write_text(
        '{\n  "parent": "minecraft:item/generated",\n  "textures": {\n    "layer0": "kontur:item/%s"\n  }\n}\n' % name)

sheet = ["wrench", "module_worker", "module_industrial", "module_peak"] + NAMES
big = Image.new("RGBA", (16 * len(sheet), 16), (60, 62, 68, 255))
for k, n in enumerate(sheet):
    big.alpha_composite(Image.open(ITEM / f"{n}.png").convert("RGBA"), (16 * k, 0))
big.resize((16 * len(sheet) * 6, 16 * 6), Image.NEAREST).save(
    "/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/components.png")
