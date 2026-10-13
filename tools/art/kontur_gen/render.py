"""Мини-рендерер пиксель-арта в ванильном духе.

Объекты описываются картой высот; свет падает сверху-слева, результат квантуется в
рампу из 9 тонов (как в ванильных текстурах), с мягкими переходами, бликом и тёмным
контуром цвета объекта. Никакого шума «точками»: только сглаженная вариация.
"""
import colorsys
import math
import random

N = 16
LIGHT = (-0.52, -0.62, 0.59)


# --------------------------------------------------------------------- цвет

def _hsv(c):
    return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def lerp(a, b, t):
    return tuple(int(a[i]) + (int(b[i]) - int(a[i])) * t for i in range(3))


def expand_ramp(stops, n=9, shadow_shift=-0.035, light_shift=0.012):
    """Из 4-5 опорных цветов строит рампу из n тонов с ванильным сдвигом оттенка:
    тени уходят в холодную сторону и насыщаются, света становятся теплее и бледнее."""
    out = []
    m = len(stops) - 1
    for i in range(n):
        t = i / (n - 1) * m
        k = min(int(t), m - 1)
        c = lerp(stops[k], stops[k + 1], t - k)
        c = tuple(int(round(v)) for v in c)
        u = i / (n - 1)
        h, s, v = _hsv(c)
        if u < 0.5:
            w = (0.5 - u) / 0.5
            h += shadow_shift * w
            s *= 1 + 0.16 * w
        elif u > 0.6:
            w = (u - 0.6) / 0.4
            h += light_shift * w
            s *= 1 - 0.28 * w
        out.append(_rgb(h, s, v))
    return out


def darken(c, k=0.55, sat=1.18, shift=-0.02):
    h, s, v = _hsv(c)
    return _rgb(h + shift, s * sat, v * k)


# --------------------------------------------------------------------- шум

