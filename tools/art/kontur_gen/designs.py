"""Собственные формы руд, сырья, слитков и блоков в ванильном стиле (9 тонов, мягкая светотень)."""
import math
from . import render as R
from . import textures as T
from .defs import *

N = R.N


# ----------------------------------------------------------------- рампы

_RAMP_CACHE = {}


def ramp9(stops, key=None):
    k = key or tuple(stops)
    if k not in _RAMP_CACHE:
        _RAMP_CACHE[k] = R.expand_ramp(stops, 9)
    return _RAMP_CACHE[k]


# «порода» для сырья: нейтральные серо-коричневые тона в духе raw_iron
HOST = ramp9([T.hexrgb("#2e2a26") if hasattr(T, "hexrgb") else (46, 42, 38),
              (86, 76, 66), (138, 124, 108), (196, 182, 164), (236, 226, 212)], key="host")
HOST_DARK = ramp9([(14, 14, 18), (40, 40, 48), (74, 74, 86), (118, 118, 130), (170, 170, 182)], key="host_dark")
HOST_COOL = ramp9([(36, 40, 44), (78, 86, 92), (128, 138, 144), (186, 196, 200), (230, 236, 238)], key="host_cool")


# ----------------------------------------------------------------- формы-примитивы

def rot_rect(cx, cy, length, width, angle_deg, pointed=0.0):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    hl, hw = length / 2, width / 2
    if pointed > 0:
        pts = [(-hl, 0), (-hl + pointed, -hw), (hl - pointed, -hw), (hl, 0), (hl - pointed, hw), (-hl + pointed, hw)]
    else:
        pts = [(-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)]
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def vein(points, r, seed=0):
    m = set()
    rnd_vals = [1.0, 0.82, 1.1, 0.9, 1.05, 0.8]
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) * 1.5))
        for s in range(steps + 1):
            t = s / steps
            rr = r * rnd_vals[(i * 3 + s + seed) % len(rnd_vals)]
            m |= R.disk_mask(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, rr)
    return m


def layer(mask, kind, rp, seed=1, **kw):
    """Заливает маску: kind = dome | bevel | tent | pyr."""
    if not mask:
        return {}
    if kind == "dome":
        z = R.height_dome(mask, kw.get("R", 2.4), kw.get("H", 2.6))
    elif kind == "bevel":
        z = R.height_bevel(mask, kw.get("R", 1.6), kw.get("H", 1.5))
    elif kind == "tent":
        z = R.height_tent(mask, kw["p0"], kw["p1"], kw.get("H", 2.6))
    elif kind == "pyr":
        z = R.height_pyramid(mask, kw["cx"], kw["cy"], kw.get("H", 2.8), kw.get("norm", "l1"),
                             kw.get("sx", 1.0), kw.get("sy", 1.0))
    else:
        raise ValueError(kind)
    return R.shade(z, rp, noise=R.Noise(seed, kw.get("cell", 4)), noise_amp=kw.get("amp", 0.06),
                   contrast=kw.get("contrast", 1.2), bias=kw.get("bias", 0.0), spec=kw.get("spec", 0.0),
                   rim=kw.get("rim", 0.11))


def tent_for(poly_pts, **kw):
    """Маска + ось (по длинной стороне) для кристалла."""
    mask = R.polygon_mask(poly_pts)
    xs = [p[0] for p in poly_pts]
    ys = [p[1] for p in poly_pts]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    # ось: направление от первой точки к противоположной (для pointed rect это ось)
    p0 = poly_pts[0]
    p1 = poly_pts[3] if len(poly_pts) >= 6 else ((poly_pts[1][0] + poly_pts[2][0]) / 2, (poly_pts[1][1] + poly_pts[2][1]) / 2)
    if len(poly_pts) < 6:
        p0 = ((poly_pts[0][0] + poly_pts[3][0]) / 2, (poly_pts[0][1] + poly_pts[3][1]) / 2)
    return mask, p0, p1


# ----------------------------------------------------------------- акценты минералов (рисунок руды)

