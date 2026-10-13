"""Конструктор объёмных моделей машин (части-кубоиды + атлас текстур) в чистом стиле Mekanism:
спокойная серая сталь, плоские панели с тонкой рамкой, заклёпки, цветные акценты на функциональных деталях."""
import math
import random
from PIL import Image

TEXEL = 1             # сетка 16x16x16: 1 пиксель текстуры = 1 единица модели = 1 кубик
ATLAS = 64            # размер кадра атласа (степень двойки); выбирается автоматически
GRID = 1              # шаг координат деталей = один кубик
FACES = ("north", "south", "east", "west", "up", "down")

# ---------------------------------------------------------------- материалы

def clamp(v):
    return max(0, min(255, int(round(v))))


def sh(c, k):
    return tuple(clamp(v * k) for v in c)


def mixc(a, b, t):
    return tuple(clamp(a[i] * (1 - t) + b[i] * t) for i in range(3))


def tone(c, k):
    """Тон с разворотом оттенка: тени темнее и холоднее, света светлее и теплее (богатая градация вместо плоской заливки)."""
    if k >= 1.0:
        t = min(1.0, (k - 1.0) * 2.0)
        return mixc(c, (min(255, c[0] + 44), min(255, c[1] + 40), min(255, c[2] + 30)), t)
    t = min(1.0, (1.0 - k) * 1.7)
    return mixc(c, (c[0] * 0.5 + 6, c[1] * 0.52 + 8, c[2] * 0.62 + 14), t)


STEEL = (118, 120, 124)
DARK = (58, 60, 64)
LIGHT = (160, 162, 166)
RUBBER = (36, 37, 40)
COPPER = (178, 100, 62)
RED_NEEDLE = (196, 52, 48)
BRASS = (190, 160, 70)
GLASS = (150, 200, 220)

MATS = {
    "steel": STEEL, "dark": DARK, "light": LIGHT, "rubber": RUBBER, "copper": COPPER, "brass": BRASS,
}


def _noise(w, h, seed, amp=0):
    r = random.Random(seed)
    return [[r.uniform(-amp, amp) for _ in range(w)] for _ in range(h)]



# Базовые цвета материалов. В рисунке нет света и теней: один тон, контур в 1 пиксель и небольшой разброс
# яркости по пикселям, чтобы поверхность не была абсолютно ровной.
RAMPS = {
    "casing": dict(f=(66, 68, 74)),
    "steel": dict(f=(118, 120, 124)),
    "dark": dict(f=(58, 60, 64)),
    "light": dict(f=(160, 162, 166)),
    "copper": dict(f=(178, 100, 62)),
    "rubber": dict(f=(36, 37, 40)),
    "brass": dict(f=(190, 160, 70)),
}


def ramp_of(rgb):
    return dict(f=rgb)


_STEPS = (0.95, 1.0, 1.05)


def jitter(x, y, seed):
    """Небольшой ступенчатый разброс яркости пикселя (детерминированный)."""
    h = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return _STEPS[(h >> 7) % 3]


def plate(put, w, h, R, seed=0):
    base = R["f"]
    for y in range(h):
        for x in range(w):
            c = base
            if w >= 3 and h >= 3 and min(x, y, w - 1 - x, h - 1 - y) == 0:
                c = sh(base, 0.78)
            put(x, y, sh(c, jitter(x, y, seed)))


def sym_lines(n, step):
    """Индексы линий сетки на отрезке длиной n: обе кромки и равномерные внутренние линии, зеркально симметричные."""
    out = {0, n - 1}
    m = max(1, int(round((n - 1) / float(step))))
    if n % 2 == 0 and m % 2 == 0:                       # у чётной длины центральная линия удвоилась бы в толстый шов
        m += 1
    for i in range(1, m):
        p = int((i * (n - 1)) / float(m) + 0.5)
        out.add(p)
        out.add(n - 1 - p)
    return out


