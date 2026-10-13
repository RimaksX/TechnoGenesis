"""Рисование текстур. Ванильные образцы берутся из tools/.vanilla (кэш скачивается
скриптом generate_assets.py), форма и тени сохраняются, меняется только палитра."""
import math
from pathlib import Path
from PIL import Image
import numpy as np

from .defs import *
from . import render as _R

V = Path(__file__).resolve().parent.parent / ".vanilla"


VANILLA_URL = "https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/1.21.1/assets/minecraft/textures/"


def van(name, frame=0):
    path = V / f"{name}.png"
    if not path.exists():
        import urllib.request
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(VANILLA_URL + name + ".png", path)
    im = Image.open(path).convert("RGBA")
    if im.height > im.width:  # анимированная полоса -> первый кадр
        im = im.crop((0, frame * im.width, im.width, (frame + 1) * im.width))
    return im


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def scale(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


def desat(c, t):
    g = int(lum(c))
    return mix(c, (g, g, g), t)


def map_ramp(rp, t):
    t = max(0.0, min(1.0, t))
    return rp[int(round(t * (len(rp) - 1)))]


def ramp_from(img, n=5):
    """Выбирает n цветов из текстуры по яркости."""
    a = np.array(img)
    cols = sorted({tuple(p[:3]) for p in a.reshape(-1, 4) if p[3] > 200}, key=lum)
    return [tuple(int(v) for v in cols[int(round(i * (len(cols) - 1) / (n - 1)))]) for i in range(n)]


def recolor(img, rp, pred=None, lo=None, hi=None, gamma=1.0):
    """Перекрашивает непрозрачные пиксели (удовлетворяющие pred) по яркости в рампу."""
    a = np.array(img).astype(int)
    out = a.copy()
    sel = a[..., 3] > 0
    if pred is not None:
        sel &= pred(a)
    L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    if not sel.any():
        return Image.fromarray(out.astype("uint8"), "RGBA")
    l0 = L[sel].min() if lo is None else lo
    l1 = L[sel].max() if hi is None else hi
    for y, x in zip(*np.where(sel)):
        t = (L[y, x] - l0) / max(1.0, (l1 - l0))
        c = map_ramp(rp, t ** gamma)
        out[y, x, :3] = c
    return Image.fromarray(out.astype("uint8"), "RGBA")


def blank(w=16, h=16):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def put(img, x, y, c, a=255):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), (*c[:3], a))


def rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(img, x, y, c)


def transform(img, how):
    if how == "h":
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    if how == "v":
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    if how == "t":
        return img.transpose(Image.TRANSPOSE)
    return img


# ------------------------------------------------------------ руды и сырьё

def metal_ramp(metal: Metal):
    if metal.ramp:
        return metal.ramp
    return ramp_from(van(f"item/{metal.id}_ingot"))


def ore_ramp(metal: Metal):
    """Цвета исходной руды данного металла."""
    for m in MINERALS:
        if m.metal == metal.id:
            return m.ramp
    return ramp_from(van(f"item/raw_{metal.id}"))


def r9(stops):
    return _R.expand_ramp(list(stops), 9)


def form_ramps(metal: Metal):
    o, mt = ore_ramp(metal), metal_ramp(metal)
    if len(o) == 5:
        o = r9(o)
    if len(mt) == 5:
        mt = r9(mt)
    crushed = [scale(c, 0.92) for c in o]
    washed = [mix(scale(c, 0.78), (50, 70, 110), 0.25) for c in o]
    concentrate = [scale(mix(a, b, 0.5), 1.08) for a, b in zip(o, mt)]
    tailings = [mix(desat(scale(c, 0.7), 0.55), (92, 74, 60), 0.35) for c in o]
    fine = [mix(scale(c, 0.9), (150, 140, 128), 0.28) for c in tailings]
    wet = [mix(scale(c, 0.6), (36, 46, 66), 0.32) for c in tailings]
    cake = [mix(desat(scale(c, 0.75), 0.7), (96, 80, 66), 0.3) for c in tailings]
    precipitate = [scale(mix(a, b, 0.75), 1.12) for a, b in zip(o, mt)]
    return dict(crushed=crushed, washed=washed, concentrate=concentrate, tailings=tailings,
                fine=fine, wet=wet, cake=cake, precipitate=precipitate)