def accents(mid, rp, S=1.0):
    """Список слоёв-цветов {пиксель: цвет}. S - масштаб относительно центра (для сырья).
    Площадь рисунка ~35% блока, как у ванильных руд."""
    L = []

    def sc(v, c=8.0):
        return c + (v - c) * S

    def disk(cx, cy, r, seed, **kw):
        m = R.blob(sc(cx), sc(cy), r * S, seed=seed, wob=kw.pop("wob", 0.2))
        L.append(layer(m, kw.pop("kind", "dome"), rp, seed=seed, **kw))

    if mid == "bauxite":  # бобовые окатыши
        for i, (cx, cy, r) in enumerate([(4.0, 4.2, 2.3), (11.6, 3.6, 1.9), (8.0, 9.4, 2.7), (13.0, 12.6, 1.9),
                                         (2.8, 12.6, 1.7)]):
            disk(cx, cy, r, 11 + i, R=2.2, H=2.8)
    elif mid == "garnierite":  # извилистая жила с узелками
        v = vein([(sc(-1), sc(13.0)), (sc(4.5), sc(10.5)), (sc(9), sc(7.2)), (sc(13.5), sc(4.2)), (sc(17), sc(2.8))],
                 1.35 * S, 3)
        L.append(layer(v, "dome", rp, seed=5, R=1.8, H=2.4))
        v2 = vein([(sc(9), sc(7.2)), (sc(10.5), sc(11.5)), (sc(10), sc(15))], 1.05 * S, 2)
        L.append(layer(v2, "dome", rp, seed=7, R=1.4, H=2.0))
        disk(3.4, 4.6, 1.6, 21, R=1.6, H=2.2)
    elif mid == "wolframite":  # тёмные призматические кристаллы
        for i, (cx, cy, ln, w, ang) in enumerate([(5.2, 5.2, 8.5, 3.0, 45), (11.8, 10.4, 8.0, 2.8, 70),
                                                  (5.6, 12.4, 6.0, 2.4, -10)]):
            pts = rot_rect(sc(cx), sc(cy), ln * S, w * S, ang, pointed=1.3 * S)
            m, p0, p1 = tent_for(pts)
            L.append(layer(m, "tent", rp, seed=30 + i, p0=p0, p1=p1, H=2.7, contrast=1.3, spec=0.16))
    elif mid == "chromite":  # массивные зёрна
        for i, (cx, cy, rx, ry, rot) in enumerate([(4.4, 4.4, 3.0, 2.5, 0.3), (11.4, 8.2, 3.1, 2.6, -0.25),
                                                   (5.0, 12.2, 2.6, 2.1, -0.1)]):
            m = R.roughen(R.superellipse(sc(cx), sc(cy), rx * S, ry * S, 2.5, rot), i, 0.8)
            L.append(layer(m, "dome", rp, seed=40 + i, R=2.0, H=2.4, spec=0.14))
    elif mid == "pyrolusite":  # дендриты (папоротник)
        lines = [([(8, 15.0), (8, 3.0)], 1.3), ([(8, 11.5), (4.6, 8.0)], 1.1), ([(8, 11.5), (11.4, 8.2)], 1.1),
                 ([(8, 8), (5.6, 5.2)], 1.0), ([(8, 8), (10.4, 5.2)], 1.0)]
        m = set()
        for pts, w in lines:
            m |= R.line_mask((sc(pts[0][0]), sc(pts[0][1])), (sc(pts[1][0]), sc(pts[1][1])), w * max(0.85, S))
        m |= R.blob(sc(8), sc(13.2), 2.1 * S, seed=3)
        L.append(layer(m, "dome", rp, seed=51, R=1.4, H=2.2, contrast=1.3))
    elif mid == "cobaltite":  # огранённые кристаллы
        for i, (cx, cy, r) in enumerate([(4.6, 4.8, 3.2), (11.4, 9.0, 3.6), (4.8, 12.6, 2.6)]):
            cx, cy, r = sc(cx), sc(cy), r * S
            m = R.polygon_mask([(cx, cy - r * 1.1), (cx + r * 0.95, cy - r * 0.1), (cx + r * 0.4, cy + r * 1.0),
                                (cx - r * 0.6, cy + r * 0.9), (cx - r * 1.0, cy - r * 0.05)])
            L.append(layer(m, "pyr", rp, seed=60 + i, cx=cx, cy=cy, H=3.0, norm="l1", contrast=1.4, spec=0.12))
    elif mid == "molybdenite":  # тонкие листовые пластины
        for i, (cx, cy, rx, ry, rot) in enumerate([(5.2, 3.8, 4.0, 1.6, -0.15), (10.6, 8.2, 4.4, 1.7, 0.12),
                                                   (5.6, 12.6, 4.0, 1.6, -0.1)]):
            m = R.superellipse(sc(cx), sc(cy), rx * S, ry * S, 2.2, rot)
            L.append(layer(m, "dome", rp, seed=70 + i, R=1.3, H=1.7, contrast=1.3, spec=0.15))
    elif mid == "rutile":  # игольчатые кристаллы
        for i, (p0, p1, w) in enumerate([((1.5, 13.5), (9.5, 2.0), 1.9), ((6, 15.4), (14.4, 5), 1.8),
                                         ((10.5, 15.0), (15.3, 10), 1.5)]):
            a = (sc(p0[0]), sc(p0[1]))
            b = (sc(p1[0]), sc(p1[1]))
            L.append(layer(R.line_mask(a, b, w * S), "tent", rp, seed=80 + i, p0=a, p1=b, H=2.4, contrast=1.3,
                           spec=0.1))
    elif mid == "graphite":  # чешуйчатые линзы
        for i, (cx, cy, rx, ry) in enumerate([(7.6, 12.6, 6.0, 1.9), (8.4, 8.0, 5.4, 1.8), (6.2, 3.8, 4.2, 1.7)]):
            m = R.superellipse(sc(cx), sc(cy), rx * S, ry * S, 2.0, -0.05 * (i % 2 * 2 - 1))
            L.append(layer(m, "dome", rp, seed=90 + i, R=1.5, H=1.8, contrast=1.3, spec=0.2))
    elif mid == "halite":  # кубические кристаллы
        for i, (cx, cy, rx, ry, rot) in enumerate([(4.4, 4.2, 2.5, 2.4, 0.2), (11.8, 5.0, 2.2, 2.1, -0.15),
                                                   (8.0, 11.0, 2.9, 2.6, 0.1), (2.8, 12.4, 1.8, 1.7, -0.2)]):
            m = R.roughen(R.superellipse(sc(cx), sc(cy), rx * S, ry * S, 4.0, rot), i + 3, 0.5)
            L.append(layer(m, "bevel", rp, seed=100 + i, R=2.0, H=2.0, contrast=1.1, bias=0.12))
    elif mid == "sulfur":  # корка и шипы
        for i, (cx, cy, r) in enumerate([(3.0, 13.2, 2.3), (6.8, 13.8, 2.4), (11.6, 13.4, 2.2), (4.8, 10.6, 1.7)]):
            disk(cx, cy, r, 110 + i, R=1.9, H=2.4, wob=0.12)
        for i, (pts, p0, p1) in enumerate([([(9.2, 11), (11.8, 2.6), (14.4, 11)], (11.8, 2.6), (11.8, 11))]):
            sp = [(sc(x), sc(y)) for x, y in pts]
            L.append(layer(R.polygon_mask(sp), "tent", rp, seed=120 + i, p0=(sc(p0[0]), sc(p0[1])),
                           p1=(sc(p1[0]), sc(p1[1])), H=3.0, contrast=1.3, spec=0.12))
    elif mid == "spodumene":  # длинные призмы
        for i, (cx, cy, ln, w, ang) in enumerate([(5.2, 8.2, 10.5, 3.4, 80), (11.4, 9.4, 9.0, 3.2, 100)]):
            pts = rot_rect(sc(cx), sc(cy), ln * S, w * S, ang, pointed=1.7 * S)
            m, p0, p1 = tent_for(pts)
            L.append(layer(m, "tent", rp, seed=130 + i, p0=p0, p1=p1, H=3.0, contrast=1.35, spec=0.14))
    return L