def paint_face(mat, w, h, seed=0, frame=None, detail=True):
    """Рисует одну грань w×h (как видна снаружи). mat: имя или (имя, параметры)."""
    if callable(mat):
        mat = mat(frame)
    name, arg = (mat, None) if isinstance(mat, str) else (mat[0], mat[1])
    if name == "crop":                        # кусок грани большой детали: рисуем её целиком и вырезаем свой участок
        inner, ox, oy, fw, fh, fseed = arg
        full = paint_face(inner, fw, fh, fseed, frame)
        return full.crop((ox, oy, ox + w, oy + h))
    img = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    px = img.load()
    base = arg[0] if name == "panel" else MATS.get(name, STEEL)
    ramp = ramp_of(arg[0]) if name == "panel" else RAMPS.get(name)
    nz = _noise(w, h, seed)

    def put(x, y, c, a=255):
        if 0 <= x < w and 0 <= y < h:
            px[x, y] = (*c[:3], a)

    if name == "port":                        # гнездо разъёма 6x6 пикселей по центру грани: фаска, тёмный зазор, контакты
        img = paint_face(arg[0], w, h, seed, frame)
        px2 = img.load()
        x0, y0 = (w - 6) // 2, (h - 6) // 2
        for j in range(6):
            for i in range(6):
                edge = min(i, j, 5 - i, 5 - j)
                if edge == 0:                 # внешний кант с фаской: верх и лево светлее, низ и право темнее
                    k = 1.12 if (j == 0 or i == 0) and not (i == 5 or j == 5) else 0.86 if (i == 5 or j == 5) else 1.0
                    c = sh((150, 146, 138), k)
                elif edge == 1:
                    c = (46, 47, 51)
                else:                         # центр 2x2: контакты с лёгким блеском
                    c = ((78, 80, 86), (30, 31, 35), (26, 27, 30), (38, 39, 43))[(j - 2) * 2 + (i - 2)]
                px2[x0 + i, y0 + j] = (*c, 255)
        return img
    if name == "eport":                       # энергетический разъём: то же гнездо с приглушённой медной молнией
        img = paint_face(arg[0], w, h, seed, frame)
        px2 = img.load()
        x0, y0 = (w - 6) // 2, (h - 6) // 2
        for j in range(6):
            for i in range(6):
                edge = min(i, j, 5 - i, 5 - j)
                if edge == 0:
                    k = 1.12 if (j == 0 or i == 0) and not (i == 5 or j == 5) else 0.86 if (i == 5 or j == 5) else 1.0
                    c = sh((150, 146, 138), k)
                else:
                    c = (46, 47, 51) if edge == 1 else (32, 30, 26)
                px2[x0 + i, y0 + j] = (*c, 255)
        for (i, j, c) in ((3, 1, (196, 150, 84)), (3, 2, (176, 134, 76)), (2, 3, (176, 134, 76)), (2, 4, (150, 114, 66))):
            px2[x0 + i, y0 + j] = (*c, 255)
        return img
    if name == "view":                        # окно с жидкостью: arg=(слои, кадр); слой=(от,до,rgb|("glow",rgb)) доли снизу
        layers, fr = arg
        for y in range(h):
            for x in range(w):
                put(x, y, (26, 40, 46))
        inner_h = max(1, h - 2)
        liquid = {}
        for (f0, f1, spec) in layers:
            ya = 1 + inner_h - int(round(inner_h * f1)); yb = 1 + inner_h - int(round(inner_h * f0))
            for y in range(max(1, ya), min(h - 1, yb)):
                for x in range(1, w - 1):
                    if isinstance(spec, tuple) and spec and spec[0] == "glow":
                        k = 1.0 if fr is not None else 0.5
                        dark = fr is not None and ((y + fr) % 3 == 0)
                        put(x, y, sh(spec[1], k * (0.7 if dark else 1.05)))
                    else:
                        put(x, y, sh(spec, 1.0 + (0.1 if y == max(1, ya) else 0)))
                        liquid[(x, y)] = spec
        if fr is not None and w >= 5 and h >= 5:                       # пузырьки поднимаются вверх, на каждом кадре выше
            for k in range(max(1, (w - 2) // 3)):
                bx = 1 + (k * 5 + 2) % (w - 2)
                by = (h - 2) - ((fr * 2 + k * 3) % max(1, h - 2))
                if (bx, by) in liquid:
                    put(bx, by, sh(liquid[(bx, by)], 1.35))
        for x in range(w):
            put(x, 0, (96, 100, 108)); put(x, h - 1, (96, 100, 108))
        for y in range(h):
            put(0, y, (96, 100, 108)); put(w - 1, y, (96, 100, 108))
        if w >= 5 and h >= 5:                                           # блик на стекле: короткая светлая диагональ слева сверху
            for i in range(min(3, h - 3)):
                x, y = 1 + i, 1 + (min(3, h - 3) - 1 - i)
                if 0 < x < w - 1 and 0 < y < h - 1:
                    r_, g_, b_, a_ = px[x, y]
                    px[x, y] = (min(255, r_ + 38), min(255, g_ + 38), min(255, b_ + 38), a_)
        if w >= 6 and h >= 7:                                           # шкала уровня справа: короткие деления через два пикселя
            for y in range(2, h - 2, 2):
                put(w - 2, y, (150, 156, 164))
        return img
    if name == "console":                     # arg=(лампы[(rgb,вкл)], rgb экрана|None, кадр)
        lamps, scr, fr = arg
        for y in range(h):
            for x in range(w):
                put(x, y, DARK)
        for x in range(w):
            put(x, 0, sh(DARK, 0.6)); put(x, h - 1, sh(DARK, 0.6))
        for y in range(h):
            put(0, y, sh(DARK, 0.6)); put(w - 1, y, sh(DARK, 0.6))
        ly = h // 2
        for i, (rgb, on) in enumerate(lamps):
            put(1 + 2 * i, ly, rgb if on else sh(rgb, 0.3))
        if scr is not None:
            sx = 2 + 2 * len(lamps)
            for y in range(1, h - 1):
                for x in range(sx, w - 1):
                    put(x, y, (20, 24, 26))
            for y in range(1, h - 1):
                n = (w - 1 - sx) if fr is None else 1 + ((y * 3 + fr * 2) % max(1, w - 2 - sx))
                for x in range(sx, min(w - 1, sx + n)):
                    put(x, y, scr if fr is not None else sh(scr, 0.35))
        return img
    if name == "hull":                        # клёпаный корпус: arg=(rgb[, шаг шва]); фаска, вертикальный градиент, швы и заклёпки
        base = arg[0]
        step = arg[1] if len(arg) > 1 else 8
        for y in range(h):
            for x in range(w):
                t = y / max(1, h - 1)
                k = 1.08 - 0.20 * t
                c = sh(base, k * jitter(x, y, seed))
                seam_x = step > 0 and w > step and x % step == step - 1 and 0 < x < w - 1
                seam_y = step > 0 and h > step and y % step == step - 1 and 0 < y < h - 1
                if seam_x or seam_y:
                    c = sh(base, 0.66)
                elif (step > 0 and w > step and x % step == 0 and x > 0) or (step > 0 and h > step and y % step == 0 and y > 0):
                    c = sh(base, 1.16)
                if seam_x and seam_y:
                    c = sh(base, 1.34)                                         # заклёпка на пересечении швов
                if x == 0 or y == 0:
                    c = sh(base, 1.26)
                if x == w - 1 or y == h - 1:
                    c = sh(base, 0.58)
                put(x, y, c)
        return img
    if name == "tube":                        # труба или цилиндрический бак: arg=(rgb, 'v'|'h'[, шаг колец]); блик смещён влево/вверх
        base, axis = arg[0], arg[1]
        ring = arg[2] if len(arg) > 2 else 0
        n = w if axis == "v" else h
        for y in range(h):
            for x in range(w):
                pos = (x if axis == "v" else y)
                u = (pos + 0.5) / n
                k = 0.50 + 0.80 * math.sin(math.pi * min(1.0, max(0.0, u * 0.86 + 0.07))) ** 1.6
                c = sh(base, k * jitter(x, y, seed))
                along = (y if axis == "v" else x)
                if ring and along % ring in (0, 1):
                    c = sh(c, 0.62 if along % ring == 1 else 1.12)
                put(x, y, c)
        return img
    if name == "winding":                     # обмотка с хомутами: arg=(rgb медного провода, 'v'|'h')
        base, axis = arg[0], arg[1]
        n = w if axis == "v" else h
        for y in range(h):
            for x in range(w):
                pos = (x if axis == "v" else y)
                along = (y if axis == "v" else x)
                u = (pos + 0.5) / n
                k = 0.55 + 0.75 * math.sin(math.pi * min(1.0, max(0.0, u * 0.86 + 0.07)))
                turn = along % 3
                c = sh(base, k * (1.0 if turn != 2 else 0.64))
                if along % 12 in (0, 1, 2) and along > 1:
                    c = sh((96, 100, 110), (0.8 + 0.3 * math.sin(math.pi * u)) if along % 12 != 2 else 0.5)   # стальной хомут
                put(x, y, c)
        return img
    if name == "deck":                        # рифлёный настил: arg=(rgb,)
        base = arg[0] if arg else (96, 100, 108)
        for y in range(h):
            for x in range(w):
                diag = ((x + y) % 4 == 0) or ((x - y) % 4 == 0)
                put(x, y, sh(base, (1.18 if diag else 0.86) * jitter(x, y, seed)))
        for x in range(w):
            put(x, 0, sh(base, 1.3)); put(x, h - 1, sh(base, 0.55))
        for y in range(h):
            put(0, y, sh(base, 1.3)); put(w - 1, y, sh(base, 0.55))
        return img
    if name == "grille":                      # решётка: тёмные щели и светлые рёбра по горизонтали или вертикали; arg=(rgb, 'v'|'h')
        base, axis = (arg[0], arg[1]) if arg else ((120, 124, 132), "h")
        for y in range(h):
            for x in range(w):
                pos = y if axis == "h" else x
                c = sh(base, 0.28) if pos % 3 == 2 else sh(base, 1.15) if pos % 3 == 0 else sh(base, 0.82)
                if x in (0, w - 1) or y in (0, h - 1):
                    c = sh(base, 1.2 if (x == 0 or y == 0) else 0.55)
                put(x, y, c)
        return img
    if name == "lamps":                       # ряд сигнальных ламп на тёмной планке: arg=(rgb, кадр)
        rgb, fr = arg
        for y in range(h):
            for x in range(w):
                put(x, y, (30, 32, 38))
        for i in range(1, w - 1, 3):
            on = fr is None or ((i // 3 + fr) % 2 == 0)
            c = rgb if (fr is not None and on) else sh(rgb, 0.4)
            for dy in range(max(1, h // 2 - 1), min(h - 1, h // 2 + 1)):
                put(i, dy, c); put(i + 1 if i + 1 < w - 1 else i, dy, c)
        return img
    if name == "fan":                         # вентилятор в круглом кожухе с решёткой: arg=(rgb лопастей, число лопастей, кадр)
        blade, n, fr = arg
        n = max(n, 7) if min(w, h) >= 12 else n                                 # 7 лопастей: симметрия не даёт «крест»
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        r = min(w, h) / 2.0
        phase = 0.0 if fr is None else fr * (2 * math.pi / n) / 4.0
        for y in range(h):
            for x in range(w):
                put(x, y, (26, 28, 34))
        for y in range(h):
            for x in range(w):
                if x == 0 or y == 0:
                    put(x, y, (84, 88, 98))
                elif x == w - 1 or y == h - 1:
                    put(x, y, (38, 40, 46))
        for y in range(h):
            for x in range(w):
                dx, dy = x - cx, y - cy
                d = math.hypot(dx, dy)
                if d > r - 1.2:
                    continue
                if d > r - 2.6:                                                 # кожух: свет сверху слева
                    lit = 1.0 + 0.5 * (-(dx + dy) / (2 * r))
                    put(x, y, tone((120, 126, 138), lit))
                    continue
                if d < max(2.0, r * 0.17):                                      # ступица
                    put(x, y, (40, 42, 48) if d < max(1.0, r * 0.08) else tone((150, 154, 164), 1.0 + 0.3 * (-(dx + dy) / (2 * r)) * 3))
                    continue
                a = math.atan2(dy, dx) + phase - 1.25 * d / r                   # лопасти закручены к краю
                t = (a / (2 * math.pi / n)) % 1.0
                if t < 0.62:
                    k = 1.18 - 0.55 * (t / 0.62) - 0.18 * (d / r)               # светлая передняя кромка, к задней темнее
                    c = tone(blade, k)
                else:
                    c = (20, 22, 28)
                gd = abs(d - r * 0.58)
                spoke = min(abs(dx), abs(dy)) < 0.55 or abs(abs(dx) - abs(dy)) < 0.55
                if gd < 0.55:                                                   # решётка: кольцо
                    c = tone(c, 0.72)
                put(x, y, c)
        return img
    if name == "hotwin":                      # окно с раскалённой изнутри плазмой: arg=(rgb, кадр); выключено - тёмное стекло
        rgb, fr = arg
        for y in range(h):
            for x in range(w):
                edge = x in (0, w - 1) or y in (0, h - 1)
                if edge:
                    put(x, y, (40, 42, 48))
                elif fr is None:
                    put(x, y, (26, 28, 34) if (x + y) % 5 else (34, 36, 44))
                else:
                    k = 0.78 + 0.22 * math.sin((x * 0.9 + y * 0.6) + fr * 1.57)
                    c = sh(rgb, k)
                    if min(x, w - 1 - x, y, h - 1 - y) >= 2:
                        c = mixc(c, (255, 244, 210), 0.45)
                    put(x, y, c)
        return img
    if name == "pane":                        # стеклянная панель в раме: arg=(rgb стекла, прозрачность)
        glass, alpha = arg if arg else (GLASS, 70)
        for y in range(h):
            for x in range(w):
                edge = x in (0, w - 1) or y in (0, h - 1)
                put(x, y, (88, 94, 104) if edge else glass, 255 if edge else alpha)
        for i in range(min(4, w - 2, h - 2)):
            put(1 + i, 1 + i, (235, 245, 250), 150)                             # блик по диагонали
        return img
    if name == "brick":                       # огнеупорный кирпич: arg=(rgb кирпича,); рисунок бесшовно повторяется по 16 пикселей
        base = arg[0] if arg else (150, 70, 52)
        tones = (0.90, 1.0, 1.08, 0.96)
        for y in range(h):
            row = y // 4
            for x in range(w):
                off = 4 if row % 2 else 0
                col = (x + off) // 8
                if y % 4 == 0 or (x + off) % 8 == 0:
                    put(x, y, (58, 40, 38))                                     # раствор: сверху и слева от каждого кирпича
                else:
                    k = tones[(col % 2 * 2 + row % 2) % 4]
                    shade = 1.12 if y % 4 == 1 else 0.88 if y % 4 == 3 else 1.0
                    put(x, y, sh(base, k * shade * jitter(x, y, seed)))
        return img
    if name in ("corrug", "tread", "cast", "tiles", "paneled", "ribs"):
        # узоры подогнаны к размерам грани: всё считается от ближайшей кромки и зеркально симметрично, свет сверху слева,
        # перепад яркости небольшой, ярких одиночных точек нет
        base = arg[0] if arg else (130, 134, 144)
        vl = set(sym_lines(w, 8 if name == "paneled" else 4)) if w > 4 else {0, w - 1}
        hl = set(sym_lines(h, 8 if name == "paneled" else 4)) if h > 4 else {0, h - 1}
        for y in range(h):
            for x in range(w):
                ex, ey = min(x, w - 1 - x), min(y, h - 1 - y)
                k = 1.0
                if name == "corrug":
                    k = (1.07, 1.0, 0.9, 0.97)[ex % 4]
                elif name == "tread":
                    d = (ex + ey) % 4 if (ex // 4 + ey // 4) % 2 == 0 else (ex - ey) % 4
                    k = 1.07 if d == 0 else 0.92 if d == 2 else 1.0
                elif name == "cast":
                    k = 0.97 + 0.03 * ((x * 7 + y * 13 + seed) % 3 - 1) * 2
                    hh = ((x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)) & 0xFFFF
                    if hh % 29 == 0:
                        k = 0.86
                elif name == "tiles":
                    k = 0.88 if (x in vl or y in hl) else 1.0
                    if x - 1 in vl and y - 1 in hl:
                        k = 1.05
                elif name == "paneled":
                    if x in vl or y in hl:
                        k = 0.9 if (x >= w // 2 or y >= h // 2) else 1.06
                    elif (x - 1 in vl or x + 1 in vl) and (y - 1 in hl or y + 1 in hl):
                        k = 0.92                                              # винты по углам плиты
                elif name == "ribs":
                    k = (1.07, 1.03, 0.88, 0.97, 0.98, 1.0)[ey % 6]
                if x == 0 or y == 0:
                    k *= 1.04
                if x == w - 1 or y == h - 1:
                    k *= 0.9
                put(x, y, sh(sh(base, k), jitter(x, y, seed)))
        return img
    if name == "pipe":                        # гладкий бок трубы: arg=(rgb, уровень света); лёгкий растр, без полос
        base, lvl = arg
        for y in range(h):
            for x in range(w):
                k = lvl + 0.03 * ((x + y) % 2 - 0.5)
                put(x, y, tone(base, k))
        return img
    if name == "slats":                       # пластины радиатора: каждая со светлой кромкой, телом и тенью; arg=(rgb,)
        base = arg[0] if arg else (110, 114, 124)
        for y in range(h):
            for x in range(w):
                ey = y % 4 if (h % 4 == 0 or y < h - h % 4) else (y - (h - h % 4))
                k = (1.08, 1.03, 0.95, 0.8)[ey % 4]
                if x == 0:
                    k *= 1.05
                elif x == w - 1:
                    k *= 0.88
                put(x, y, tone(base, k))
        return img
    if name == "shade":                       # плавный свет по грани: сверху слева светлее, снизу справа темнее, 5 тонов с растром
        inner, amp = arg
        base_img = paint_face(inner, w, h, seed, frame)
        bp = base_img.load()
        step = 0.04
        bayer = ((0.0, 0.5), (0.75, 0.25))
        for y in range(h):
            for x in range(w):
                r, g, b, a = bp[x, y]
                if a == 0:
                    continue
                gd = (x / max(1, w - 1) + y / max(1, h - 1)) / 2.0
                k = 1.0 + amp * (0.5 - gd) * 2.0
                kk = k / step
                q = int(kk // 1) + (1 if (kk % 1.0) > bayer[y % 2][x % 2] else 0)
                kq = q * step
                kq = max(1.0 - 2 * step, min(1.0 + 2 * step, kq))
                put(x, y, tone((r, g, b), kq), a)
        return img
    if name == "wind2":                       # провод в витках: тёмный край, середина, блик, середина; arg=(rgb, 'v'|'h')
        base, axis = (arg[0], arg[1]) if arg else ((184, 108, 66), "v")
        prof = (0.84, 0.98, 1.08, 1.0)
        for y in range(h):
            for x in range(w):
                pos = y if axis == "v" else x
                ed = min(pos, (h if axis == "v" else w) - 1 - pos)
                k = prof[ed % 4]
                oth = x if axis == "v" else y
                if oth == 0:
                    k *= 1.04
                elif oth == (w if axis == "v" else h) - 1:
                    k *= 0.88
                put(x, y, tone(base, k))
        return img
    if name == "melt":                        # ковш: arg=(кадр,); пустой - тёмная футеровка с ободком, работающий - раскалённая ванна
        fr = arg[0] if arg else None
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        rr = max(1.0, min(w, h) / 2.0)
        for y in range(h):
            for x in range(w):
                d = max(abs(x - cx), abs(y - cy)) / rr                          # 0 в центре, 1 у края
                rim = min(x, y, w - 1 - x, h - 1 - y)
                if rim == 0:
                    put(x, y, tone((70, 66, 72), 1.1 if (x == 0 or y == 0) else 0.8))
                    continue
                if rim == 1:
                    put(x, y, tone((54, 50, 56), 1.0))
                    continue
                if fr is None:
                    k = 1.06 - 0.5 * d + 0.05 * math.sin(x * 1.3 + y * 0.8)
                    put(x, y, tone((60, 50, 50), k) if d > 0.45 else tone((84, 52, 40), 1.0 + 0.2 * (0.45 - d)))
                else:
                    v = math.sin(x * 0.9 + y * 0.5 + fr * 1.3) + math.sin(y * 1.1 - x * 0.4 - fr * 0.9)
                    heat = 1.0 - d * 0.75 + 0.12 * v
                    cols = ((150, 50, 26), (226, 100, 32), (250, 160, 56), (255, 212, 120), (255, 240, 190))
                    put(x, y, cols[max(0, min(4, int(heat * 5)))])
        return img
    if name == "louver":                      # жалюзи: arg=(rgb,)
        base = arg[0] if arg else (120, 124, 132)
        for y in range(h):
            for x in range(w):
                put(x, y, sh(base, 1.15) if y % 4 == 0 else sh(base, 0.5) if y % 4 == 3 else sh(base, 0.9))
        return img
    if name == "mouth":                       # зев печи с огнём: arg=(кадр,)
        fr = arg[0] if arg else None
        for y in range(h):
            for x in range(w):
                put(x, y, (20, 15, 15))
        cx = (w - 1) / 2.0
        for y in range(h):
            for x in range(w):
                arch = y >= 1 + (abs(x - cx) / max(1.0, cx)) ** 2 * (h * 0.32)
                if not (arch and 1 <= x <= w - 2 and y <= h - 2):
                    continue
                if fr is None:                                                  # остывшая топка: угли
                    k = (x * 7 + y * 13) % 11
                    put(x, y, (86, 30, 22) if k == 0 and y > h * 0.6 else (44, 26, 24) if y > h * 0.5 else (30, 20, 20))
                    continue
                ph = fr * math.pi / 2
                tongue = 0.50 + 0.30 * (math.sin(x * 0.95 + ph) + math.sin(x * 0.52 - ph * 1.3)) / 2
                dist = (h - 2 - y) / max(1.0, (h - 2) * tongue)                 # 0 у пода, 1 на кончике языка
                glow = 1.0 - (h - 2 - y) / max(1.0, h - 2.0)
                if dist < 1.0 and not (dist > 0.85 and (x + y + fr) % 2):
                    c = (255, 244, 190) if dist < 0.2 else (255, 205, 80) if dist < 0.45 else (255, 130, 36) if dist < 0.75 else (206, 64, 24)
                else:
                    c = sh((120, 40, 22), 0.5 + 0.7 * glow)                     # отсвет на кладке за языками
                put(x, y, c)
        for x in range(w):
            put(x, 0, (92, 96, 106)); put(x, 1, (58, 60, 66))
        return img
    if name in ("weld", "ribbed", "sieve", "insul", "bolts", "cloth", "coil"):   # фактурные материалы: arg=(rgb,)
        base = arg[0] if arg else COPPER
        edge_dark = name not in ("coil",)
        for y in range(h):
            for x in range(w):
                c = base
                edge = w >= 3 and h >= 3 and min(x, y, w - 1 - x, h - 1 - y) == 0
                if name == "weld":                # сварные листы: поперечный шов каждые 6 строк с заклёпками
                    my, mx = min(y, h - 1 - y), min(x, w - 1 - x)
                    if h >= 8 and 0 < x < w - 1:
                        if my % 6 == 2:
                            c = sh(base, 0.86)
                            if mx % 4 == 2:
                                c = sh(base, 1.08)
                        elif my % 6 == 3:
                            c = sh(base, 1.04)
                elif name == "ribbed":            # вертикальные рёбра радиатора
                    c = sh(base, (1.1, 1.0, 0.8)[min(x, w - 1 - x) % 3])
                elif name == "sieve":             # перфорация
                    if min(x, w - 1 - x) % 2 == 1 and min(y, h - 1 - y) % 2 == 1 and 0 < x < w - 1 and 0 < y < h - 1:
                        c = sh(base, 0.4)
                elif name == "insul":             # керамический изолятор с юбками
                    c = sh(base, 0.8 if min(y, h - 1 - y) % 3 == 0 else 1.06)
                elif name == "bolts":             # болты по углам и серединам кромок
                    pts = {(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)}
                    if w >= 10:
                        pts |= {(w // 2, 1), (w // 2, h - 2)}
                    if h >= 10:
                        pts |= {(1, h // 2), (w - 2, h // 2)}
                    if (x, y) in pts and w >= 4 and h >= 4:
                        c = sh(base, 1.35)
                elif name == "cloth":             # фильтровальная ткань в раме: светлая кромка и складки по центру
                    if min(x, y, w - 1 - x, h - 1 - y) < 2:
                        c = sh(base, 1.12)
                    else:
                        c = sh(base, 0.8 if min(x, w - 1 - x) % 2 == 0 else 0.9)
                elif name == "coil":              # обмотка: поперечные витки
                    c = sh(base, 1.1 if min(y, h - 1 - y) % 2 == 0 else 0.84)
                    if x == 0 or x == w - 1:
                        c = sh(base, 0.68)
                if edge and edge_dark and name not in ("cloth", "bolts"):
                    c = sh(c, 0.82)
                if edge and name == "bolts":
                    c = sh(base, 0.78)
                put(x, y, sh(c, jitter(x, y, seed)))
        return img
    if name == "liquid":                      # поверхность жидкости как ванильная вода: пятна тона rgb, плывущие по кадрам
        rgb, fr = arg
        k = 0 if fr is None else fr
        for y in range(h):
            for x in range(w):
                v = (math.sin(x * 0.85 + y * 0.42 + k * 0.9) + math.sin(y * 1.05 - x * 0.37 + k * 0.7)
                     + 0.6 * math.sin((x + y) * 0.55 - k * 1.1))
                lvl = (0.66, 0.76, 0.86, 0.96)[min(3, max(0, int((v + 2.2) / 4.4 * 4)))]
                put(x, y, sh(rgb, lvl))
        return img
    if name == "wiring":                      # щит с проводкой: arg=(rgb основы, число проводов); плоский рисунок проводов с изломами
        base = arg[0]
        n = arg[1] if len(arg) > 1 else 3
        for y in range(h):
            for x in range(w):
                c = base
                if w >= 3 and h >= 3 and min(x, y, w - 1 - x, h - 1 - y) == 0:
                    c = sh(base, 0.78)
                put(x, y, sh(c, jitter(x, y, seed)))
        palette = ((168, 66, 56), (70, 104, 170), (132, 138, 146), (176, 112, 66), (72, 140, 100))
        rnd = random.Random(seed * 7 + w * 3 + h)
        if w >= 6 and h >= 5:
            for k in range(n):
                col = palette[(k + seed) % len(palette)]
                y0 = 1 + rnd.randrange(0, max(1, h - 2))
                y1 = 1 + rnd.randrange(0, max(1, h - 2))
                xm_ = 2 + rnd.randrange(0, max(1, w - 4))
                for x in range(1, xm_ + 1):
                    put(x, y0, col)
                for y in range(min(y0, y1), max(y0, y1) + 1):
                    put(xm_, y, col)
                for x in range(xm_, w - 1):
                    put(x, y1, col)
                put(1, y0, sh(col, 1.35))
                put(w - 2, y1, sh(col, 1.35))
                put(xm_, y0, (210, 212, 206))
        return img
    if name == "pipework":                    # плоский рисунок трубок на стенке: arg=(rgb основы, rgb трубок)
        base, tube = arg[0], arg[1]
        for y in range(h):
            for x in range(w):
                c = base
                if w >= 3 and h >= 3 and min(x, y, w - 1 - x, h - 1 - y) == 0:
                    c = sh(base, 0.78)
                put(x, y, sh(c, jitter(x, y, seed)))
        rnd = random.Random(seed * 11 + w + h * 5)
        if w >= 6 and h >= 6:
            for k in range(2):
                ys = 2 + rnd.randrange(0, max(1, h - 4))
                xs = 2 + rnd.randrange(0, max(1, w - 4))
                for x in range(1, w - 1):
                    put(x, ys, tube)
                    put(x, ys + 1, sh(tube, 0.7)) if ys + 1 < h - 1 else None
                for y in range(1, h - 1):
                    put(xs, y, sh(tube, 1.1))
                put(xs, ys, (200, 204, 208))
        return img
    if name == "dial":                        # круглый манометр со стрелкой: arg=(rgb стрелки,)
        needle = arg[0] if arg else RED_NEEDLE
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        r = min(w, h) / 2.0
        for y in range(h):
            for x in range(w):
                put(x, y, (40, 42, 46))
        for y in range(h):
            for x in range(w):
                d = math.hypot(x - cx, y - cy)
                if d <= r - 0.2:
                    put(x, y, (112, 116, 124) if d > r - 1.2 else (214, 216, 210))
        steps = int(max(abs(cx), abs(cy)) * 1.4) + 1
        ang = math.radians(-50)
        for i in range(steps + 1):
            t = i / max(1, steps)
            x = int(round(cx + math.sin(ang) * t * (r - 1.6)))
            y = int(round(cy - math.cos(ang) * t * (r - 1.6)))
            put(x, y, needle)
        put(int(round(cx)), int(round(cy)), (40, 42, 46))
        return img
    if name == "belt":
        for y in range(h):
            for x in range(w):
                put(x, y, sh(RUBBER, 1.0 + (0.35 if min(y, h - 1 - y) % 4 == 0 else 0)))
        for y in range(h):
            put(0, y, sh(RUBBER, 0.6)); put(w - 1, y, sh(RUBBER, 0.6))
        return img
    if name == "lamp":                        # arg: (rgb, on)
        rgb, on = arg
        for y in range(h):
            for x in range(w):
                put(x, y, rgb if on else sh(rgb, 0.28))
        return img
    if name == "meter":                       # шкала заряда: arg=(уровень 0..5,); по центру, 5 секций по 2 пикселя
        lvl = arg[0] if arg else 0
        for y in range(h):
            for x in range(w):
                put(x, y, (18, 20, 22))
        inner = w - 2
        seg = max(1, inner // 5)
        left = 1 + (inner - seg * 5) // 2
        for i in range(5):
            for x in range(left + i * seg, left + (i + 1) * seg):
                for y in range(2 if h >= 6 else 1, h - 2 if h >= 6 else h - 1):
                    put(x, y, (96, 214, 120) if i < lvl else (40, 43, 48))
        for x in range(w):
            put(x, 0, LIGHT); put(x, h - 1, LIGHT)
        for y in range(h):
            put(0, y, LIGHT); put(w - 1, y, LIGHT)
        return img
    if name == "cells":                       # солнечные элементы: arg=(цвет ячейки, цвет разделителей, шаг сетки, рамка по бокам[, без горизонтальных линий])
        cell, line, step = arg[0], arg[1], arg[2]
        sides = arg[3] if len(arg) > 3 else True
        flat = arg[4] if len(arg) > 4 else False
        lx, ly = sym_lines(w, step), sym_lines(h, step)
        for y in range(h):
            for x in range(w):
                if flat:                          # узкая ступень: только вертикальные разделители, вся площадь - элементы
                    grid = x in lx
                    edge = False
                else:
                    edge = (min(y, h - 1 - y) == 0) or (sides and min(x, w - 1 - x) == 0)
                    grid = (x in lx) or (y in ly)
                dg = (min(x, w - 1 - x) + min(y, h - 1 - y)) % 3 - 1     # градация: плюс-минус 3, зеркально симметрична
                c = tuple(min(255, v + 10) for v in line) if edge else line if grid else tuple(clamp(v + 3 * dg) for v in cell)
                put(x, y, c)
        return img
    if name == "grate":
        for y in range(h):
            for x in range(w):
                put(x, y, DARK if (min(x, w - 1 - x) % 2 == 0) else sh(DARK, 0.6))
        return img
    if name == "hazard":                      # предупреждающая полоса
        for y in range(h):
            for x in range(w):
                put(x, y, (212, 176, 44) if ((x + y) // 2) % 2 == 0 else (30, 30, 34))
        return img
    if name == "glow":                        # arg: (rgb, frame): ровное свечение с тёмными полосами
        rgb, fr = arg
        for y in range(h):
            for x in range(w):
                dark = fr is not None and ((y + fr) % 3 == 0)
                k = 1.0 if fr is not None else 0.45
                c = sh(rgb, k * (0.62 if dark else 1.0))
                if fr is not None and not dark:
                    c = mixc(c, (255, 232, 160), 0.35)
                put(x, y, c)
        return img
    plate(put, w, h, ramp or RAMPS["steel"], seed)
    return img


# ---------------------------------------------------------------- модель

class Box:
    def __init__(self, a, b, mat, faces, rot=None, name=""):
        self.a, self.b, self.mat, self.faces, self.rot, self.name = a, b, mat, faces, rot, name

    def size(self):
        return (self.b[0] - self.a[0], self.b[1] - self.a[1], self.b[2] - self.a[2])


class Model:
    def __init__(self, mid):
        self.id = mid
        self.boxes = []
        self.glass = False   # прозрачных деталей нет: все модели cutout
        self.seed = abs(hash(mid)) % 1000

    def box(self, a, b, mat="steel", faces="nsewud", rot=None, name=""):
        fm = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"}
        fs = [fm[c] for c in faces]
        if isinstance(mat, (str, tuple)) or callable(mat):
            mats = {f: mat for f in fs}
        else:
            mat = {fm.get(k, k): v for k, v in mat.items()}
            mats = {f: mat.get(f, mat.get("*", "steel")) for f in fs}
        bx = Box(a, b, mats, fs, rot, name or f"p{len(self.boxes)}")
        self.boxes.append(bx)
        return bx

    # «Цилиндры» в ванильном стиле - прямые квадратные колонны без поворотов
    def cyl(self, axis, c1, c2, R, t0, t1, mat="steel", cap="steel", caps=True):
        """axis: 'y'|'x'|'z'. c1,c2 - центр в плоскости, t0..t1 - вдоль оси, R - половина стороны (с небольшим зазором)."""
        h = R * 0.9
        mat = "steel" if mat == "tube" else mat
        cap = "steel" if cap == "tube" else cap
        if axis == "y":
            A = [c1 - h, t0, c2 - h]; B = [c1 + h, t1, c2 + h]
            cap_faces, side_faces, capnames = "ud", "nsew", ("up", "down")
        elif axis == "x":
            A = [t0, c1 - h, c2 - h]; B = [t1, c1 + h, c2 + h]
            cap_faces, side_faces, capnames = "ew", "nsud", ("east", "west")
        else:
            A = [c1 - h, c2 - h, t0]; B = [c1 + h, c2 + h, t1]
            cap_faces, side_faces, capnames = "sn", "ewud", ("south", "north")
        bx = self.box(A, B, {"*": mat}, faces=side_faces + (cap_faces if caps else ""), name=f"col_{axis}")
        for f in capnames:
            if f in bx.mat:
                bx.mat[f] = cap
        return [bx]


def face_dims(bx, f):
    dx, dy, dz = bx.size()
    return {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}[f]


EPS = 1e-6
NORMAL = {"north": (2, -1), "south": (2, 1), "west": (0, -1), "east": (0, 1), "down": (1, -1), "up": (1, 1)}


def _plane(bx, f):
    ax, sg = NORMAL[f]
    return ax, (bx.b[ax] if sg > 0 else bx.a[ax])


def _rect(bx, f):
    ax, _ = NORMAL[f]
    others = [i for i in range(3) if i != ax]
    return others, [(bx.a[i], bx.b[i]) for i in others]


def _inside(p, bx):
    return all(bx.a[i] - EPS <= p[i] <= bx.b[i] + EPS for i in range(3))


def cull_hidden_faces(model):
    """Убирает грани, целиком закрытые другими деталями (по ячейкам сетки 0.5)."""
    removed = 0
    for bi, bx in enumerate(model.boxes):
        if bx.rot:                                   # повёрнутые детали ничего не закрывают и сами не обрезаются
            continue
        for f in list(bx.faces):
            ax, sg = NORMAL[f]
            others, ((a0, a1), (b0, b1)) = _rect(bx, f)
            na = max(1, int(round((a1 - a0) / GRID)))
            nb = max(1, int(round((b1 - b0) / GRID)))
            covered = True
            for i in range(na):
                for j in range(nb):
                    p = [0.0, 0.0, 0.0]
                    p[ax] = (bx.b[ax] if sg > 0 else bx.a[ax]) + sg * 0.01
                    p[others[0]] = a0 + (a1 - a0) * (i + 0.5) / na
                    p[others[1]] = b0 + (b1 - b0) * (j + 0.5) / nb
                    if not any(o is not bx and not o.rot and _inside(p, o) for o in model.boxes):
                        covered = False
                        break
                if not covered:
                    break
            if covered:
                bx.faces.remove(f)
                bx.mat.pop(f, None)
                removed += 1
    return removed


def check_grid(model):
    bad = []
    for bx in model.boxes:
        if min(bx.a) < 0 or max(bx.b) > 16:
            bad.append(f"границы блока: {bx.name} {bx.a}-{bx.b} выходит за 0..16")
        for v in list(bx.a) + list(bx.b):
            if abs(v / GRID - round(v / GRID)) > 1e-6:
                bad.append(f"сетка: {bx.name} координата {v} не кратна {GRID}")
                break
    return bad


def validate(model, place):
    """Возвращает список проблем: пересечение областей атласа и z-fighting (совпадающие перекрывающиеся грани)."""
    issues = check_grid(model)
    rects = [(k, v) for k, v in place.items()]
    for i in range(len(rects)):
        (k1, (x1, y1, w1, h1)) = rects[i]
        for j in range(i + 1, len(rects)):
            (k2, (x2, y2, w2, h2)) = rects[j]
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                issues.append(f"атлас: области {model.boxes[k1[0]].name}/{k1[1]} и {model.boxes[k2[0]].name}/{k2[1]} пересекаются")
    bs = model.boxes
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            for f in bs[i].faces:
                if f not in bs[j].faces:
                    continue
                ax, pa = _plane(bs[i], f)
                _, pb = _plane(bs[j], f)
                if abs(pa - pb) > EPS:
                    continue
                oi, ri = _rect(bs[i], f)
                oj, rj = _rect(bs[j], f)
                ov = all(min(ri[k][1], rj[k][1]) - max(ri[k][0], rj[k][0]) > EPS for k in range(2))
                if ov:
                    issues.append(f"z-fighting: {bs[i].name}#{i} и {bs[j].name}#{j}, грань {f}")
    return issues


def volume_overlaps(model):
    """Детали, проникающие друг в друга (не касающиеся): для информации."""
    out = []
    bs = model.boxes
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            d = [min(bs[i].b[k], bs[j].b[k]) - max(bs[i].a[k], bs[j].a[k]) for k in range(3)]
            if all(v > EPS for v in d):
                out.append((i, j, [round(v, 2) for v in d]))
    return out


def _pack(rects, atlas):
    x = y = rowh = 0
    place = {}
    for r in rects:
        w, h = r[0], r[1]
        if w > atlas or h > atlas:
            return None
        if x + w > atlas:
            x = 0; y += rowh + 1; rowh = 0
        if y + h > atlas:
            return None
        place[(r[2], r[3])] = (x, y, w, h)
        x += w + 1
        rowh = max(rowh, h)
    return place


def _n(v):
    r = round(v, 4)
    return int(r) if r == int(r) else r


def build(model, frames=None, scale=1.0, offset=(0.0, 0.0, 0.0)):
    """Возвращает (элементы, [кадры атласа], раскладка). Каждая грань получает свой прямоугольник
    атласа на сетке 32 текселя на блок; прямоугольники не пересекаются."""
    global ATLAS
    cull_hidden_faces(model)
    model.boxes = [bx for bx in model.boxes if bx.faces]       # деталь без видимых граней не нужна (пустой элемент ломает модель)
    rects = []
    for bi, bx in enumerate(model.boxes):
        for f in bx.faces:
            w, h = face_dims(bx, f)
            rects.append([max(1, int(round(w * TEXEL))), max(1, int(round(h * TEXEL))), bi, f])
    rects.sort(key=lambda r: (-r[1], -r[0]))
    place = None
    for atlas in (32, 64, 96, 128, 192, 256, 384, 512):
        place = _pack(rects, atlas)
        if place:
            break
    if not place:
        raise ValueError(f"{model.id}: атлас переполнен")
    ATLAS = atlas
    model.atlas = atlas
    imgs = []
    n = 1 if frames is None else frames
    for fi in range(n):
        fr = None if frames is None else fi
        img = Image.new("RGBA", (atlas, atlas), (0, 0, 0, 0))
        for (bi, f), (px_, py_, w, h) in place.items():
            bx = model.boxes[bi]
            im = paint_face(bx.mat[f], w, h, seed=model.seed + bi * 7 + len(f), frame=fr)
            img.paste(im, (px_, py_), im)
        imgs.append(img)
    els = []
    k = 16.0 / atlas
    for bi, bx in enumerate(model.boxes):
        faces = {}
        for f in bx.faces:
            px_, py_, w, h = place[(bi, f)]
            faces[f] = {"uv": [round(px_ * k, 6), round(py_ * k, 6), round((px_ + w) * k, 6), round((py_ + h) * k, 6)],
                        "texture": "#0"}
        el = {"name": "%s [%d,%d,%d]-[%d,%d,%d]" % (bx.name, *[int(round(v)) for v in bx.a], *[int(round(v)) for v in bx.b]), "from": [_n(bx.a[i] * scale + offset[i]) for i in range(3)], "to": [_n(bx.b[i] * scale + offset[i]) for i in range(3)], "faces": faces}
        if bx.rot:
            el["rotation"] = {"origin": [_n(bx.rot["origin"][i] * scale + offset[i]) for i in range(3)], "axis": bx.rot["axis"], "angle": bx.rot["angle"]}
        els.append(el)
    model.place = place
    return els, imgs, place


def floating(model):
    """Детали, не связанные с основанием через соприкосновение граней (положительная площадь контакта)."""
    bs = model.boxes
    n = len(bs)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            a, b = bs[i], bs[j]
            ov = [min(a.b[k], b.b[k]) - max(a.a[k], b.a[k]) for k in range(3)]
            if any(o < -EPS for o in ov):
                continue
            touching = [k for k in range(3) if abs(ov[k]) <= EPS]
            if len(touching) == 1 and all(ov[k] > EPS for k in range(3) if k not in touching):
                adj[i].append(j)
                adj[j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return [(i, bs[i].name, bs[i].a, bs[i].b) for i in range(n) if i not in seen]
