"""Текстуры машин: стальные плиты с фасками, заклёпки, подсветка. Рисуются тем же рендерером (9 тонов)."""
import math
from . import render as R
from . import textures as T
from .designs import ramp9, layer, merge

N = R.N

STEEL = ramp9([(22, 26, 36), (58, 66, 82), (106, 116, 134), (162, 172, 188), (226, 232, 242)], key="steel")
CARBON = ramp9([(8, 8, 14), (26, 26, 36), (52, 52, 66), (92, 92, 108), (150, 150, 168)], key="carbon")
COPPER = ramp9([(60, 26, 22), (122, 56, 34), (190, 98, 56), (238, 156, 104), (255, 220, 176)], key="copperw")
ORANGE = ramp9([(80, 26, 10), (170, 66, 14), (236, 124, 24), (255, 190, 70), (255, 244, 170)], key="orange")
WATER = ramp9([(10, 36, 52), (22, 82, 110), (40, 138, 164), (96, 196, 214), (214, 246, 250)], key="water9")
MUD = ramp9([(26, 18, 12), (62, 44, 28), (104, 78, 48), (146, 114, 72), (190, 156, 108)], key="mud")
RED = ramp9([(60, 10, 16), (140, 24, 30), (212, 52, 46), (244, 110, 92), (255, 190, 170)], key="red")
BLUE = ramp9([(12, 22, 70), (28, 56, 150), (58, 100, 224), (118, 160, 255), (210, 226, 255)], key="blue")
GREEN = ramp9([(10, 50, 22), (24, 110, 44), (56, 180, 76), (130, 230, 130), (214, 255, 214)], key="green")
RUBBER = ramp9([(8, 8, 10), (22, 22, 26), (40, 40, 46), (64, 64, 72), (96, 96, 108)], key="rubber")


def img_from(colors):
    im = T.blank()
    for (x, y), c in colors.items():
        im.putpixel((x, y), (*c, 255))
    return im


def paste(im, layers):
    for lay in layers:
        for (x, y), c in lay.items():
            if 0 <= x < N and 0 <= y < N:
                im.putpixel((x, y), (*c, 255))
    return im