# ----------------------------------------------------------------- руды

def merge(layers):
    out = {}
    for l in layers:
        out.update(l)
    return out


# ----------------------------------------------------------------- руды: мелкие кластеры

SCATTER = {  # центры кластеров держим внутри [3; 12.5]: отступ от края блока >= 1-2 px
    "A": [(3.5, 3.5), (10.5, 3.2), (7, 7), (12.5, 7.5), (3.5, 10.5), (9.5, 11.5), (12.5, 12.5)],
    "B": [(4.5, 3.2), (11.5, 4), (3.2, 7.5), (8.5, 9), (12.5, 10.5), (5, 12.5), (10, 12.5)],
    "C": [(3.5, 4.5), (8, 3.2), (12, 6), (5.5, 8.5), (10.5, 10.5), (3.5, 12), (12.5, 12.5)],
    "D": [(5, 3.5), (11, 3.5), (3.5, 8), (8, 7.5), (12.5, 9.5), (6, 12), (11.5, 12.5)],
}


def small(shape_fn, rp, seed, **kw):
    kw.setdefault("amp", 0.0)
    kw.setdefault("rim", 0.0)
    return layer(shape_fn, kw.pop("kind", "dome"), rp, seed=seed, **kw)


def ore_clusters(mid, rp):
    """6-7 мелких кластеров по 2-4 пикселя, как вкрапления в алмазной/изумрудной руде."""
    L = []
    pts = SCATTER[{"bauxite": "A", "garnierite": "B", "wolframite": "C", "chromite": "D", "pyrolusite": "A",
                   "cobaltite": "C", "molybdenite": "B", "rutile": "D", "graphite": "C", "halite": "A",
                   "sulfur": "B", "spodumene": "D"}[mid]]
    for i, (cx, cy) in enumerate(pts):
        sd = 7 * i + len(mid)
        big = i in (2, 4)          # пара кластеров покрупнее, остальные мельче
        k = 1.0 if big else 0.72
        if mid == "bauxite":       # круглые окатыши
            m = R.blob(cx, cy, 1.9 * k, seed=sd, wob=0.12)
            L.append(small(m, rp, sd, R=1.6, H=2.2))
        elif mid == "garnierite":  # короткие изогнутые прожилки
            ang = (-35, 20, -60, 35, -20, 55, -45)[i]
            a = (cx - 2.0 * math.cos(math.radians(ang)) * k, cy - 2.0 * math.sin(math.radians(ang)) * k)
            b = (cx + 2.0 * math.cos(math.radians(ang)) * k, cy + 2.0 * math.sin(math.radians(ang)) * k)
            L.append(small(R.line_mask(a, b, 1.45), rp, sd, R=1.0, H=1.6))
        elif mid == "wolframite":  # угловатые тёмные обломки
            pts_ = rot_rect(cx, cy, 4.2 * k, 2.4 * k, (25, -30, 60, -10, 40, -50, 15)[i], pointed=0.9)
            m, p0, p1 = tent_for(pts_)
            L.append(small(m, rp, sd, kind="tent", p0=p0, p1=p1, H=2.2, contrast=1.3, spec=0.14))
        elif mid == "chromite":    # плотные зёрна
            m = R.roughen(R.superellipse(cx, cy, 2.0 * k, 1.7 * k, 2.4, (0.3, -0.2, 0.1, -0.3, 0.2, 0.0, 0.25)[i]), sd, 0.5)
            L.append(small(m, rp, sd, R=1.5, H=2.0, spec=0.14))
        elif mid == "pyrolusite":  # крестики-дендриты
            m = R.line_mask((cx - 2 * k, cy), (cx + 2 * k, cy), 1.2) | R.line_mask((cx, cy - 2 * k), (cx, cy + 2 * k), 1.2)
            m |= R.disk_mask(cx, cy, 1.1)
            L.append(small(m, rp, sd, R=1.0, H=1.8, contrast=1.3))
        elif mid == "cobaltite":   # ромбы-кристаллы
            r = 2.3 * k
            m = R.polygon_mask([(cx, cy - r), (cx + r * 0.9, cy), (cx, cy + r), (cx - r * 0.9, cy)])
            L.append(small(m, rp, sd, kind="pyr", cx=cx, cy=cy, H=2.4, norm="l1", contrast=1.4, spec=0.12))
        elif mid == "molybdenite": # плоские чешуйки
            m = R.superellipse(cx, cy, 2.6 * k, 1.1 * k, 2.2, (-0.2, 0.1, -0.1, 0.2, 0.0, -0.15, 0.1)[i])
            L.append(small(m, rp, sd, R=1.0, H=1.4, contrast=1.3, spec=0.15))
        elif mid == "rutile":      # иглы
            ang = math.radians((-50, -35, -60, -45, -30, -55, -40)[i])
            a = (cx - 2.4 * k * math.cos(ang), cy - 2.4 * k * math.sin(ang))
            b = (cx + 2.4 * k * math.cos(ang), cy + 2.4 * k * math.sin(ang))
            L.append(small(R.line_mask(a, b, 1.3), rp, sd, kind="tent", p0=a, p1=b, H=1.6, contrast=1.3, spec=0.1))
        elif mid == "graphite":    # чешуйчатые линзы
            m = R.superellipse(cx, cy, 2.5 * k, 1.3 * k, 2.0, (-0.1, 0.1, 0.0, -0.15, 0.1, 0.0, -0.1)[i])
            L.append(small(m, rp, sd, R=1.1, H=1.6, contrast=1.3, spec=0.2))
        elif mid == "halite":      # кубики соли
            m = R.superellipse(cx, cy, 1.7 * k, 1.7 * k, 4.0, (0.15, -0.1, 0.0, 0.2, -0.15, 0.1, 0.0)[i])
            L.append(small(m, rp, sd, kind="bevel", R=1.4, H=1.6, bias=0.1))
        elif mid == "sulfur":      # жёлтые корочки
            m = R.blob(cx, cy, 1.8 * k, seed=sd, wob=0.3, sx=1.25, sy=0.9)
            L.append(small(m, rp, sd, R=1.4, H=2.0))
        elif mid == "spodumene":   # призмы
            pts_ = rot_rect(cx, cy, 4.6 * k, 2.2 * k, (70, 110, 90, 60, 100, 80, 120)[i], pointed=0.9)
            m, p0, p1 = tent_for(pts_)
            L.append(small(m, rp, sd, kind="tent", p0=p0, p1=p1, H=2.4, contrast=1.35, spec=0.14))
    return L


