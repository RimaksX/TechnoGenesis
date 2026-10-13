"""Куски сырой руды: у каждого минерала свой силуэт, нарисованный чёткими плоскими гранями.

Свет сверху-слева: верхние/левые грани светлые (тона 6-8), правые/нижние тёмные (1-3),
контур снизу-справа самый тёмный, сверху-слева мягче (как у ванильных raw_iron/raw_gold).
"""
import math
from PIL import Image, ImageDraw
from . import render as R
from . import textures as T
from .designs import ramp9

N = 16


SCALE = 0.86     # рисунок сжимается к центру: вместе с контуром отступ от края >= 1 px
CENTER = 8.0


def _sp(pt):
    return (CENTER + (pt[0] - CENTER) * SCALE, CENTER + (pt[1] - CENTER) * SCALE)


class Sprite:
    def __init__(self, ramps):
        self.ramps = ramps          # {'m': ramp9, 'h': ramp9, ...}
        self.px = {}                # (x, y) -> (ramp_key, tone)

    def _mask(self, drawfn):
        im = Image.new("L", (N, N), 0)
        drawfn(ImageDraw.Draw(im))
        return {(x, y) for y in range(N) for x in range(N) if im.getpixel((x, y))}

    def poly(self, pts, tone, ramp="m", clip=None):
        pts = [_sp(p) for p in pts]
        m = self._mask(lambda d: d.polygon(pts, fill=255))
        return self.fill(m, tone, ramp, clip)

    def ell(self, cx, cy, rx, ry, tone, ramp="m", clip=None):
        cx, cy = _sp((cx, cy))
        rx, ry = rx * SCALE, ry * SCALE
        m = {(x, y) for y in range(N) for x in range(N)
             if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0}
        return self.fill(m, tone, ramp, clip)

    def line(self, p0, p1, w, tone, ramp="m", clip=None):
        m = R.line_mask(_sp(p0), _sp(p1), w * SCALE)
        return self.fill(m, tone, ramp, clip)

    def pixels(self, pts, tone, ramp="m"):
        """Точечные блики/тени: координаты масштабируются вместе с рисунком."""
        for pt in pts:
            q = _sp(pt)
            self.px[(int(round(q[0])), int(round(q[1])))] = (ramp, tone)

    def fill(self, mask, tone, ramp="m", clip=None):
        for p in mask:
            if clip is None or p in clip:
                self.px[p] = (ramp, tone)
        return mask

    def ball(self, cx, cy, r, ramp="m", base=4):
        body = self.ell(cx, cy, r, r, base, ramp)
        cx, cy = _sp((cx, cy))
        r = r * SCALE
        lit = {(x, y) for y in range(N) for x in range(N)
               if math.hypot(x + 0.5 - (cx - 1.3), y + 0.5 - (cy - 1.4)) <= r * 0.92}
        shade = {p for p in body if p not in lit}
        self.fill(shade, base - 2, ramp)
        mid = {(x, y) for (x, y) in body if math.hypot(x + 0.5 - (cx - 1.0), y + 0.5 - (cy - 1.1)) <= r * 0.62}
        self.fill(mid, base + 2, ramp)
        hl = {(x, y) for (x, y) in body if math.hypot(x + 0.5 - (cx - 1.5), y + 0.5 - (cy - 1.7)) <= r * 0.32}
        self.fill(hl, base + 3, ramp)
        return body

    def lump(self, cx, cy, rx, ry, rot=0.0, ramp="m", base=4, glints=True):
        """Округлая глыба: светлая верхне-левая часть, тёмный нижне-правый серп, блик (приём как у боксита)."""
        cx, cy = _sp((cx, cy))
        rx, ry = rx * SCALE, ry * SCALE
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

        def inside(x, y, ox=0.0, oy=0.0, k=1.0):
            dx, dy = x + 0.5 - (cx + ox), y + 0.5 - (cy + oy)
            u, v = dx * ca + dy * sa, -dx * sa + dy * ca
            return (u / (rx * k)) ** 2 + (v / (ry * k)) ** 2 <= 1.0

        grid = [(x, y) for y in range(N) for x in range(N)]
        body = {p for p in grid if inside(*p)}
        self.fill(body, base, ramp)
        lit = {p for p in body if inside(p[0], p[1], -1.3, -1.4, 0.92)}
        self.fill(body - lit, base - 2, ramp)
        self.fill({p for p in body if inside(p[0], p[1], -1.0, -1.1, 0.62)}, base + 2, ramp)
        if glints:
            self.fill({p for p in body if inside(p[0], p[1], -1.5, -1.7, 0.32)}, base + 3, ramp)
        return body

    def render(self):
        img = T.blank()
        shape = set(self.px)
        out = {}
        for (x, y), (rk, t) in self.px.items():
            t2 = t
            # блик по верхне-левой кромке силуэта
            if ((x, y - 1) not in shape or (x - 1, y) not in shape) and t >= 3:
                t2 = min(8, t + 1)
            # мягкий отражённый свет по нижне-правой кромке
            if ((x + 1, y) not in shape or (x, y + 1) not in shape) and t <= 2:
                t2 = min(8, t + 1)
            out[(x, y)] = self.ramps[rk][max(0, min(8, t2))]
        # контур: снизу/справа самый тёмный, сверху/слева мягче
        for (x, y), (rk, t) in self.px.items():
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                q = (x + dx, y + dy)
                if q in shape or not (0 <= q[0] < N and 0 <= q[1] < N):
                    continue
                shadow_side = (dx > 0) + (dy > 0) - (dx < 0) * 0.5 - (dy < 0) * 0.5
                tone = 0 if shadow_side >= 1 else (1 if shadow_side >= 0 else 2)
                c = self.ramps[rk][tone]
                prev = out.get(q)
                if prev is None or sum(c) < sum(prev):
                    out[q] = c
        for (x, y), c in out.items():
            T.put(img, x, y, c)
        return img