def box(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def plate_z(x, y, x0, y0, x1, y1, Rr=1.4, H=1.5):
    d = min(x - x0, x1 - x, y - y0, y1 - y)
    return H * min(1.0, max(0.0, (d + 0.6) / Rr))


def rivet_layers(rp, spots):
    L = []
    for (cx, cy) in spots:
        L.append(layer(R.disk_mask(cx + 0.5, cy + 0.5, 1.3), "dome", rp, seed=cx * 7 + cy, R=1.0, H=1.4, contrast=1.3))
    return L


def casing(rp=STEEL, inset=True, groove=False, rivets=True, seed=3):
    """Стальная плита: фаска по краю, утопленная панель, четыре заклёпки."""
    z = {}
    for y in range(N):
        for x in range(N):
            v = plate_z(x, y, 0, 0, 15, 15, 1.2, 1.6)
            if inset and 2 <= x <= 13 and 2 <= y <= 13:
                v = 1.0 + 0.5 * plate_z(x, y, 2, 2, 13, 13, 1.0, 1.0) - 0.15
            if groove and x in (7, 8) and 2 <= y <= 13:
                v -= 0.8 if x == 7 else 0.0
                v += 0.5 if x == 8 else 0.0
            z[(x, y)] = v
    colors = R.shade(z, rp, noise=R.Noise(seed, 4), noise_amp=0.05, contrast=1.3, rim=0.0, wrap=True)
    im = img_from(colors)
    if rivets:
        paste(im, rivet_layers(rp, [(2, 2), (12, 2), (2, 12), (12, 12)]))
    return im


def machine_side():
    return casing(groove=True, seed=4)


def machine_bottom():
    return casing(inset=False, seed=5)


def carbon_side():
    im = casing(CARBON, groove=True, seed=6)
    for x in (6, 7, 8, 9):
        im.putpixel((x, 14), (*COPPER[5 if x % 2 else 4], 255))
    return im


# ------------------------------------------------------------------ дробилка

def crusher_front(frame=None):
    im = casing()
    on = frame is not None
    # пасть: утопленный проём
    mouth = box(3, 3, 12, 9)
    z = {p: 0.0 for p in mouth}
    dark = R.shade({p: 1.0 for p in mouth}, RUBBER, noise=R.Noise(2, 3), noise_amp=0.12, rim=0)
    paste(im, [dark])
    gap = [0, 1, 2, 1][frame] if on else 0   # раскрытие челюстей
    teeth = []
    # верхняя челюсть
    for i, x in enumerate(range(3, 12, 3)):
        top = R.polygon_mask([(x, 3), (x + 3, 3), (x + 1.5, 6.4 - gap)])
        teeth.append(layer(top, "pyr", STEEL, seed=70 + i, cx=x + 1.5, cy=3.5, H=2.6, norm="l1", contrast=1.4, bias=0.05))
    for i, x in enumerate(range(4, 13, 3)):
        bot = R.polygon_mask([(x - 1, 9.2), (x + 2, 9.2), (x + 0.5, 6.2 + gap)])
        teeth.append(layer(bot, "pyr", STEEL, seed=80 + i, cx=x + 0.5, cy=9, H=2.6, norm="l1", contrast=1.4))
    paste(im, teeth)
    # балки челюстей
    paste(im, [layer(box(3, 3, 12, 3), "bevel", STEEL, seed=1, R=0.6, H=1.0, bias=0.1),
               layer(box(3, 9, 12, 9), "bevel", STEEL, seed=2, R=0.6, H=1.0, bias=-0.1)])
    if on:
        glow = {(x, 6 - 0): ORANGE[4 + (x + frame) % 2] for x in range(4, 12) if (x + frame) % 3 != 0}
        glow.update({(x, 5): ORANGE[2] for x in (5, 9) if frame % 2 == 0})
        glow.update({(x, 7): ORANGE[3] for x in (6, 10) if frame % 2 == 1})
        paste(im, [glow])
    # панель управления
    z2 = {(x, y): plate_z(x, y, 3, 11, 12, 13, 0.9, 1.0) for y in range(11, 14) for x in range(3, 13)}
    paste(im, [R.shade(z2, STEEL, noise=None, rim=0.0, contrast=1.3)])
    for i, (x, col, lit) in enumerate([(4, ORANGE, on), (6, GREEN, on and frame in (0, 2))]):
        paste(im, [layer(R.disk_mask(x + 0.5, 12.5, 1.0), "dome", col if lit else RUBBER, seed=i, R=0.8, H=1.0)])
    for x in range(8, 12):
        im.putpixel((x, 12), (*RUBBER[1], 255))
    return im


def crusher_top():
    im = casing(inset=True, seed=11)
    paste(im, [R.shade({p: 0.5 for p in box(3, 3, 12, 12)}, RUBBER, noise=R.Noise(5, 3), noise_amp=0.14, rim=0)])
    bars = []
    for x in range(4, 12, 2):
        bars.append(layer(box(x, 3, x, 12), "bevel", STEEL, seed=x, R=0.6, H=1.2, bias=0.1))
    paste(im, bars)
    paste(im, [layer(box(3, 7, 12, 8), "bevel", STEEL, seed=3, R=0.8, H=1.2)])
    return im


# ------------------------------------------------------------------ барабан

def drum_front(frame=None):
    im = casing()
    on = frame is not None
    cx, cy = 8.0, 8.0
    ring = R.disk_mask(cx, cy, 6.1) - R.disk_mask(cx, cy, 4.3)
    paste(im, [layer(ring, "dome", STEEL, seed=7, R=1.2, H=1.8, contrast=1.3)])
    glass = R.disk_mask(cx, cy, 4.3)
    zz = {}
    for (x, y) in glass:
        d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
        zz[(x, y)] = 1.4 * math.sqrt(max(0, 1 - (d / 4.6) ** 2))
    col = R.shade(zz, WATER if on else CARBON, noise=R.Noise(3, 3), noise_amp=0.1, contrast=1.1, bias=-0.05 if not on else 0.0, rim=0.0)
    paste(im, [col])
    # лопасти
    ang0 = (frame or 0) * 30
    blades = {}
    for k in range(3):
        a = math.radians(ang0 + k * 120 + 20)
        for r in range(1, 5):
            x, y = int(round(cx - 0.5 + math.cos(a) * r)), int(round(cy - 0.5 + math.sin(a) * r))
            blades[(x, y)] = STEEL[5 + (1 if r < 3 else 0)] if on else STEEL[3]
    paste(im, [blades])
    paste(im, [layer(R.disk_mask(cx, cy, 1.5), "dome", STEEL, seed=2, R=1.0, H=1.4)])
    if on:
        paste(im, [{(6, 5 + frame % 2): WATER[8], (10, 9 - frame % 2): WATER[7], (9, 5): WATER[8]}])
    # блик на стекле
    paste(im, [{(5, 5): STEEL[8], (6, 4): STEEL[7], (4, 6): STEEL[7]}] if not on else [{(5, 5): WATER[8], (6, 4): WATER[8]}])
    return im


def drum_top():
    im = casing(seed=12)
    paste(im, [layer(R.disk_mask(8, 8, 4.6), "dome", STEEL, seed=2, R=1.6, H=2.0, contrast=1.3)])
    paste(im, [layer(R.disk_mask(8, 8, 2.2), "dome", RUBBER, seed=4, R=1.2, H=1.2, contrast=1.2)])
    paste(im, [layer(R.disk_mask(8.0, 8.0, 0.9), "dome", WATER, seed=5, R=0.6, H=1.0)])
    return im


# ------------------------------------------------------------------ сепаратор

def separator_front(frame=None):
    im = casing()
    on = frame is not None
    # подкова-магнит
    cx, cy = 8, 7.2
    outer = R.superellipse(cx, cy + 0.6, 5.2, 5.0, 2.0)
    inner = R.superellipse(cx, cy + 0.2, 2.6, 3.0, 2.0)
    horseshoe = {p for p in outer if p not in inner and p[1] >= 5 or (p in outer and p not in inner and p[1] >= 3 and (p[0] <= 4 or p[0] >= 11))}
    horseshoe = {p for p in horseshoe if p[1] <= 9 or p[0] <= 5 or p[0] >= 10}
    left = {p for p in horseshoe if p[0] < 8}
    right = {p for p in horseshoe if p[0] >= 8}
    paste(im, [layer(left, "dome", RED, seed=3, R=1.4, H=1.8, contrast=1.3),
               layer(right, "dome", BLUE, seed=4, R=1.4, H=1.8, contrast=1.3)])
    tips = {(x, y) for (x, y) in horseshoe if y <= 4}
    paste(im, [layer({p for p in tips if p[0] < 8}, "bevel", STEEL, seed=5, R=0.8, H=1.0),
               layer({p for p in tips if p[0] >= 8}, "bevel", STEEL, seed=6, R=0.8, H=1.0)])
    if on:
        sp = {(7, 4): ORANGE[8], (8, 5): ORANGE[7], (6, 6): ORANGE[8]} if frame % 2 == 0 else {(8, 4): ORANGE[8], (7, 6): ORANGE[7], (9, 5): ORANGE[8]}
        paste(im, [sp])
    # конвейерная лента
    belt = box(2, 11, 13, 13)
    zb = {p: 0.9 for p in belt}
    paste(im, [R.shade(zb, RUBBER, noise=R.Noise(8, 3), noise_amp=0.1, rim=0)])
    paste(im, [{(x, 11): STEEL[5] for x in range(2, 14)}, {(x, 13): STEEL[1] for x in range(2, 14)}])
    off = frame or 0
    for x in range(2, 14):
        if (x + off) % 4 == 0:
            paste(im, [{(x, 12): STEEL[4], (min(13, x + 1), 12): STEEL[3]}])
    return im


def separator_top():
    im = casing(seed=13)
    pl = box(3, 3, 12, 12)
    paste(im, [R.shade({p: 0.8 for p in pl}, RUBBER, noise=R.Noise(2, 2), noise_amp=0.1, rim=0)])
    holes = []
    for y in range(4, 12, 2):
        for x in range(4 + (y // 2 % 2), 12, 2):
            holes.append({(x, y): STEEL[6]})
    paste(im, holes)
    return im


# ------------------------------------------------------------------ отстойник

def settler_front(frame=None):
    im = casing()
    on = frame is not None
    win = box(3, 3, 12, 11)
    paste(im, [layer(win, "bevel", STEEL, seed=3, R=1.0, H=1.2, bias=-0.1)])
    glass = box(4, 4, 11, 10)
    zz = {p: 1.0 for p in glass}
    wcol = R.shade(zz, WATER, noise=R.Noise(4, 3), noise_amp=0.18, rim=0)
    paste(im, [{p: c for p, c in wcol.items() if p[1] >= 5}])
    paste(im, [{(x, 4): WATER[3 if x % 2 else 4] for x in range(4, 12)}])
    mud = {p: c for p, c in R.shade({q: 1.0 for q in box(4, 9, 11, 10)}, MUD, noise=R.Noise(9, 2), noise_amp=0.2, rim=0).items()}
    paste(im, [mud])
    paste(im, [{(5, 5): STEEL[8], (4, 6): STEEL[7], (6, 4): STEEL[7]}])
    if on:
        f = frame
        paste(im, [{(5, 8 - f % 3): WATER[8], (8, 7 - (f + 1) % 3): WATER[8], (10, 8 - (f + 2) % 3): WATER[7]}])
    paste(im, [R.shade({p: plate_z(p[0], p[1], 3, 12, 12, 13, 0.7, 1.0) for p in box(3, 12, 12, 13)}, STEEL, rim=0, contrast=1.3)])
    return im


def settler_top():
    im = casing(seed=14)
    paste(im, [layer(R.disk_mask(8, 8, 4.8), "dome", STEEL, seed=1, R=1.5, H=1.8, contrast=1.3)])
    paste(im, [layer(R.disk_mask(8, 8, 3.2), "dome", WATER, seed=2, R=1.8, H=1.4, contrast=1.1)])
    paste(im, [{(6, 6): WATER[8], (7, 5): WATER[7]}])
    return im


# ------------------------------------------------------------------ генератор

def generator_front(on=False):
    src = T.van("block/furnace_front_on" if on else "block/furnace_front")
    img = T.recolor(src, STEEL, pred=lambda a: ~((a[..., 0] > a[..., 2] + 40) & (a[..., 0] > 140)))
    # молния
    bolt = [(9, 2), (8, 3), (7, 4), (8, 4), (9, 4), (8, 5), (7, 6)]
    c = ORANGE[7] if on else ORANGE[2]
    for (x, y) in bolt:
        img.putpixel((x, y), (*c, 255))
    return img


def generator_top():
    im = casing(seed=15)
    paste(im, [R.shade({p: 0.5 for p in box(4, 4, 11, 11)}, RUBBER, noise=R.Noise(2, 2), noise_amp=0.1, rim=0)])
    paste(im, [layer(box(5, y, 10, y), "bevel", STEEL, seed=y, R=0.6, H=1.0) for y in (5, 7, 9)])
    return im


# ------------------------------------------------------------------ конденсатор

def capacitor_front(level):
    im = casing(CARBON, seed=7)
    paste(im, [R.shade({p: 0.6 for p in box(5, 2, 10, 13)}, RUBBER, noise=None, rim=0)])
    cols = [GREEN, GREEN, ORANGE, ORANGE, RED]
    for i in range(5):
        y = 11 - i * 2
        lit = i < level
        rp = cols[i] if lit else RUBBER
        paste(im, [layer(box(6, y, 9, y + 1), "bevel", rp, seed=i, R=0.7, H=1.0, contrast=1.2, bias=0.1 if lit else 0.0)])
    return im


def capacitor_top():
    im = casing(CARBON, seed=8)
    for (x, y) in ((4, 4), (10, 4), (4, 10), (10, 10)):
        paste(im, [layer(R.disk_mask(x + 1, y + 1, 1.6), "dome", COPPER, seed=x + y, R=1.2, H=1.6, contrast=1.3)])
    return im


# ------------------------------------------------------------------ провод и компоненты

def wire_texture():
    z = {}
    for y in range(N):
        for x in range(N):
            z[(x, y)] = 1.3 * math.sin(math.pi * (((x + y) % 4) + 0.5) / 4.0)
    return img_from(R.shade(z, COPPER, noise=R.Noise(3, 4), noise_amp=0.04, contrast=1.3, wrap=True, rim=0))


def machine_frame_item():
    im = T.blank()
    ring = box(2, 2, 13, 13) - box(5, 5, 10, 10)
    cross = R.line_mask((2.5, 2.5), (13.5, 13.5), 1.5) | R.line_mask((13.5, 2.5), (2.5, 13.5), 1.5)
    shape = ring | (cross & box(2, 2, 13, 13))
    fill = layer(shape, "bevel", STEEL, seed=3, R=1.4, H=1.8, contrast=1.3)
    ring_px = R.selout(fill, set(fill), 0.5)
    paste(im, [ring_px, fill])
    paste(im, rivet_layers(STEEL, [(2, 2), (12, 2), (2, 12), (12, 12)]))
    return im


# ------------------------------------------------------------------ ступень ×3

ACID = ramp9([(36, 54, 8), (88, 124, 18), (156, 194, 38), (208, 234, 88), (244, 255, 168)], key="acid")
OLIVE = ramp9([(34, 30, 10), (78, 72, 24), (124, 118, 52), (168, 160, 90), (212, 204, 140)], key="olive")
HOT = ORANGE


def _window(im, x0, y0, x1, y1, rp=RUBBER):
    paste(im, [R.shade({p: 0.8 for p in box(x0, y0, x1, y1)}, rp, noise=R.Noise(x0 + y0, 3), noise_amp=0.1, rim=0)])


def _control(im, on, frame=None, y0=12, y1=13):
    paste(im, [R.shade({p: plate_z(p[0], p[1], 3, y0, 12, y1, 0.8, 1.0) for p in box(3, y0, 12, y1)}, STEEL, rim=0,
                       contrast=1.3)])
    lamp(im, 4, y0 + 0, on, (110, 220, 110)) if False else None
    paste(im, [{(4, y0): GREEN[6] if on else RUBBER[3], (6, y0): ORANGE[6] if on and frame in (1, 3) else RUBBER[3]}])
    paste(im, [{(x, y0): RUBBER[1] for x in range(8, 12)}])


def mill_front(frame=None):
    """Роторная мельница: горизонтальный барабан с мелющими шарами, на ходу крутится и пылит."""
    im = casing()
    on = frame is not None
    _window(im, 3, 3, 12, 10)
    cx, cy = 7.5, 6.5
    ring = R.superellipse(cx, cy, 4.9, 3.9, 2.4) - R.superellipse(cx, cy, 3.5, 2.6, 2.4)
    paste(im, [layer(ring, "dome", STEEL, seed=3, R=1.0, H=1.6, contrast=1.3)])
    ang = math.radians((frame or 0) * 45)
    for k in range(4):
        a = ang + k * math.pi / 2
        bx, by = cx - 0.5 + math.cos(a) * 2.0, cy - 0.5 + math.sin(a) * 1.4
        paste(im, [layer(R.disk_mask(bx + 0.5, by + 0.5, 1.15), "dome", STEEL if not on else STEEL, seed=k, R=0.9, H=1.4,
                         contrast=1.3, rim=0.0)])
    if on:
        paste(im, [{(4, 4 + frame % 2): STEEL[7], (11, 8 - frame % 2): STEEL[6], (7, 5): STEEL[8]}])
    _control(im, on, frame)
    return im


def mill_top():
    im = casing(seed=21)
    _window(im, 3, 3, 12, 12)
    paste(im, [layer(box(4, y, 11, y), "bevel", STEEL, seed=y, R=0.6, H=1.0, bias=0.05) for y in (5, 7, 9)])
    paste(im, [layer(box(7, 4, 8, 11), "bevel", STEEL, seed=3, R=0.6, H=1.0)])
    return im


def acid_plant_front(frame=None):
    """Круглодонная колба с жёлто-зелёной кислотой; на ходу в ней поднимаются пузырьки."""
    im = casing()
    on = frame is not None
    flask = R.disk_mask(8.0, 8.6, 4.6) | box(6, 2, 9, 5)
    glass = R.shade({p: 1.0 for p in flask}, STEEL, rim=0, contrast=1.0, bias=0.1)
    paste(im, [{p: c for p, c in glass.items()}])
    liquid = {p for p in R.disk_mask(8.0, 8.6, 3.7) if p[1] >= 7} | ({(7, 6), (8, 6)} if on else set())
    lz = {p: 1.0 for p in liquid}
    paste(im, [R.shade(lz, ACID, noise=R.Noise(5, 3), noise_amp=0.12, rim=0)])
    paste(im, [{(x, 7): ACID[7] for x in range(5, 11) if (x, 7) in liquid}])
    paste(im, [{(5, 9): STEEL[8], (4, 8): STEEL[7], (6, 3): STEEL[8]}])
    if on:
        f = frame
        paste(im, [{(7, 11 - f % 4 * 2): ACID[8], (9, 10 - (f + 1) % 4 * 2): ACID[8], (8, 12 - (f + 2) % 3 * 2): ACID[7]}])
    paste(im, [layer(box(6, 1, 9, 2), "bevel", STEEL, seed=1, R=0.6, H=1.0)])
    _control(im, on, frame)
    return im


def acid_plant_top():
    im = casing(seed=22)
    paste(im, [layer(R.disk_mask(8, 8, 4.6), "dome", STEEL, seed=2, R=1.5, H=1.8, contrast=1.3)])
    paste(im, [layer(R.disk_mask(8, 8, 2.8), "dome", ACID, seed=3, R=1.4, H=1.4, contrast=1.2)])
    paste(im, [{(7, 7): ACID[8], (6, 6): ACID[7]}])
    return im


def leach_front(frame=None):
    """Вертикальный реактор со смотровым окном: кислотная взвесь кипит."""
    im = casing()
    on = frame is not None
    vessel = box(4, 3, 11, 12)
    paste(im, [layer(vessel, "tent", STEEL, seed=4, p0=(4, 8), p1=(11, 8), H=2.4, contrast=1.3)])
    glass = box(5, 5, 10, 10)
    paste(im, [R.shade({p: 1.0 for p in glass}, OLIVE if not on else ACID, noise=R.Noise(6, 3), noise_amp=0.16, rim=0)])
    paste(im, [{(x, 5): OLIVE[2] if not on else ACID[3] for x in range(5, 11)}])
    for y in (4, 11):
        paste(im, [{(x, y): STEEL[7 if y == 4 else 3] for x in range(4, 12)}])
    if on:
        f = frame
        paste(im, [{(6, 9 - f % 4): ACID[8], (8, 8 - (f + 1) % 4): ACID[8], (9, 9 - (f + 2) % 3): ACID[7]}])
    paste(im, [{(5, 6): STEEL[8], (5, 7): STEEL[7]}])
    _control(im, on, frame)
    return im


def leach_top():
    im = casing(seed=23)
    paste(im, [layer(R.disk_mask(8, 8, 4.8), "dome", STEEL, seed=1, R=1.6, H=2.0, contrast=1.3)])
    for (x, y) in ((5, 5), (10, 5), (5, 10), (10, 10)):
        paste(im, [layer(R.disk_mask(x + 0.5, y + 0.5, 0.9), "dome", STEEL, seed=x + y, R=0.6, H=1.0)])
    paste(im, [layer(R.disk_mask(8, 8, 1.8), "dome", ACID, seed=2, R=1.0, H=1.2)])
    return im


def press_front(frame=None):
    """Пакет фильтровальных плит между упорами; на ходу плиты сжимаются и стекает фильтрат."""
    im = casing()
    on = frame is not None
    _window(im, 3, 3, 12, 10)
    layout = {None: (5, 7, 9), 0: (5, 7, 9), 1: (5, 6, 8), 2: (5, 6, 7), 3: (5, 6, 8)}[frame]
    paste(im, [layer(box(3, 3, 4, 10), "bevel", STEEL, seed=1, R=0.8, H=1.4, bias=0.0),
               layer(box(11, 3, 12, 10), "bevel", STEEL, seed=2, R=0.8, H=1.4, bias=-0.1)])
    for i, x in enumerate(layout):
        paste(im, [layer(box(x, 4, x, 9), "bevel", STEEL, seed=10 + i, R=0.6, H=1.2, bias=0.14 if i % 2 == 0 else -0.04)])
    paste(im, [{(x2, 3): STEEL[7] for x2 in range(5, 11)}, {(x2, 10): STEEL[3] for x2 in range(5, 11)}])
    if on:
        f = frame
        paste(im, [{(6 + f % 2 * 2, 11): OLIVE[6], (8, 11 - f % 2): OLIVE[5]}])
    _control(im, on, frame)
    return im


def press_top():
    im = casing(seed=24)
    paste(im, [layer(box(3, 6, 12, 9), "bevel", STEEL, seed=1, R=0.9, H=1.4)])
    paste(im, [layer(box(7, 3, 8, 12), "bevel", STEEL, seed=2, R=0.6, H=1.2, bias=0.1)])
    paste(im, rivet_layers(STEEL, [(4, 7), (10, 7)]))
    return im


def precip_front(frame=None):
    """Конический осадительный бак: кристаллы оседают к вершине конуса."""
    im = casing()
    on = frame is not None
    body = R.polygon_mask([(4, 3), (12, 3), (12, 8), (9, 12), (7, 12), (4, 8)])
    paste(im, [layer(body, "tent", STEEL, seed=5, p0=(4, 6), p1=(12, 6), H=2.4, contrast=1.3)])
    inner = R.polygon_mask([(5, 4), (11, 4), (11, 8), (8.5, 11), (7.5, 11), (5, 8)])
    liq = R.shade({p: 1.0 for p in inner}, WATER, noise=R.Noise(7, 3), noise_amp=0.12, rim=0)
    paste(im, [liq])
    crystals = [(8, 11), (7, 10), (8, 10), (8, 9)] + ([(9, 9), (7, 9), (8, 8)] if on and frame >= 1 else []) + \
               ([(6, 8), (10, 8)] if on and frame >= 2 else [])
    paste(im, [{p: STEEL[8 if (p[0] + p[1]) % 2 else 7] for p in crystals}])
    paste(im, [{(5, 5): STEEL[8], (5, 6): STEEL[7]}])
    if on:
        paste(im, [{(6, 5 + frame % 3): WATER[8], (10, 6 + (frame + 1) % 3): WATER[7]}])
    _control(im, on, frame)
    return im


def precip_top():
    im = casing(seed=25)
    paste(im, [layer(R.disk_mask(8, 8, 4.8), "dome", STEEL, seed=1, R=1.4, H=1.8, contrast=1.3)])
    paste(im, [layer(R.disk_mask(8, 8, 2.6), "dome", WATER, seed=2, R=1.4, H=1.4, contrast=1.1)])
    paste(im, [{(7, 7): WATER[8]}])
    return im


def column_front(frame=None):
    """Ректификационная колонна: тарелки по высоте, внизу нагрев, в окне перетекает кислота."""
    im = casing()
    on = frame is not None
    col = box(5, 2, 10, 11)
    paste(im, [layer(col, "tent", STEEL, seed=6, p0=(5, 6), p1=(10, 6), H=2.2, contrast=1.3)])
    for y in (4, 6, 8):
        paste(im, [{(x, y): STEEL[8] for x in range(5, 11)}, {(x, y + 1): STEEL[2] for x in range(5, 11)}])
    win = box(7, 3, 8, 10)
    paste(im, [R.shade({p: 1.0 for p in win}, ACID if on else OLIVE, noise=R.Noise(9, 2), noise_amp=0.14, rim=0)])
    if on:
        f = frame
        paste(im, [{(7, 9 - f % 4 * 2 // 1 if (9 - f % 4 * 2) > 3 else 9): ACID[8], (8, 8 - (f + 2) % 4 * 2 // 1 if (8 - (f + 2) % 4 * 2) > 3 else 8): ACID[8]}])
        paste(im, [{(x, 11): HOT[4 + (x + f) % 3] for x in range(5, 11)}])
    else:
        paste(im, [{(x, 11): RUBBER[3] for x in range(5, 11)}])
    _control(im, on, frame)
    return im


def column_top():
    im = casing(seed=26)
    paste(im, [layer(R.disk_mask(8, 8, 3.2), "dome", STEEL, seed=1, R=1.4, H=1.8, contrast=1.3)])
    paste(im, [layer(R.disk_mask(8, 8, 1.4), "dome", RUBBER, seed=2, R=0.8, H=1.0)])
    return im