def ore_texture(m, kind="stone"):
    """Фон (камень/сланец/незерак) не трогаем: он бесшовный. Меняются только пиксели вкраплений;
    тёмный край и блик у кластеров рисует сам рендерер."""
    base = T.van({"stone": "block/stone", "deepslate": "block/deepslate", "nether": "block/netherrack"}[kind]).copy()
    rp = ramp9(m.ramp, key=("ore", m.id))
    fill = merge(ore_clusters(m.id, rp))
    # вкрапления не должны подходить к краю блока ближе 1 px
    bad = [p for p in fill if not (1 <= p[0] <= 14 and 1 <= p[1] <= 14)]
    if bad:
        raise ValueError(f"{m.id}: вкрапления у края блока: {bad}")
    for (x, y), c in fill.items():
        base.putpixel((x, y), (*c, 255))
    return base


# ----------------------------------------------------------------- сырьё: граненые камни

def facet_rock(pts, rp, acc_rp=None, seed=1, accents_=(), tone=0.0):
    """Низкополигональный камень: каждая грань (треугольник от центра к ребру) плоско освещена,
    блики по верхне-левой кромке, чёткие рёбра. Без размытых градиентов."""
    mask = R.polygon_mask(pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    lx, ly = -0.62, -0.78
    n = len(rp)
    fill = {}
    # тон каждой грани
    tones = []
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        mx, my = (x0 + x1) / 2 - cx, (y0 + y1) / 2 - cy
        ml = math.hypot(mx, my) or 1
        d = (mx / ml) * lx + (my / ml) * ly          # -1..1: к свету +
        tones.append(max(0.0, min(1.0, 0.5 + d * 0.42 + tone)))
    for (x, y) in mask:
        px, py = x + 0.5, y + 0.5
        ang = math.atan2(py - cy, px - cx)
        best, bi = 9.0, 0
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            a0, a1 = math.atan2(y0 - cy, x0 - cx), math.atan2(y1 - cy, x1 - cx)
            da = (ang - a0 + math.pi) % (2 * math.pi) - math.pi
            span = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            if 0 <= da <= span or (span < 0 and span <= da <= 0):
                bi = i
                break
        t = tones[bi]
        # лёгкий градиент к краю граней: ближе к центру светлее
        dist = math.hypot(px - cx, py - cy)
        t += 0.05 - dist * 0.012
        fill[(x, y)] = rp[int(round(max(0.0, min(1.0, t)) * (n - 1)))]
    # блик на верхне-левой кромке, тень на нижне-правой
    for (x, y) in list(fill):
        if (x - 1, y) not in mask or (x, y - 1) not in mask:
            fill[(x, y)] = rp[min(n - 1, rp.index(fill[(x, y)]) + 1)]
        if (x + 1, y) not in mask or (x, y + 1) not in mask:
            fill[(x, y)] = rp[max(0, rp.index(fill[(x, y)]) - 1)]
    if acc_rp:
        inner = {q for q in mask if (q[0] + 1, q[1]) in mask and (q[0] - 1, q[1]) in mask
                 and (q[0], q[1] + 1) in mask and (q[0], q[1] - 1) in mask}
        for i, (a, b, w) in enumerate(accents_):
            m = R.line_mask(a, b, w) & inner
            if m:
                fill.update(layer(m, "dome", acc_rp, seed=seed + i, R=1.2, H=1.8, amp=0.0, contrast=1.25, rim=0.0)
                            if False else layer(m, "dome", acc_rp, seed=seed + i, R=1.2, H=1.8, amp=0.0, contrast=1.25))
    return fill


def raw_texture(m):
    rp = ramp9(m.ramp, key=("ore", m.id))
    mid = m.id
    host = ramp9([T.scale(T.desat(c, 0.55), 0.9) for c in m.ramp], key=("host", m.id))
    rocks = {
        "bauxite":     ([(2, 8), (4, 4), (9, 2.5), (13.5, 5), (14, 10), (10, 13.5), (4.5, 13)], 3,
                        [((4.5, 10), (9.5, 5.5), 2.0), ((9, 11), (12, 8.5), 1.6)]),
        "garnierite":  ([(2.5, 9), (3, 4.5), (8, 2.5), (13, 4), (14, 9.5), (9, 13.5), (4, 12.5)], 4,
                        [((4, 11), (10, 5.5), 1.9), ((8, 10), (11.5, 11), 1.5)]),
        "wolframite":  ([(2, 6), (7, 2.5), (13, 4.5), (13.5, 11), (8, 13.5), (3, 11.5)], 5,
                        [((4, 5.5), (9.5, 10.5), 2.2), ((9, 5), (11.5, 6.5), 1.5)]),
        "chromite":    ([(3, 5.5), (8.5, 2), (13.5, 6), (12, 12.5), (6, 14), (2.5, 10)], 6,
                        [((4.5, 10.5), (11, 5), 2.0), ((8, 11), (11, 10), 1.5)]),
        "pyrolusite":  ([(2.5, 8.5), (5, 3.5), (10.5, 3), (14, 7.5), (12, 12.5), (6, 13.5)], 7,
                        [((6, 12), (10, 4.5), 1.8), ((7, 8), (11, 8.5), 1.4)]),
        "cobaltite":   ([(8, 1.5), (13.5, 5.5), (12.5, 11.5), (7, 14.5), (2.5, 10.5), (3, 5)], 8,
                        [((4.5, 9), (10.5, 4.5), 2.0), ((7, 12), (10.5, 9.5), 1.5)]),
        "molybdenite": ([(2, 9), (3, 5), (8, 3), (13.5, 5.5), (14, 10.5), (8, 13), (3.5, 12.5)], 9,
                        [((4, 9), (11, 6), 1.8), ((5, 11.5), (10, 10.5), 1.5)]),
        "rutile":      ([(3.5, 12.5), (2.5, 7), (6, 3), (11.5, 2.5), (14, 8), (11, 13.5)], 10,
                        [((5, 11), (11, 5), 1.8), ((8, 12), (12, 9), 1.4)]),
        "graphite":    ([(2, 7.5), (5.5, 3.5), (11, 3.5), (14, 8), (10.5, 12.5), (4, 12)], 11,
                        [((4, 9.5), (11, 6), 1.9), ((6, 11), (10, 10.5), 1.4)]),
    }
    if mid in rocks:
        pts, sd, acc = rocks[mid]
        fill = facet_rock(pts, host, rp, seed=sd, accents_=acc)
    elif mid == "halite":      # друза кубических кристаллов
        fill = {}
        for pts in ([(3, 9), (6.5, 7), (9, 10), (6, 13)], [(7, 7), (10, 3.5), (13.5, 6), (10.5, 10)],
                    [(2, 12), (5, 10.5), (7.5, 13.5), (4.5, 14.5)]):
            fill.update(facet_rock(pts, rp, tone=0.1))
    elif mid == "sulfur":      # шипастая друза
        fill = {}
        for pts in ([(2, 14), (4.5, 7), (7, 14)], [(5.5, 14), (9, 3), (12.5, 14)], [(10.5, 14), (13, 8), (15, 14)]):
            fill.update(facet_rock(pts, rp, tone=0.05))
    else:                      # spodumene: длинный кристалл-призма
        fill = facet_rock([(4, 14), (2.5, 10.5), (9, 2), (13.5, 3), (13, 7.5), (7, 14.5)], rp, tone=0.05)
    img = T.blank()
    ring = R.selout(fill, set(fill), 0.5)
    for (x, y), c in ring.items():
        T.put(img, x, y, c)
    for (x, y), c in fill.items():
        T.put(img, x, y, c)
    return img


# ----------------------------------------------------------------- слитки

def prism(x0, y0, w, h, d, rp, top=0.16, side=-0.26, front=-0.02, seed=0, bevel_r=1.2):
    """Брус в косой проекции: верх, лицо, правая грань, у каждой свой мягкий градиент."""
    front_m = {(x0 + x, y0 + d + y) for y in range(h) for x in range(w)}
    top_m = R.polygon_mask([(x0 + d, y0), (x0 + w + d, y0), (x0 + w, y0 + d), (x0, y0 + d)])
    side_m = R.polygon_mask([(x0 + w + d, y0), (x0 + w + d, y0 + h), (x0 + w, y0 + d + h), (x0 + w, y0 + d)])
    top_m |= set()
    out = {}
    out.update(layer(side_m, "bevel", rp, seed=seed + 1, R=bevel_r, H=1.0, bias=side, contrast=1.0))
    out.update(layer(front_m, "bevel", rp, seed=seed + 2, R=bevel_r, H=1.4, bias=front, contrast=1.1))
    out.update(layer(top_m, "bevel", rp, seed=seed + 3, R=bevel_r, H=1.2, bias=top, contrast=1.0))
    return out


def ingot_texture(m):
    rp = ramp9(m.ramp, key=("metal", m.id))
    mid = m.id
    L = []
    if mid == "aluminum":      # две тонкие плиты, смещённые друг относительно друга
        L.append(prism(1, 7, 10, 3, 3, rp, seed=1))
        L.append(prism(3, 2, 10, 3, 3, rp, seed=5))
    elif mid == "nickel":      # короткий брусок со скошенными гранями
        L.append(prism(2, 3, 9, 6, 4, rp, seed=9, bevel_r=1.5))
    elif mid == "tungsten":    # тяжёлый шестигранный «кирпич»
        front = R.polygon_mask([(1, 9), (4, 6), (11, 6), (14, 9), (11, 13), (4, 13)])
        L.append(layer(front, "bevel", rp, seed=14, R=2.2, H=2.2, bias=-0.04, contrast=1.15))
        top = R.polygon_mask([(4, 6), (6, 3), (13, 3), (14, 9), (11, 6)])
        L.append(layer(top, "bevel", rp, seed=15, R=1.0, H=1.0, bias=0.14))
    elif mid == "chromium":    # длинный зеркальный стержень с косым бликом
        L.append(prism(0, 6, 12, 3, 3, rp, seed=20, top=0.2))
        for i in range(2, 9):
            L.append({(i, 9): rp[7 if i % 2 else 8]})
    elif mid == "manganese":   # литой слиток с наклонными боками
        front = R.polygon_mask([(1, 13), (15, 13), (12.5, 8), (3.5, 8)])
        L.append(layer(front, "bevel", rp, seed=27, R=1.6, H=1.8, bias=-0.06))
        top = R.polygon_mask([(3.5, 8), (12.5, 8), (11, 4.5), (5, 4.5)])
        L.append(layer(top, "bevel", rp, seed=28, R=1.1, H=1.4, bias=0.16))
    elif mid == "cobalt":      # стопка шайб
        for i, y in enumerate((9, 5, 1)):
            body = R.superellipse(7.5, y + 4, 6.4, 3.2, 2.0)
            L.append(layer(body, "dome", rp, seed=33 + i, R=2.2, H=2.6, bias=-0.08, contrast=1.2))
            cap = R.superellipse(7.5, y + 2.6, 5.4, 2.0, 2.0)
            L.append(layer(cap, "dome", rp, seed=40 + i, R=1.6, H=1.6, bias=0.2, contrast=1.0, spec=0.1))
    elif mid == "molybdenum":  # диагональный цилиндрический пруток
        pts = rot_rect(8, 8, 14.5, 4.2, -38)
        mk = R.polygon_mask(pts)
        L.append(layer(mk, "tent", rp, seed=47, p0=(8 - 7 * math.cos(math.radians(38)), 8 + 7 * math.sin(math.radians(38))),
                       p1=(8 + 7 * math.cos(math.radians(38)), 8 - 7 * math.sin(math.radians(38))), H=3.0,
                       contrast=1.25, spec=0.12))
    elif mid == "titanium":    # шестигранный брусок с рёбрами и торцом
        body = R.polygon_mask([(1, 9), (3.5, 5), (11, 5), (14, 9), (11, 13), (3.5, 13)])
        L.append(layer(body, "tent", rp, seed=51, p0=(1, 9), p1=(14, 9), H=2.8, contrast=1.3))
        cap = R.polygon_mask([(11, 5), (14, 9), (11, 13), (9.5, 9)])
        L.append(layer(cap, "bevel", rp, seed=52, R=1.0, H=1.0, bias=-0.22))
    fill = merge(L)
    img = T.blank()
    ring = R.selout(fill, set(fill), 0.5)
    for (x, y), c in ring.items():
        T.put(img, x, y, c)
    for (x, y), c in fill.items():
        T.put(img, x, y, c)
    return img


# ----------------------------------------------------------------- блоки металлов

def tile_z(fn):
    return {(x, y): fn(x, y) for y in range(N) for x in range(N)}


def plate_height(x, y, x0, y0, w, h, R_=1.6):
    dx = min(x - x0, x0 + w - 1 - x)
    dy = min(y - y0, y0 + h - 1 - y)
    d = min(dx, dy)
    return 1.6 * min(1.0, (d + 0.5) / R_)


def block_texture(m):
    rp = ramp9(m.ramp, key=("metal", m.id))
    mid = m.id
    z = {}
    noise = R.Noise(hash(mid) % 997, 4)
    bias = 0.0
    contrast = 1.25
    if mid == "aluminum":      # 2x2 плиты со скруглённой фаской
        z = tile_z(lambda x, y: plate_height(x % 8, y % 8, 0, 0, 8, 8, 1.4))
    elif mid == "nickel":      # гладкая плита, диагональный отлив
        z = tile_z(lambda x, y: plate_height(x, y, 0, 0, 16, 16, 1.2) + 0.25 * math.sin((x + y) / 3.0))
    elif mid == "tungsten":    # плиты 8x8 + заклёпки
        def f(x, y):
            v = plate_height(x % 8, y % 8, 0, 0, 8, 8, 1.2)
            for (rx, ry) in ((2, 2), (5, 2), (2, 5), (5, 5)):
                dd = math.hypot((x % 8) - rx, (y % 8) - ry)
                if dd < 1.1:
                    v += 1.0 * (1.1 - dd)
            return v
        z = tile_z(f)
    elif mid == "chromium":    # полированные панели с глянцевым бликом
        z = tile_z(lambda x, y: plate_height(x % 16, y % 16, 0, 0, 16, 16, 1.2) + 1.2 * math.exp(-((x - y + 1) ** 2) / 6.0))
        bias = 0.08
    elif mid == "manganese":   # протекторная плита с косыми рёбрами
        def f(x, y):
            v = 1.2
            for (cx, cy, rot) in ((4, 4, 1), (12, 4, -1), (4, 12, -1), (12, 12, 1)):
                for ox in (-16, 0, 16):
                    for oy in (-16, 0, 16):
                        dx, dy = x - cx - ox, y - cy - oy
                        u = (dx + rot * dy) / 1.414
                        w = (dx - rot * dy) / 1.414
                        if abs(u) < 3.0 and abs(w) < 0.9:
                            v += 1.1 * math.sqrt(max(0.0, 1 - (w / 0.9) ** 2)) * (1 - (abs(u) / 3.0) ** 3)
            return v
        z = tile_z(f)
    elif mid == "cobalt":      # квадратная плитка с фасками
        z = tile_z(lambda x, y: plate_height(x % 8, y % 8, 0, 0, 8, 8, 1.5))
    elif mid == "molybdenum":  # кладка
        def f(x, y):
            row = y // 4
            off = 4 if row % 2 else 0
            return plate_height((x + off) % 8, y % 4, 0, 0, 8, 4, 1.0)
        z = tile_z(f)
    elif mid == "titanium":    # вертикальные рёбра-цилиндры
        z = tile_z(lambda x, y: 1.4 * math.sin(math.pi * ((x % 4) + 0.5) / 4.0) + plate_height(x, y, 0, 0, 16, 16, 1.0) * 0.3)
    colors = R.shade(z, rp, noise=noise, noise_amp=0.05, contrast=contrast, bias=bias, wrap=True)
    img = T.blank()
    for (x, y), c in colors.items():
        img.putpixel((x, y), (*c, 255))
    return img