# ---------------------------------------------------------------- рисунки

def host_ramp(m, k=0.62, sat=0.5):
    return ramp9([T.desat(T.scale(c, k), sat) for c in m.ramp[:5]], key=("rawhost", m.id, k))


def lifted(m, k, key):
    """Тёмные минералы: поднимаем средние тона, чтобы глыбы читались (тёмный контур сохраняется)."""
    st = list(m.ramp[:5])
    st = [st[0]] + [tuple(min(255, int(v * k)) for v in c) for c in st[1:]]
    return ramp9(st, key=(key, m.id, k))


def sprite_for(m):
    mid = m.id
    main = ramp9(m.ramp, key=("ore", m.id))
    sp = Sprite({"m": main, "h": host_ramp(m)})
    L = sp.lump

    if mid == "bauxite":              # скопление округлых окатышей (эталон: оставлен как есть)
        sp.ball(5.6, 9.6, 4.3)
        sp.ball(10.8, 9.4, 3.9)
        sp.ball(8.2, 5.2, 3.5)
        sp.pixels([(7, 6)], 7)
    elif mid == "garnierite":         # наклонная плита тёмно-зелёной породы с яркой яблочно-зелёной жилой
        sp.ramps["h"] = host_ramp(m, 0.7, 0.55)
        L(7.8, 9.0, 5.8, 3.5, -16, "h", 4)
        L(11.2, 5.6, 3.0, 2.5, 0, "h", 5)
        L(4.2, 11.8, 2.6, 2.0, 8, "h", 3)
        inside = set(sp.px)
        sp.line((3.0, 12.2), (7.5, 8.4), 2.0, 4, "m", clip=inside)       # тело жилы
        sp.line((7.5, 8.4), (13.0, 5.2), 1.8, 4, "m", clip=inside)
        sp.line((3.2, 11.4), (7.5, 7.6), 0.9, 7, "m", clip=inside)       # блик по верхней кромке жилы
        sp.line((7.7, 7.6), (12.6, 4.6), 0.9, 7, "m", clip=inside)
        sp.line((4.0, 13.0), (8.2, 9.4), 0.8, 2, "m", clip=inside)       # тень по нижней кромке
        sp.ball(5.6, 12.6, 1.5, "m", base=4)                              # колломорфные натёки у основания
        sp.ball(9.2, 11.4, 1.3, "m", base=4)
    elif mid == "wolframite":         # тёмные тяжёлые глыбы, широкий низкий силуэт
        sp.ramps["m"] = lifted(m, 1.2, "wolf")
        L(4.8, 9.6, 3.9, 3.3, -8, "m", 4)
        L(10.6, 9.2, 3.8, 3.6, 10, "m", 4)
        L(7.8, 5.6, 3.2, 2.7, 0, "m", 5)
        sp.pixels([(6, 4), (9, 7), (4, 8)], 8)
    elif mid == "chromite":           # уголок из трёх глыб: серо-зелёная порода с серебристыми включениями
        sp.ramps["h"] = host_ramp(m, 1.0, 0.45)
        sp.ramps["m"] = lifted(m, 1.3, "chrom")
        L(5.4, 5.4, 3.1, 2.9, 0, "h", 5)
        L(5.8, 10.6, 3.6, 3.3, 0, "h", 4)
        L(10.8, 10.4, 3.5, 3.3, 0, "h", 4)
        L(5.0, 5.0, 1.4, 1.2, 0, "m", 5)
        L(10.6, 10.0, 1.5, 1.2, 0, "m", 5)
        sp.pixels([(4, 4), (9, 9), (6, 9)], 8, "m")
    elif mid == "pyrolusite":         # гроздь сажистых почек (ботриоидальный агрегат)
        sp.ramps["m"] = lifted(m, 1.75, "pyro")
        for (cx, cy, r) in [(4.4, 10.6, 2.7), (8.4, 11.4, 2.8), (11.8, 9.6, 2.6), (6.2, 6.8, 2.7), (10.2, 6.2, 2.6),
                            (8.0, 3.6, 2.3), (4.0, 5.4, 1.9)]:
            sp.ball(cx, cy, r, "m", base=4)
        sp.pixels([(7, 3), (5, 6), (9, 6)], 8)
    elif mid == "cobaltite":          # диагональная цепочка серебристо-розовых глыб
        sp.ramps["m"] = lifted(m, 1.18, "cob")
        sp.ramps["h"] = host_ramp(m, 1.1, 0.35)
        L(4.8, 10.8, 3.4, 3.1, 0, "h", 4)
        L(8.4, 8.4, 4.2, 3.8, 20, "h", 4)
        L(11.6, 5.0, 3.2, 3.0, 0, "h", 5)
        L(8.2, 8.0, 2.0, 1.7, 0, "m", 5)
        L(11.2, 4.8, 1.4, 1.3, 0, "m", 5)
        L(4.6, 10.8, 1.5, 1.3, 0, "m", 5)
        sp.pixels([(10, 4), (7, 7)], 8)
    elif mid == "molybdenite":        # стопка плоских «блинов» свинцово-голубого цвета
        L(8.0, 11.0, 5.6, 2.7, -3, "m", 3)
        L(8.2, 7.8, 5.2, 2.5, 3, "m", 4)
        L(7.6, 4.8, 4.2, 2.1, -4, "m", 5)
        sp.pixels([(4, 4), (7, 7), (5, 10)], 8)
    elif mid == "rutile":             # веер из трёх игольчатых агрегатов, расходящийся из одной точки
        sp.ramps["m"] = lifted(m, 1.25, "rut")
        for (ang, ln, base_t) in ((-18, 4.7, 3), (-48, 5.0, 4), (-78, 4.6, 5)):
            r = math.radians(ang)
            L(4.6 + math.cos(r) * ln * 0.9, 12.2 + math.sin(r) * ln * 0.9, ln, 1.9, ang, "m", base_t)
        sp.pixels([(11, 10), (9, 6), (5, 5)], 8)
    elif mid == "graphite":           # две крупные чешуйчатые глыбы, тёмные с блеском
        sp.ramps["m"] = lifted(m, 1.4, "graph")
        L(5.4, 9.0, 4.4, 4.4, -25, "m", 4)
        L(10.8, 8.4, 3.8, 4.9, 20, "m", 4)
        L(8.0, 5.0, 3.0, 2.0, 0, "m", 5)
        sp.pixels([(5, 6), (9, 4), (10, 7)], 8)
    elif mid == "halite":             # светлые глыбы каменной соли, полупрозрачные, с лёгкой тенью
        sp.ramps["m"] = lifted(m, 0.9, "salt")
        L(5.0, 9.8, 3.9, 3.5, 12, "m", 4)
        L(10.4, 10.0, 3.4, 3.0, -8, "m", 4)
        L(8.2, 5.4, 3.6, 3.1, 0, "m", 5)
        L(11.4, 5.8, 1.7, 1.5, 0, "m", 5)
        sp.pixels([(6, 4), (4, 8)], 8)
    elif mid == "sulfur":             # бугристая жёлтая корка на буром основании
        L(8.0, 10.0, 5.6, 3.6, 0, "h", 3)
        for (cx, cy, r) in [(4.6, 7.8, 2.1), (7.8, 6.2, 2.4), (11.0, 7.6, 2.1), (6.0, 10.6, 1.9), (10.0, 10.4, 2.0)]:
            sp.ball(cx, cy, r, "m", base=4)
    elif mid == "spodumene":          # вытянутая сиреневая глыба с двумя спутниками
        L(8.0, 8.0, 5.4, 3.7, -35, "m", 4)
        L(4.6, 11.6, 2.4, 2.1, 0, "m", 4)
        L(11.8, 4.6, 2.2, 1.9, 0, "m", 5)
        sp.pixels([(9, 5), (6, 9)], 8)
    return sp


def raw_texture(m):
    return sprite_for(m).render()