def form_texture(metal: Metal, form: str):
    shape = dict(crushed="item/gunpowder", washed="item/clay_ball",
                 concentrate="item/sugar", tailings="item/netherite_scrap",
                 fine="item/bone_meal", wet="item/charcoal", cake="item/netherite_scrap",
                 precipitate="item/redstone")[form]
    return recolor(van(shape), form_ramps(metal)[form])


def simple_item(shape, rp, **kw):
    return recolor(van(shape), rp, **kw)


# ------------------------------------------------------------ жидкости / вёдра

def bucket_texture(rgb):
    img = van("item/water_bucket")
    rp = r9([scale(rgb, 0.4), scale(rgb, 0.7), rgb, mix(rgb, (255, 255, 255), 0.35), mix(rgb, (255, 255, 255), 0.8)])
    return recolor(img, rp, pred=lambda a: (a[..., 2] > a[..., 0] + 25) & (a[..., 2] > a[..., 1] + 10))


# ------------------------------------------------------------ машины (процедурные)

STEEL_D = (44, 46, 52)
STEEL_S = (74, 77, 85)
STEEL_M = (110, 114, 122)
STEEL_L = (156, 160, 168)
STEEL_H = (204, 208, 214)
DARK = (24, 25, 29)
RIVET = (214, 218, 222)

_noise = None


def noise16():
    global _noise
    if _noise is None:
        a = np.array(van("block/smooth_stone")).astype(float)
        L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
        _noise = (L - L.mean())
    return _noise


def casing(base=(112, 116, 124), border=STEEL_D, rivets=True, groove=False, k=0.55):
    img = blank()
    n = noise16()
    for y in range(16):
        for x in range(16):
            v = int(n[y, x] * k)
            put(img, x, y, tuple(max(0, min(255, c + v)) for c in base))
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            put(img, x, y, border)
    for i in range(1, 15):
        put(img, i, 1, scale(base, 1.3))
        put(img, 1, i, scale(base, 1.22))
        put(img, i, 14, scale(base, 0.72))
        put(img, 14, i, scale(base, 0.78))
    if rivets:
        for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
            put(img, x, y, RIVET)
    if groove:
        for y in range(2, 14):
            put(img, 7, y, scale(base, 0.7))
            put(img, 8, y, scale(base, 1.25))
    return img


