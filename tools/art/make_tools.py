"""Текстуры ключа и трёх модулей форсирования (16x16, правила: тёмный контур, свет сверху-слева, 6-8 тонов)."""
import math
from pathlib import Path
from PIL import Image

ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
OUT_D = (22, 24, 31)      # контур: холодный тёмный
OUT_D2 = (36, 40, 52)


def put(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), (*c, 255))


def outline(im, mask_px):
    """Контур тёмным вокруг заливки (по 4 соседям)."""
    w, h = im.size
    pts = set(mask_px)
    for (x, y) in list(pts):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in pts and 0 <= n[0] < w and 0 <= n[1] < h:
                put(im, n[0], n[1], OUT_D)


STEEL = [(58, 64, 78), (88, 97, 114), (128, 139, 158), (172, 184, 204), (214, 224, 238)]
GRIP = [(96, 40, 24), (150, 66, 30), (204, 104, 40), (240, 156, 66)]


def wrench():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    # ось от (2.5, 13.5) к (10.5, 5.5); ширина 3
    ax, ay, bx, by = 2.5, 13.5, 10.5, 5.5
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px_, py_ = -uy, ux            # нормаль (вправо-вниз)
    body = {}
    for y in range(16):
        for x in range(16):
            cx, cy = x + 0.5, y + 0.5
            t = ((cx - ax) * ux + (cy - ay) * uy)
            d = ((cx - ax) * px_ + (cy - ay) * py_)
            if -0.5 <= t <= L + 0.2 and abs(d) <= 1.5:
                body[(x, y)] = (t, d)
    # головка: круг + прорезь
    hx, hy = 11.5, 4.5
    head = {}
    for y in range(16):
        for x in range(16):
            r = math.hypot(x + 0.5 - hx, y + 0.5 - hy)
            if r <= 3.7:
                head[(x, y)] = r
    notch = set()
    for (x, y) in list(head):
        # прорезь открывается вверх-вправо
        nx, ny = x + 0.5 - hx, y + 0.5 - hy
        along = nx * 0.7071 - ny * 0.7071
        across = abs(nx * 0.7071 + ny * 0.7071)
        if along > 0.4 and across < 1.35:
            notch.add((x, y))
    for p in notch:
        head.pop(p)
    allpx = set(body) | set(head)
    for p in notch:
        allpx.discard(p)
    for (x, y) in allpx:
        if (x, y) in head:
            r = head[(x, y)]
            lit = (hx - (x + 0.5)) * 0.7 + (hy - (y + 0.5)) * 0.7      # ближе к верху-слева светлее
            k = 2 + (1 if lit > 1.2 else 0) + (1 if lit > 2.4 else 0) - (1 if lit < -1.2 else 0) - (1 if lit < -2.4 else 0)
            put(im, x, y, STEEL[max(0, min(4, k))])
        else:
            t, d = body[(x, y)]
            if t < 5.2:
                k = 2 if d < -0.5 else 1 if d < 0.6 else 0
                k = {2: 3, 1: 2, 0: 1}[k] if d >= -0.5 else 3
                put(im, x, y, GRIP[max(0, min(3, 3 if d < -0.5 else 2 if d < 0.6 else 1))])
            else:
                put(im, x, y, STEEL[3 if d < -0.5 else 2 if d < 0.6 else 1])
    outline(im, allpx)
    # блик
    for (x, y) in sorted(allpx):
        pass
    im.save(ITEM / "wrench.png")


def module(name, die, pcb, pips):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pts = set()
    for y in range(3, 13):
        for x in range(3, 13):
            pts.add((x, y))
    for (x, y) in pts:
        shade = 1 if (x == 3 or y == 3) else -1 if (x == 12 or y == 12) else 0
        base = pcb[1 + shade] if 0 <= 1 + shade < len(pcb) else pcb[1]
        put(im, x, y, base)
    # контакты по краям (золотые)
    gold = [(150, 106, 30), (214, 168, 52), (255, 226, 120)]
    for i in range(4, 12, 2):
        for (x, y) in ((i, 2), (i, 13), (2, i), (13, i)):
            put(im, x, y, gold[1])
            pts.add((x, y))
        put(im, i, 2, gold[2]); put(im, 2, i, gold[2])
        put(im, i, 13, gold[0]); put(im, 13, i, gold[0])
    # кристалл-кристалл: 4x4 в центре
    for y in range(5, 9):
        for x in range(5, 9):
            k = 2 if (x + y) <= 11 and (x == 5 or y == 5) else 1 if x < 8 and y < 8 else 0
            put(im, x, y, die[k])
    # пины тира: 1-3 точки справа снизу
    for i in range(pips):
        put(im, 6 + i * 2, 10, die[2]); put(im, 6 + i * 2, 11, die[0])
    # дорожки
    put(im, 10, 5, pcb[2]); put(im, 10, 6, pcb[2]); put(im, 9, 7, pcb[2]); put(im, 10, 8, pcb[2])
    outline(im, pts)
    im.save(ITEM / f"module_{name}.png")


if __name__ == "__main__":
    wrench()
    PCB = [(34, 78, 62), (46, 104, 82), (84, 156, 122)]                   # зелёная плата
    module("worker", [(26, 92, 58), (62, 190, 104), (170, 255, 190)], PCB, 1)
    module("industrial", [(150, 90, 14), (240, 176, 40), (255, 238, 150)], PCB, 2)
    module("peak", [(30, 84, 170), (84, 170, 255), (200, 236, 255)], PCB, 3)