class Noise:
    def __init__(self, seed=1, cell=4):
        r = random.Random(seed)
        self.cell = cell
        self.g = [[r.uniform(-1, 1) for _ in range(N // cell + 2)] for _ in range(N // cell + 2)]

    def __call__(self, x, y):
        c = self.cell
        gx, gy = x / c, y / c
        x0, y0 = int(gx), int(gy)
        fx, fy = gx - x0, gy - y0
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        a = self.g[y0][x0] * (1 - fx) + self.g[y0][x0 + 1] * fx
        b = self.g[y0 + 1][x0] * (1 - fx) + self.g[y0 + 1][x0 + 1] * fx
        return a * (1 - fy) + b * fy


# --------------------------------------------------------------------- формы

def disk_mask(cx, cy, r):
    return {(x, y) for y in range(N) for x in range(N) if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}


def blob(cx, cy, r, seed=0, wob=0.22, sx=1.0, sy=1.0, rot=0.0):
    """Органичный «окатыш»: радиус плавно меняется по углу."""
    rnd = random.Random(seed)
    p1, p2, p3 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    a1, a2 = rnd.uniform(0.5, 1), rnd.uniform(0.3, 0.8)
    out = set()
    ca, sa = math.cos(rot), math.sin(rot)
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            ux, uy = (dx * ca + dy * sa) / sx, (-dx * sa + dy * ca) / sy
            th = math.atan2(uy, ux)
            rr = r * (1 + wob * (a1 * math.sin(2 * th + p1) + a2 * math.sin(3 * th + p2)) * 0.6
                      + wob * 0.25 * math.sin(5 * th + p3))
            if math.hypot(ux, uy) <= rr:
                out.add((x, y))
    return out


def polygon_mask(pts):
    from PIL import Image, ImageDraw
    im = Image.new("L", (N, N), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return {(x, y) for y in range(N) for x in range(N) if im.getpixel((x, y))}


def line_mask(p0, p1, w=1.0):
    out = set()
    x0, y0 = p0
    x1, y1 = p1
    L = max(1e-6, math.hypot(x1 - x0, y1 - y0))
    for y in range(N):
        for x in range(N):
            px, py = x + 0.5, y + 0.5
            t = max(0, min(1, ((px - x0) * (x1 - x0) + (py - y0) * (y1 - y0)) / (L * L)))
            if math.hypot(px - (x0 + t * (x1 - x0)), py - (y0 + t * (y1 - y0))) <= w / 2:
                out.add((x, y))
    return out


def superellipse(cx, cy, rx, ry, p=3.2, rot=0.0):
    out = set()
    ca, sa = math.cos(rot), math.sin(rot)
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            ux, uy = dx * ca + dy * sa, -dx * sa + dy * ca
            if abs(ux / rx) ** p + abs(uy / ry) ** p <= 1:
                out.add((x, y))
    return out


def roughen(mask, seed=0, amount=0.5):
    """Слегка обкусывает/наращивает край, чтобы не было идеальной геометрии."""
    rnd = random.Random(seed)
    out = set(mask)
    for (x, y) in mask:
        edge = any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge and rnd.random() < amount * 0.35:
            out.discard((x, y))
    return out


# --------------------------------------------------------------------- освещение

def dist_inside(mask):
    d = {}
    for (x, y) in mask:
        best = 99.0
        for yy in range(y - 4, y + 5):
            for xx in range(x - 4, x + 5):
                if (xx, yy) not in mask:
                    best = min(best, math.hypot(xx - x, yy - y))
        d[(x, y)] = best
    return d


def height_dome(mask, R=3.0, H=2.6):
    d = dist_inside(mask)
    z = {}
    for p, v in d.items():
        t = min(1.0, max(0.0, (v - 0.5) / R))
        z[p] = H * math.sqrt(max(0.0, 1 - (1 - t) ** 2))
    return z


def height_bevel(mask, R=1.6, H=1.4):
    """Плоская лицевая сторона и узкая фаска по краю (плиты, кирпичи)."""
    d = dist_inside(mask)
    z = {}
    for p, v in d.items():
        t = min(1.0, max(0.0, (v - 0.5) / R))
        z[p] = H * t
    return z


def height_tent(mask, p0, p1, H=2.6):
    """Призма/«крыша»: гребень вдоль оси p0-p1, две грани по сторонам (кристалл)."""
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    z = {}
    d = dist_inside(mask)
    w = max(abs((px + 0.5 - x0) * -uy + (py + 0.5 - y0) * ux) for (px, py) in mask) or 1
    for (px, py) in mask:
        across = abs((px + 0.5 - x0) * -uy + (py + 0.5 - y0) * ux)
        base = H * (1 - across / (w + 0.6))
        z[(px, py)] = base * min(1.0, d[(px, py)] / 1.2 + 0.25)
    return z


def height_pyramid(mask, cx, cy, H=2.8, norm="l1", sx=1.0, sy=1.0):
    z = {}
    d = dist_inside(mask)
    ext = 0.01
    for (x, y) in mask:
        dx, dy = abs(x + 0.5 - cx) / sx, abs(y + 0.5 - cy) / sy
        ext = max(ext, (dx + dy) if norm == "l1" else max(dx, dy))
    for (x, y) in mask:
        dx, dy = abs(x + 0.5 - cx) / sx, abs(y + 0.5 - cy) / sy
        r = (dx + dy) if norm == "l1" else max(dx, dy)
        z[(x, y)] = H * (1 - r / (ext + 0.7)) * min(1.0, d[(x, y)] / 1.0 + 0.3)
    return z


def shade(z, ramp, noise=None, noise_amp=0.07, light=LIGHT, contrast=1.15, bias=0.0, wrap=False, spec=0.0, rim=0.11):
    """Карта высот -> {пиксель: цвет рампы}. Нормали по разностям высот; за пределами маски высота 0."""
    lx, ly, lz = light
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    n = len(ramp)
    out = {}
    for (x, y), h in z.items():
        def zz(a, b):
            if wrap:
                return z.get((a % N, b % N), 0.0)
            return z.get((a, b), 0.0)
        gx = (zz(x + 1, y) - zz(x - 1, y)) * 0.5
        gy = (zz(x, y + 1) - zz(x, y - 1)) * 0.5
        nx, ny, nz = -gx, -gy, 1.0
        m = math.sqrt(nx * nx + ny * ny + nz * nz)
        d = (nx * lx + ny * ly + nz * lz) / m
        s = 0.5 + (d - 0.59) * contrast + bias
        s += min(0.25, max(0.0, h) * 0.035) * 0.0
        if noise is not None:
            s += noise(x, y) * noise_amp
        if spec and d > 0.93:
            s += spec
        if rim and not wrap and ((x + 1, y) not in z or (x, y + 1) not in z):
            s += rim  # отражённый свет на нижней/правой кромке
        idx = int(round(max(0.0, min(1.0, s)) * (n - 1)))
        out[(x, y)] = ramp[idx]
    return out


def selout(fill, canvas_mask, strength=0.5):
    """Контур цвета объекта: на освещённой стороне (сверху/слева) светлее, в тени (снизу/справа) темнее,
    тени смещены в холодную сторону. Никакого чистого чёрного."""
    ring = {}
    for (x, y) in canvas_mask:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            q = (x + dx, y + dy)
            if q in canvas_mask or not (0 <= q[0] < N and 0 <= q[1] < N):
                continue
            ring.setdefault(q, []).append((fill[(x, y)], dx, dy))
    out = {}
    for q, lst in ring.items():
        lst.sort(key=lambda t: abs(t[1]) + abs(t[2]))
        c, dx, dy = lst[0]
        # q = пиксель объекта + (dx, dy): dx>0/dy>0 -> контур справа/снизу (тень)
        shade_side = (1 if dx > 0 else 0) + (1 if dy > 0 else 0) - (1 if dx < 0 else 0) * 0.6 - (1 if dy < 0 else 0) * 0.6
        k = 0.66 - 0.12 * shade_side
        out[q] = darken(c, max(0.34, min(0.8, k)), 1.2, -0.025)
    return out