def plate(img, x0, y0, x1, y1, base=STEEL_M):
    """Вдавленная панель с фаской."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(img, x, y, base)
    for x in range(x0, x1 + 1):
        put(img, x, y0, scale(base, 0.62))
        put(img, x, y1, scale(base, 1.25))
    for y in range(y0, y1 + 1):
        put(img, x0, y, scale(base, 0.7))
        put(img, x1, y, scale(base, 1.18))


def machine_side():
    return casing(groove=True)


def machine_bottom():
    return casing(base=(86, 89, 96), rivets=True, k=0.4)


def lamp(img, x, y, on, color=(255, 176, 60)):
    put(img, x, y, color if on else scale(color, 0.28))
    if on:
        put(img, x, y + 1, scale(color, 0.7))


# --- щёковая дробилка
def crusher_front(frame=None):
    """frame None - выключена; 0..3 - кадры работы."""
    img = casing()
    on = frame is not None
    rect(img, 3, 3, 12, 9, DARK)
    # зубья: гэп между челюстями меняется по кадрам
    gap = [2, 1, 0, 1][frame] if on else 2
    for x in range(3, 13):
        put(img, x, 3, STEEL_L)
        put(img, x, 9, STEEL_L)
    for x in range(3, 13):
        top = 4 + (0 if (x % 2 == 0) else 1)
        bot = 8 - (0 if (x % 2 == 1) else 1)
        top_end = top + (2 - gap)
        bot_end = bot - (2 - gap)
        for y in range(4, min(top_end, 7) + 1):
            if y <= top + (0 if x % 2 == 0 else -1) + (2 - gap) and y <= 5 + (2 - gap):
                put(img, x, y, STEEL_M if x % 2 == 0 else STEEL_L)
        for y in range(max(bot_end, 6), 9):
            if y >= bot - (2 - gap):
                put(img, x, y, STEEL_M if x % 2 == 1 else STEEL_L)
    if on:
        # угольки/искры в зазоре и накал
        for x in (4, 7, 10):
            put(img, x, 6, (232, 132, 44))
        put(img, 5 + (frame % 2) * 3, 6, (255, 200, 90))
        # вибрация корпуса
        for x in range(3, 13):
            put(img, x, 2, scale(STEEL_L, 1.0))
    rect(img, 3, 10, 12, 10, STEEL_D)
    # панель управления
    plate(img, 3, 11, 12, 13, STEEL_S)
    lamp(img, 4, 12, on, (255, 150, 40))
    lamp(img, 6, 12, on and frame in (0, 2), (110, 220, 110))
    for x in (8, 10, 12):
        pass
    for x in range(8, 12):
        put(img, x, 12, DARK)
    return img


def crusher_top():
    img = casing(base=(104, 108, 116))
    rect(img, 3, 3, 12, 12, DARK)
    # решётка загрузочного бункера
    for x in range(4, 12, 2):
        for y in range(4, 12):
            put(img, x, y, STEEL_L)
    for y in range(4, 12, 3):
        for x in range(4, 12):
            put(img, x, y, STEEL_M)
    return img


# --- промывочный барабан
def drum_front(frame=None):
    img = casing()
    on = frame is not None
    cx, cy = 7.5, 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            if d <= 5.9:
                put(img, x, y, STEEL_L if d > 5.0 else (STEEL_M if d > 4.4 else (28, 52, 70) if not on else (40, 96, 132)))
    # лопасти
    ang0 = (frame or 0) * 30
    for k in range(3):
        a = math.radians(ang0 + k * 120)
        for r in range(1, 5):
            x = int(round(cx + math.cos(a) * r))
            y = int(round(cy + math.sin(a) * r))
            put(img, x, y, (120, 180, 210) if on else (86, 108, 122))
    put(img, 7, 7, STEEL_H)
    put(img, 8, 7, STEEL_L)
    put(img, 7, 8, STEEL_L)
    put(img, 8, 8, STEEL_M)
    if on:
        for (x, y) in ((5, 5 + frame % 2), (10, 9 - frame % 2), (9, 5)):
            put(img, x, y, (200, 232, 245))
    # крепёж обода
    for (x, y) in ((7, 1), (8, 1), (7, 14), (8, 14), (1, 7), (1, 8), (14, 7), (14, 8)):
        put(img, x, y, STEEL_H if (x + y) % 2 else STEEL_L)
    return img


def drum_top():
    img = casing(base=(104, 108, 116))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d <= 4.6:
                put(img, x, y, DARK if d < 3.2 else STEEL_L)
    put(img, 7, 7, (60, 120, 160))
    put(img, 8, 8, (60, 120, 160))
    return img


# --- магнитно-плотностной сепаратор
def separator_front(frame=None):
    img = casing()
    on = frame is not None
    red, blue = (200, 54, 54), (60, 96, 214)
    # подкова-магнит
    for y in range(3, 9):
        put(img, 4, y, red)
        put(img, 5, y, scale(red, 0.75))
        put(img, 10, y, blue)
        put(img, 11, y, scale(blue, 0.75))
    for x in range(6, 10):
        put(img, x, 8, STEEL_L)
        put(img, x, 9, STEEL_M)
    put(img, 5, 8, STEEL_L)
    put(img, 10, 8, STEEL_L)
    put(img, 4, 3, STEEL_H)
    put(img, 5, 3, STEEL_H)
    put(img, 10, 3, STEEL_H)
    put(img, 11, 3, STEEL_H)
    # просвет между полюсами
    rect(img, 6, 3, 9, 7, DARK)
    if on:
        sp = [(7, 4), (8, 6), (6, 5), (9, 4)]
        for i, (x, y) in enumerate(sp):
            if (i + frame) % 2 == 0:
                put(img, x, y, (255, 224, 120))
    # конвейерная лента
    rect(img, 2, 10, 13, 13, DARK)
    for x in range(2, 14):
        put(img, x, 10, STEEL_L)
        put(img, x, 13, STEEL_D)
    off = (frame or 0)
    for x in range(2, 14):
        if (x + off) % 4 == 0:
            put(img, x, 11, STEEL_M)
            put(img, x + 1 if x + 1 < 14 else x, 12, STEEL_M)
            put(img, x, 12 if (x + off) % 4 else 12, STEEL_M)
    return img


def separator_top():
    img = casing(base=(104, 108, 116))
    rect(img, 3, 3, 12, 12, STEEL_D)
    for y in range(4, 12):
        for x in range(4, 12):
            put(img, x, y, (92, 96, 104) if (x + y) % 2 else (72, 76, 84))
    return img


# --- отстойник
def settler_front(frame=None):
    img = casing()
    on = frame is not None
    rect(img, 3, 2, 12, 12, STEEL_D)
    rect(img, 4, 3, 11, 11, (30, 40, 48))
    water, mud = (62, 150, 170), (92, 70, 44)
    for y in range(5, 10):
        for x in range(4, 12):
            put(img, x, y, water if y > 5 else scale(water, 1.25))
    for y in range(10, 12):
        for x in range(4, 12):
            put(img, x, y, mud if (x + y) % 3 else scale(mud, 0.8))
    if on:
        f = frame
        for (x, y) in ((5, 9 - f % 4 // 1), (8, 8 + (f // 2)), (10, 9 - (f + 1) % 3)):
            if 5 <= y <= 9:
                put(img, x, y, (190, 232, 240))
    put(img, 4, 3, STEEL_H)
    put(img, 5, 3, STEEL_L)
    # шкала уровня
    for y in range(4, 11, 2):
        put(img, 12, y, STEEL_H)
    plate(img, 3, 13, 12, 13, STEEL_S)
    return img


def settler_top():
    img = casing(base=(104, 108, 116))
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            if d <= 4.5:
                put(img, x, y, (46, 98, 112) if d < 3.6 else STEEL_L)
    for (x, y) in ((6, 6), (9, 9)):
        put(img, x, y, (110, 190, 205))
    return img


# --- твердотопливный генератор
def generator_front(on=False):
    src = van("block/furnace_front_on" if on else "block/furnace_front")
    steel = [DARK, STEEL_D, STEEL_S, STEEL_M, STEEL_L, STEEL_H]
    img = recolor(src, steel, pred=lambda a: ~((a[..., 0] > a[..., 2] + 40) & (a[..., 0] > 140)))
    # молния на верхней панели
    bolt = [(8, 2), (7, 3), (6, 4), (7, 4), (8, 4), (7, 5), (6, 6)]
    c = (255, 214, 64) if on else (150, 124, 40)
    for (x, y) in bolt:
        put(img, x, y, c)
    return img


def generator_top():
    img = casing(base=(96, 100, 108))
    rect(img, 4, 4, 11, 11, DARK)
    for y in range(5, 11, 2):
        for x in range(5, 11):
            put(img, x, y, STEEL_M)
    return img


# --- углеродный конденсатор
CARBON = (46, 46, 54)


def carbon_casing(groove=True):
    img = casing(base=CARBON, border=(18, 18, 22), rivets=True, k=0.35)
    if groove:
        for y in range(2, 14):
            put(img, 5, y, (30, 30, 36))
            put(img, 10, y, (60, 60, 70))
    # медные клеммы
    for x in (6, 7, 8, 9):
        put(img, x, 14, (190, 110, 60))
    return img


def capacitor_front(level):
    img = casing(base=CARBON, border=(18, 18, 22), rivets=True, k=0.35)
    rect(img, 5, 2, 10, 13, (16, 16, 20))
    cols = [(60, 200, 80), (110, 210, 70), (200, 210, 60), (230, 160, 50), (230, 80, 50)]
    for i in range(5):
        y = 11 - i * 2
        lit = i < level
        c = cols[i] if lit else (38, 38, 44)
        rect(img, 6, y, 9, y + 1, c)
        if lit:
            put(img, 6, y, scale(c, 1.3))
    return img


def capacitor_top():
    img = casing(base=(52, 52, 60), border=(18, 18, 22), k=0.35)
    for (x, y) in ((5, 5), (10, 5), (5, 10), (10, 10)):
        rect(img, x, y, x + 1, y + 1, (190, 110, 60))
        put(img, x, y, (230, 150, 90))
    return img


# --- кабель
def wire_texture(rp):
    img = blank()
    for y in range(16):
        for x in range(16):
            band = (x + y) % 4
            put(img, x, y, rp[[1, 3, 2, 0][band]] if True else rp[2])
    return img


# --- предметы-компоненты

def machine_frame_item():
    img = blank()
    ol = DARK
    for i in range(2, 14):
        for (x, y) in ((i, 2), (i, 13), (2, i), (13, i)):
            put(img, x, y, ol)
    for i in range(3, 13):
        put(img, i, 3, STEEL_H)
        put(img, 3, i, STEEL_L)
        put(img, i, 12, STEEL_S)
        put(img, 12, i, STEEL_S)
    for y in range(4, 12):
        for x in range(4, 12):
            img.putpixel((x, y), (0, 0, 0, 0))
    for i in range(4, 12):
        put(img, i, i, STEEL_M)
        put(img, i, 15 - i, STEEL_M)
    for (x, y) in ((3, 3), (12, 3), (3, 12), (12, 12)):
        put(img, x, y, RIVET)
    return img


def gangue_texture():
    return recolor(van("item/flint"), r9([(48, 48, 50), (84, 84, 88), (118, 118, 122), (150, 150, 154), (180, 180, 184)]))


def ash_texture():
    return recolor(van("item/gunpowder"), r9([(70, 66, 64), (110, 104, 100), (150, 144, 138), (190, 184, 176), (222, 216, 208)]))


def sludge_texture():
    return recolor(van("item/slime_ball"), r9([(40, 30, 20), (68, 52, 34), (96, 74, 48), (128, 102, 68), (158, 130, 90)]))


def mineral_fraction_texture():
    return recolor(van("item/clay_ball"), r9([(70, 66, 60), (104, 98, 90), (138, 130, 120), (168, 160, 148), (196, 188, 174)]))


def salt_texture():
    return recolor(van("item/sugar"), r9([(150, 146, 158), (190, 186, 198), (222, 220, 230), (244, 243, 248), (255, 255, 255)]))


def sulfur_powder_texture():
    return recolor(van("item/glowstone_dust"), r9([(110, 94, 10), (166, 142, 14), (214, 190, 24), (244, 226, 60), (255, 249, 150)]))


def crushed_spodumene_texture():
    return recolor(van("item/gunpowder"), r9(MINERAL["spodumene"].ramp))


def graphite_texture():
    return recolor(van("item/coal"), r9(MINERAL["graphite"].ramp))
