"""Формы переработки (хвосты, тонкая смесь, влажный кек, кек R2): рисуются тем же приёмом, что и куски сырой руды -
знаковый силуэт, грани и блик сверху-слева, отражённый свет снизу-справа, контур из двух самых тёмных тонов,
палитра контрастная и насыщенная, тени смещены в синий, света в жёлтый."""
import math
import random
from . import render as R
from . import textures as T
from .rawore import Sprite, _sp
from .designs import ramp9

BASE = {
    "tailings": [(30, 30, 40), (84, 78, 84), (132, 124, 120), (180, 170, 156), (226, 216, 198)],
    "fine": [(52, 48, 52), (116, 104, 96), (174, 160, 138), (216, 202, 174), (248, 238, 210)],
    "wet": [(20, 22, 30), (62, 56, 46), (104, 92, 66), (150, 134, 92), (200, 184, 130)],
    "cake": [(40, 38, 46), (106, 98, 96), (160, 150, 134), (204, 192, 168), (240, 230, 206)],
}
WATER = [(16, 36, 80), (36, 88, 150), (76, 146, 206), (146, 204, 238), (232, 248, 255)]


def stops_for(metal, form, k):
    o = T.ore_ramp(metal)
    if len(o) != 5:
        idx = [0, len(o) // 4, len(o) // 2, 3 * len(o) // 4, len(o) - 1]
        o = [o[i] for i in idx]
    return [T.mix(b, c, k) for b, c in zip(BASE[form], o)]


def sprite(metal, form, k):
    return Sprite({"m": ramp9(stops_for(metal, form, k), key=("form", metal.id, form)),
                   "w": ramp9(WATER, key="formwater")})


def tailings(metal):
    sp = sprite(metal, "tailings", 0.28)
    L = sp.lump
    L(4.6, 11.4, 3.1, 2.7, -12, "m", 4)
    L(11.0, 11.6, 3.5, 2.7, 10, "m", 4)
    L(7.8, 8.4, 3.8, 3.1, 0, "m", 5)
    L(4.6, 6.4, 2.3, 2.0, -20, "m", 4)
    L(11.4, 6.2, 2.5, 2.1, 15, "m", 5)
    L(8.0, 3.8, 2.2, 1.9, 0, "m", 5)
    sp.pixels([(7, 7), (4, 5), (11, 5), (6, 11), (12, 10)], 8)
    return sp.render()


def fine(metal):
    sp = sprite(metal, "fine", 0.22)
    mask = R.polygon_mask([(2.4, 12.6), (5.0, 8.4), (7.0, 6.4), (9.0, 6.4), (11.0, 8.4), (13.6, 12.6)])
    mask |= R.superellipse(8.0, 11.0, 5.5, 2.3, p=2.2)
    z = R.height_dome(mask, R=3.6, H=3.2)
    fill = R.shade(z, sp.ramps["m"], noise=R.Noise(9, 1), noise_amp=0.55, contrast=1.2, rim=0.1)
    for p, c in fill.items():
        sp.px[p] = ("m", sp.ramps["m"].index(c))
    sp.pixels([(7, 7), (9, 8), (5, 10)], 8)
    sp.pixels([(3, 13), (13, 13)], 4)
    return sp.render()


def wet(metal):
    """Влажный кек: тёмный блестящий ком (тот же силуэт, что у сухого, но гладкий и мокрый)."""
    sp = sprite(metal, "wet", 0.18)
    L = sp.lump
    L(8.0, 8.6, 5.8, 4.4, -4, "m", 3)
    L(4.4, 12.4, 2.0, 1.6, 0, "m", 3)
    L(12.2, 12.4, 2.0, 1.6, 0, "m", 3)
    sp.pixels([(5, 6), (6, 5), (6, 6)], 8)                                # мокрый блеск
    sp.pixels([(11, 7), (12, 8)], 7)
    sp.pixels([(8, 10), (9, 11)], 6)
    return sp.render()


def cake(metal):
    """Сухой кек: матовый растрескавшийся ком, светлее и грубее влажного, с осыпающимися крошками."""
    sp = sprite(metal, "cake", 0.2)
    L = sp.lump
    L(8.0, 8.6, 5.8, 4.4, -4, "m", 4)
    L(4.4, 12.4, 2.0, 1.6, 0, "m", 4)
    L(12.2, 12.4, 2.0, 1.6, 0, "m", 3)
    sp.pixels([(10, 9), (6, 10), (11, 6)], 2)                       # редкие тёмные поры вместо трещин
    sp.pixels([(5, 6), (6, 5), (10, 6)], 8)
    return sp.render()


FUNCS = {"tailings_r1": tailings, "fine_tailings": fine, "wet_cake": wet, "cake_r2": cake}


STEEL = [(24, 26, 34), (58, 62, 74), (104, 110, 124), (156, 162, 176), (214, 220, 232)]


def machine_frame():
    """Каркас машины: стальная рама-куб (вид спереди-сверху): передняя рама, задняя грань и рёбра между ними."""
    sp = Sprite({"m": ramp9(STEEL, key="frame")})
    fx0, fy0, fx1, fy1 = 1.5, 6.0, 11.0, 14.5          # передняя грань
    dx, dy = 3.5, -3.6                                   # сдвиг задней грани
    bx0, by0, bx1, by1 = fx0 + dx, fy0 + dy, fx1 + dx, fy1 + dy
    sp.poly([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], 1)           # задняя панель видна сквозь раму
    sp.poly([(fx0, fy0), (fx1, fy0), (fx1 + dx, fy0 + dy), (fx0 + dx, fy0 + dy)], 2)   # верхняя грань
    sp.poly([(fx1, fy0), (fx1 + dx, fy0 + dy), (fx1 + dx, fy1 + dy), (fx1, fy1)], 0)   # правая грань
    sp.poly([(fx0 + 1.6, fy0 + 1.6), (fx1 - 1.6, fy0 + 1.6), (fx1 - 1.6, fy1 - 1.6), (fx0 + 1.6, fy1 - 1.6)], 0)  # проём
    for (p0, p1, t, w) in (((fx0, fy0), (fx0 + dx, fy0 + dy), 5, 1.3), ((fx1, fy0), (fx1 + dx, fy0 + dy), 4, 1.3),
                           ((fx1, fy1), (fx1 + dx, fy1 + dy), 2, 1.3),
                           ((bx0, by0), (bx1, by0), 5, 1.3), ((bx1, by0), (bx1, by1), 3, 1.3)):
        sp.line(p0, p1, w, t)
    sp.line((fx0, fy0), (fx1, fy0), 1.9, 7)                # верхняя балка
    sp.line((fx0, fy0), (fx0, fy1), 1.9, 6)                # левая стойка
    sp.line((fx1, fy0), (fx1, fy1), 1.9, 4)                # правая стойка
    sp.line((fx0, fy1), (fx1, fy1), 1.9, 3)                # нижняя балка
    sp.pixels([(2, 6), (11, 6), (2, 14)], 8)
    return sp.render()
