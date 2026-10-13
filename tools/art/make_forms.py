"""Рисунки форм переработки: оригинальные спрайты (не перекраска ванильных предметов).
Цвет формы = цвет материала формы, смешанный с оттенком руды металла."""
import math
import random
import sys
sys.path.insert(0, ".")
from pathlib import Path
import numpy as np
from PIL import Image
from kontur_gen import textures as T, defs as D

ROOT = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
SCR = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad")
LADDER = (0.30, 0.44, 0.60, 0.76, 0.92, 1.08, 1.24, 1.42)


def clampc(c):
    return tuple(max(0, min(255, int(round(v)))) for v in c)


def ladder(base, tint, k=0.3):
    """Лесенка из 8 тонов: от тёмного контура до блика."""
    mid = tuple(base[i] * (1 - k) + tint[i] * k for i in range(3))
    return [clampc(tuple(v * m for v in mid)) for m in LADDER]


def ore_tint(metal):
    o = T.ore_ramp(metal)
    return o[len(o) // 2]


BASES = {"tailings": (112, 106, 100), "fine": (176, 166, 148), "wet": (104, 90, 62), "cake": (182, 172, 152)}


def ramp(metal, form, k=0.3):
    return ladder(BASES[form], ore_tint(metal), k)


def new():
    return np.zeros((16, 16, 4), dtype=np.uint8)


def setpx(a, x, y, c):
    if 0 <= x < 16 and 0 <= y < 16:
        a[y, x] = (*c[:3], 255)


def outline(a, col, diagonal=False):
    out = a.copy()
    for y in range(16):
        for x in range(16):
            if a[y, x, 3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 16 and 0 <= ny < 16 and a[ny, nx, 3]:
                        setpx(out, x, y, col); break
    return out


# ---------------------------------------------------------------- хвосты R1: груда угловатых обломков

def rock(a, cx, cy, rw, rh, base, rp, seed):
    rnd = random.Random(seed)
    n = 6
    vs = []
    for i in range(n):
        ang = 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        k = rnd.uniform(0.8, 1.05)
        vs.append((cx + math.cos(ang) * rw * k, cy + math.sin(ang) * rh * k))
    peak = (cx - rw * 0.15, cy - rh * 0.25)
    owner = {}
    for y in range(16):
        for x in range(16):
            px, py = x + 0.5, y + 0.5
            for i in range(n):
                p0, p1 = vs[i], vs[(i + 1) % n]
                d0 = (p0[0] - peak[0], p0[1] - peak[1]); d1 = (p1[0] - peak[0], p1[1] - peak[1])
                dp = (px - peak[0], py - peak[1])
                c0 = d0[0] * dp[1] - d0[1] * dp[0]
                c1 = dp[0] * d1[1] - dp[1] * d1[0]
                c01 = d0[0] * d1[1] - d0[1] * d1[0]
                if c01 != 0 and (c0 * c01 >= 0) and (c1 * c01 >= 0):
                    # внутри клина; проверка по внешнему ребру
                    e = (p1[0] - p0[0], p1[1] - p0[1])
                    ep = (px - p0[0], py - p0[1])
                    cr = e[0] * ep[1] - e[1] * ep[0]
                    cp = e[0] * (peak[1] - p0[1]) - e[1] * (peak[0] - p0[0])
                    if cr * cp >= 0:
                        owner[(x, y)] = i
                        break
    tones = []
    for i in range(n):
        mid = math.atan2(((vs[i][1] + vs[(i + 1) % n][1]) / 2 - cy), ((vs[i][0] + vs[(i + 1) % n][0]) / 2 - cx))
        light = math.cos(mid - math.radians(225))          # свет сверху-слева
        tones.append(base + (3 if light > 0.75 else 2 if light > 0.25 else 1 if light > -0.25 else 0 if light > -0.75 else -1))
    mask = {}
    for (x, y), i in owner.items():
        mask[(x, y)] = rp[max(1, min(7, tones[i]))]
    for (x, y), c in mask.items():
        setpx(a, x, y, c)
    return set(mask)


def tailings(metal):
    rp = ramp(metal, "tailings", 0.1)
    a = new()
    cells = []
    for (cx, cy, rw, rh, base, seed) in ((4.6, 11.4, 3.3, 2.7, 4, 2), (11.3, 11.6, 3.6, 2.9, 3, 5), (8.0, 8.4, 3.6, 3.0, 4, 8),
                                         (4.8, 6.6, 2.4, 2.1, 4, 4), (11.4, 6.2, 2.5, 2.2, 5, 6), (8.0, 3.9, 2.4, 2.1, 5, 9)):
        # каждый обломок рисуем поверх прежних с собственным тёмным контуром
        layer = new()
        cellset = rock(layer, cx, cy, rw, rh, base, rp, seed)
        layer = outline(layer, rp[0])
        mask = layer[..., 3] > 0
        a[mask] = layer[mask]
    return Image.fromarray(a)


# ---------------------------------------------------------------- тонкая смесь: облачко пыли с зёрнами

def fine(metal):
    rp = ramp(metal, "fine", 0.1)
    a = new()
    rnd = random.Random(31)
    blobs = [(7.6, 9.2, 6.0, 3.4), (5.2, 7.4, 3.6, 2.6), (10.4, 7.0, 3.8, 2.8), (8.0, 5.2, 2.8, 2.2)]
    for y in range(16):
        for x in range(16):
            best = 9.0
            for (cx, cy, rw, rh) in blobs:
                best = min(best, ((x + 0.5 - cx) / rw) ** 2 + ((y + 0.5 - cy) / rh) ** 2)
            if best <= 1.0:
                # центр светлее, край темнее, на краях шахматная растушёвка
                depth = 1.0 - best
                t = 3 + int(depth * 3.2) + (1 if (x + y) % 2 == 0 and depth < 0.5 else 0)
                t -= 1 if y > 9 else 0
                setpx(a, x, y, rp[max(1, min(7, t))])
            elif best <= 1.35 and (x + y) % 2 == 0:
                setpx(a, x, y, rp[2])
    for (x, y, i) in ((1, 11, 3), (14, 9, 4), (2, 4, 4), (13, 3, 3), (6, 13, 2), (11, 13, 3), (15, 6, 2)):
        if a[y, x, 3] == 0:
            setpx(a, x, y, rp[i])
    return Image.fromarray(a)


# ---------------------------------------------------------------- влажный кек: комок мокрой массы

def lobes_height(lobes):
    hmap = np.zeros((16, 16))
    for (cx, cy, r, hh) in lobes:
        for y in range(16):
            for x in range(16):
                d2 = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) / (r * r)
                if d2 < 1.0:
                    hmap[y, x] = max(hmap[y, x], hh * math.sqrt(1.0 - d2))
    return hmap


def wet(metal):
    rp = ramp(metal, "wet", 0.18)
    a = new()
    hmap = lobes_height([(8.0, 10.2, 6.6, 3.8), (4.2, 11.8, 3.0, 2.0), (12.0, 11.8, 3.0, 2.2), (8.8, 7.6, 3.6, 2.8), (5.6, 8.4, 2.4, 1.8)])
    L = np.array([-0.55, -0.7, 0.45]); L /= np.linalg.norm(L)
    gy, gx = np.gradient(hmap)
    for y in range(16):
        for x in range(16):
            if hmap[y, x] <= 0.05:
                continue
            n = np.array([-gx[y, x], -gy[y, x], 1.0]); n /= np.linalg.norm(n)
            lam = float(n @ L)
            idx = 1 + int(max(0.0, min(1.0, (lam - 0.1) / 0.85)) * 5.4)
            if (x + y) % 2 == 0 and idx in (3, 4):
                idx += 1 if ((x * 3 + y * 5) % 4 == 0) else 0
            setpx(a, x, y, rp[max(1, min(6, idx))])
            if lam > 0.93 and hmap[y, x] > 1.2:
                setpx(a, x, y, (226, 242, 248))
    a = outline(a, rp[0])
    for (x, y, c) in ((11, 14, (96, 156, 206)), (11, 15, (150, 202, 236))):
        setpx(a, x, y, c)
    return Image.fromarray(a)


# ---------------------------------------------------------------- кек R2: сухая прессованная плитка с трещинами

def cake(metal):
    rp = ramp(metal, "cake", 0.12)
    a = new()
    cx, cy, hw, hh, th = 8.0, 6.8, 6.6, 3.6, 3
    def top(x, y):
        return abs((x + 0.5 - cx) / hw) + abs((y + 0.5 - cy) / hh)
    for y in range(16):
        for x in range(16):
            u = (x + 0.5 - cx) / hw
            if top(x, y) <= 1.0:
                setpx(a, x, y, rp[6] if top(x, y) > 0.78 else rp[5])      # фаска по краю плитки
            elif y + 0.5 > cy and abs(u) <= 1.0 and (y + 0.5 - cy) <= (1.0 - abs(u)) * hh + th:
                setpx(a, x, y, rp[3] if u < 0 else rp[2])
    for (x, y) in ((6, 3), (7, 4), (7, 5), (8, 6), (8, 7), (9, 8), (4, 6), (5, 6), (5, 7), (10, 5), (11, 5), (11, 6), (12, 6)):
        if a[y, x, 3] and top(x, y) <= 0.78:
            setpx(a, x, y, rp[3])
    for x in range(1, 15):                                  # слои пресса на боковых гранях
        for y in range(16):
            if a[y, x, 3] and top(x, y) > 1.0 and y == int(cy + (1.0 - abs((x + 0.5 - cx) / hw)) * hh + th - 1):
                setpx(a, x, y, rp[1])
    a = outline(a, rp[0])
    for (x, y) in ((14, 7), (13, 8), (14, 8)):               # отколотый угол
        a[y, x] = (0, 0, 0, 0)
    for (x, y, i) in ((15, 10, 4), (14, 11, 3), (13, 13, 4), (2, 12, 4), (1, 11, 3), (3, 13, 3)):
        if a[y, x, 3] == 0:
            setpx(a, x, y, rp[i])
    return Image.fromarray(a)


FUNCS = {"tailings_r1": tailings, "fine_tailings": fine, "wet_cake": wet, "cake_r2": cake}


def preview(path, big=True):
    sel = [D.METAL["nickel"], D.METAL["cobalt"], D.METAL["chromium"]]
    van = ["block/gravel", "item/bone_meal", "item/charcoal", "item/netherite_scrap"]
    sheet = Image.new("RGBA", (4 * 100, 4 * 100), (70, 72, 80, 255))
    for r, m in enumerate(sel):
        for c, (name, fn) in enumerate(FUNCS.items()):
            im = fn(m).resize((96, 96), 0)
            sheet.paste(im, (c * 100 + 2, r * 100 + 2), im)
    for c, v in enumerate(van):
        im = T.van(v).resize((96, 96), 0)
        sheet.paste(im, (c * 100 + 2, 302), im)
    sheet.save(path)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "write":
        for m in D.METALS:
            for name, fn in FUNCS.items():
                fn(m).save(ROOT / f"{m.id}_{name}.png")
    preview(SCR / "forms_new.png")
