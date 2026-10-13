"""Готовые модели собираемых игроком машин: реактор, турбина, градирня, доменная печь. Строятся по тем же правилам, что и крупные
машины обработки: рама-каркас по клеткам (chassis без гнёзд - порты здесь настоящие блоки), крупные сварные корпуса с поясами,
катушки, шкафы с проводкой, лестницы, приборы; затем автоматически расставляются узлы (щит питания, насосы, баки) и
прокладываются провода. Лицо - сторона north (z = 0), контроллер в центре передней стенки на втором ряду."""
from .multi import (Big, chassis, weld, ribbed, coil, insul, cab, pw, dial, vent, ladder, band_sides, valve, bolts, liquid,
                    panel, sieve)
from .machines3d import (fan, pane, brick, louver, mouth, glow, hotwin, corrug, tread, cast, tiles, paneled, ribs, melt, slats, wind2, pipe_mat, console_mat, hull, tube, winding, deck, grille, lamps,
                         GREEN, AMBER, ORANGE, PLASMA, WATER, STEAM, view_mat)
from . import machines3d as MM

STEEL = (112, 116, 126)
HOT = (255, 176, 96)


def oct_y(m, x0, z0, x1, z1, y0, y1, side, top="light", c=3):
    """Вертикальный сосуд-восьмигранник (ступенчатое срезание углов)."""
    mats = {"u": top, "d": top, "*": side}
    m.box([x0, y0, z0 + c], [x1, y1, z1 - c], mats)
    m.box([x0 + c, y0, z0], [x1 - c, y1, z0 + c], mats)
    m.box([x0 + c, y0, z1 - c], [x1 - c, y1, z1], mats)


def oct_x(m, x0, x1, y0, y1, z0, z1, side, end="light", c=3):
    """Лежащий вдоль x цилиндр-восьмигранник (как в автоклаве): без перекрытия объёмов."""
    mats = {"e": end, "w": end, "*": side}
    m.box([x0, y0 + c, z0], [x1, y1 - c, z1], mats)
    m.box([x0, y1 - c, z0 + c], [x1, y1, z1 - c], mats)
    m.box([x0, y0, z0 + c], [x1, y0 + c, z1 - c], mats)


def oct_z(m, x0, x1, y0, y1, z0, z1, side, end="light", c=3):
    """Лежащий вдоль z цилиндр-восьмигранник."""
    mats = {"n": end, "s": end, "*": side}
    m.box([x0, y0 + c, z0], [x1, y1 - c, z1], mats)
    m.box([x0 + c, y1 - c, z0], [x1 - c, y1, z1], mats)
    m.box([x0 + c, y0, z0], [x1 - c, y0 + c, z1], mats)


def rungs_z(m, x0, x1, y0, y1, zs, mat="dark"):
    """Бандажи-кольца вокруг лежащего вдоль z цилиндра: тонкие рёбра сверху, снизу и по бокам."""
    for z in zs:
        m.box([x0 + 3, y1, z], [x1 - 3, y1 + 1, z + 1], mat)
        if y0 > 2:
            m.box([x0 + 3, y0 - 1, z], [x1 - 3, y0, z + 1], mat)
        m.box([x0 - 1, y0 + 3, z], [x0, y1 - 3, z + 1], mat)
        m.box([x1, y0 + 3, z], [x1 + 1, y1 - 3, z + 1], mat)


def rungs_x(m, z0, z1, y0, y1, xs, mat="dark"):
    for x in xs:
        m.box([x, y1, z0 + 3], [x + 1, y1 + 1, z1 - 3], mat)
        m.box([x, y0 - 1, z0 + 3], [x + 1, y0, z1 - 3], mat)
        m.box([x, y0 + 3, z0 - 1], [x + 1, y1 - 3, z0], mat)
        m.box([x, y0 + 3, z1], [x + 1, y1 - 3, z1 + 1], mat)


def banded_column(m, x0, z0, w, y0, y1, bands, base=(104, 108, 120)):
    """Стойка из стальных секций и медных обмоток между ними."""
    y = y0
    for (a, b) in bands:
        m.box([x0, y, z0], [x0 + w, a, z0 + w], weld(base))
        m.box([x0 + 1, a, z0 + 1], [x0 + w - 1, b, z0 + w - 1], coil())
        m.box([x0, a, z0], [x0 + 1, b, z0 + w], "dark")
        m.box([x0 + w - 1, a, z0], [x0 + w, b, z0 + w], "dark")
        y = b
    m.box([x0, y, z0], [x0 + w, y1, z0 + w], weld(base))


def hatch(m, x, y, z, face="n", size=6):
    """Люк-лаз с болтами на стенке сосуда: пластина size x size, выступает на 1 от грани."""
    h = size // 2
    if face == "n":
        m.box([x - h, y - h, z - 1], [x + h, y + h, z], bolts((176, 178, 184)))
    elif face == "s":
        m.box([x - h, y - h, z], [x + h, y + h, z + 1], bolts((176, 178, 184)))
    elif face == "w":
        m.box([x - 1, y - h, z - h], [x, y + h, z + h], bolts((176, 178, 184)))
    else:
        m.box([x, y - h, z - h], [x + 1, y + h, z + h], bolts((176, 178, 184)))


def nozzle(m, x, y, z, h=4, w=4, wheel=True):
    """Патрубок сверху сосуда: короткая труба с фланцем и вентилем."""
    m.box([x, y, z], [x + w, y + h, z + w], "steel")
    m.box([x - 1, y + h, z - 1], [x + w + 1, y + h + 1, z + w + 1], "light")
    if wheel:
        valve(m, x, y + h + 1, z, w, w)


def magnet(m, a, b):
    """Магнит-обойма кольца: стальные торцы и медная обмотка по бокам."""
    m.box(a, b, {"u": "steel", "d": "steel", "*": wind2((184, 108, 66), "h")})


def tank_y(m, x0, z0, x1, z1, y0, y1, rgb, bands=(), acc=None):
    """Вертикальный бак с трубками на стенках, бандажами и крышкой с люком."""
    m.box([x0, y0, z0], [x1, y1, z1], pw(rgb, tuple(min(255, c + 52) for c in rgb), "nsew"))
    for y in bands:
        band_sides(m, x0, z0, x1, z1, y, "lrbf")
    m.box([x0 + 1, y1, z0 + 1], [x1 - 1, y1 + 1, z1 - 1], "dark")
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    m.box([cx - 1, y1 + 1, cz - 1], [cx + 1, y1 + 2, cz + 1], "light")


def frame(m):
    """Основание машины: плита-цоколь с кромкой и панелью индикаторов спереди (рамы по периметру нет)."""
    X, Z, xm = m.X, m.Z, m.xm
    m.box([0, 0, 0], [X, 2, Z], hull((60, 62, 70), 16))
    m.box([xm + 4, 2, 0], [xm + 12, 3, 2], {"n": console_mat(MM.GL, None), "u": "dark", "*": "dark"})


# ---------------------------------------------------------------- термоядерный реактор

def fusion_reactor():
    """Термоядерный реактор 5x5x4: в центре на высоком постаменте кольцо токамака из медных магнитов со стальными стяжками и
    небольшими окнами, светящимися изнутри при работе, вокруг соленоида со стальной паровой трубой; сзади лежащий паровой барабан
    на седлах, слева три трансформатора, справа три сосуда хладагента ступенями, спереди пульт управления."""
    m = Big("fusion_reactor", 5, 5, 4)
    frame(m)
    R = 20                                                                     # высота низа кольца
    oct_y(m, 16, 16, 64, 64, 2, R, tread((88, 92, 104)), "light", c=10)
    for y in (6, 12):
        band_sides(m, 16, 26, 64, 54, y, "lrbf", "dark") if False else None
    for (lo, hi, ax) in ((16, 28, "x"), (52, 64, "x"), (16, 28, "z"), (52, 64, "z")):
        for (a_, b_, k) in ((28, 34, "m"), (34, 36, "t"), (36, 44, "m"), (44, 46, "t"), (46, 52, "m")):
            A, B = ([a_, R, lo], [b_, R + 16, hi]) if ax == "x" else ([lo, R, a_], [hi, R + 16, b_])
            if k == "m":
                magnet(m, A, B)
            else:
                m.box(A, B, {"u": "light", "d": "light", "*": paneled((100, 104, 116))})
    for (x0, z0) in ((16, 16), (52, 16), (16, 52), (52, 52)):
        m.box([x0, R, z0], [x0 + 12, R + 16, z0 + 12], paneled((84, 88, 100)))
        m.box([x0 + 3, R + 16, z0 + 3], [x0 + 9, R + 17, z0 + 9], hotwin())
        m.box([x0 + 2, R + 17, z0 + 2], [x0 + 10, R + 18, z0 + 10], "dark") if False else None
    # окна, светящиеся изнутри при работе
    m.box([38, R + 5, 15], [42, R + 11, 16], hotwin())
    m.box([38, R + 5, 64], [42, R + 11, 65], hotwin())
    m.box([15, R + 5, 38], [16, R + 11, 42], hotwin())
    m.box([64, R + 5, 38], [65, R + 11, 42], hotwin())
    banded_column(m, 36, 36, 8, R, 46, [(R + 4, R + 12), (R + 16, R + 20)])
    for (a_, b_) in (((38, R + 6, 28), (42, R + 10, 36)), ((38, R + 6, 44), (42, R + 10, 52)),
                     ((28, R + 6, 38), (36, R + 10, 42)), ((44, R + 6, 38), (52, R + 10, 42))):
        m.box(list(a_), list(b_), "steel")
    oct_y(m, 32, 32, 48, 48, 46, 50, ribs((190, 196, 206)), "light", c=6)
    # паровая магистраль: от головки соленоида вверх, назад и вниз в барабан
    pipe_path(m, [(40, 50, 40), (40, 56, 40), (40, 56, 70), (40, 30, 70)], 6, (150, 156, 166), 8)
    oct_x(m, 10, 64, 8, 30, 64, 77, corrug((150, 156, 168)), "light", c=5)
    for x in (14, 34, 54):
        m.box([x, 2, 66], [x + 6, 8, 76], cast((92, 94, 104)))
    for x in (20, 30, 40, 50):
        m.box([x, 30, 66], [x + 2, 31, 76], "dark") if False else None
    ladder(m, 12, 62, 8, 30, axis="x")
    # слева: три трансформатора
    for (z0, z1, h) in ((6, 22, 24), (26, 42, 30), (46, 62, 20)):
        m.box([3, 2, z0], [13, h, z1], cab("nes", 4))
        m.box([4, h, z0 + 2], [12, h + 6, z1 - 2], coil())
    vent(m, 4, 4, 5, 12, 14, 6, "n")
    # справа: три сосуда хладагента ступенями
    for (z0, z1, h) in ((5, 23, 34), (28, 46, 28), (52, 70, 22)):
        oct_y(m, 65, z0, 77, z1, 2, h, tiles((84, 120, 150)), "light", c=3)
        for y in range(8, h - 4, 10):
            band_sides(m, 65, z0, 77, z1, y, "lbf")
    # спереди: пульт и шкафы
    m.box([20, 2, 3], [58, 10, 14], {"n": console_mat(MM.GL, None), "u": lamps(GREEN), "*": hull((50, 52, 58), 0)})
    m.box([24, 10, 8], [54, 18, 12], cab("n", 4))
    m.box([14, 2, 3], [20, 22, 12], cab("n", 4))
    m.box([58, 2, 3], [64, 22, 12], cab("n", 4))
    dial(m, 15, 14, 19, 18, 3)
    dial(m, 59, 14, 63, 18, 3)
    # детали: люки, патрубки, решётки
    for (z0, z1, h) in ((5, 23, 34), (28, 46, 28), (52, 70, 22)):
        zc = (z0 + z1) // 2
        hatch(m, 77, h // 2, zc, "e", 6)
        nozzle(m, 69, h, zc - 2)
    for (z0, z1, h) in ((6, 22, 24), (26, 42, 30), (46, 62, 20)):
        zc = (z0 + z1) // 2
        m.box([2, 6, zc - 4], [3, h - 6, zc + 4], {"w": "grate", "*": "dark"})
    hatch(m, 10, 19, 70, "w", 6)
    nozzle(m, 20, 30, 68)
    nozzle(m, 44, 30, 68)
    hatch(m, 40, 10, 16, "n", 8)
    return m


# ---------------------------------------------------------------- паротурбинный зал

def tube_box(m, a, b, axis, rgb, ring=0, cap=None):
    """Труба или цилиндрический бак вдоль оси axis: цилиндрическая закраска боков, торцы стальные."""
    cap = cap or hull((98, 102, 112), 0)
    t = lambda ax: tube(rgb, ax, ring)
    if axis == "y":
        mats = {"n": t("v"), "s": t("v"), "e": t("v"), "w": t("v"), "u": cap, "d": cap}
    elif axis == "x":
        mats = {"n": t("h"), "s": t("h"), "u": t("h"), "d": t("h"), "e": cap, "w": cap}
    else:
        mats = {"e": t("h"), "w": t("h"), "u": t("v"), "d": t("v"), "n": cap, "s": cap}
    return m.box(a, b, mats)


def pipe_oct(m, a, b, axis, rgb, cap=None):
    """Цельная круглая труба: восьмигранник вдоль оси axis (три бруса без перекрытия), свет сверху слева: верх светлее,
    низ темнее, боковые стороны между ними; торцы закрыты крышкой (cap)."""
    k = {"x": 0, "y": 1, "z": 2}[axis]
    lo, hi = list(a), list(b)
    sz = [hi[i] - lo[i] for i in range(3)]
    d = min(sz[i] for i in range(3) if i != k)
    c = max(1, d // 4)
    cap = cap or hull(tuple(int(v * 0.8) for v in rgb), 0)
    P = lambda lvl: pipe_mat(rgb, lvl)
    if axis == "z":
        m.box([lo[0], lo[1] + c, lo[2]], [hi[0], hi[1] - c, hi[2]], {"w": P(1.04), "e": P(0.94), "u": P(1.0), "d": P(0.86), "n": cap, "s": cap})
        m.box([lo[0] + c, hi[1] - c, lo[2]], [hi[0] - c, hi[1], hi[2]], {"u": P(1.1), "w": P(1.07), "e": P(1.0), "n": cap, "s": cap})
        m.box([lo[0] + c, lo[1], lo[2]], [hi[0] - c, lo[1] + c, hi[2]], {"d": P(0.82), "w": P(0.97), "e": P(0.9), "n": cap, "s": cap})
    elif axis == "x":
        m.box([lo[0], lo[1] + c, lo[2]], [hi[0], hi[1] - c, hi[2]], {"n": P(1.04), "s": P(0.94), "u": P(1.0), "d": P(0.86), "e": cap, "w": cap})
        m.box([lo[0], hi[1] - c, lo[2] + c], [hi[0], hi[1], hi[2] - c], {"u": P(1.1), "n": P(1.07), "s": P(1.0), "e": cap, "w": cap})
        m.box([lo[0], lo[1], lo[2] + c], [hi[0], lo[1] + c, hi[2] - c], {"d": P(0.82), "n": P(0.97), "s": P(0.9), "e": cap, "w": cap})
    else:
        m.box([lo[0], lo[1], lo[2] + c], [hi[0], hi[1], hi[2] - c], {"w": P(1.05), "e": P(0.92), "n": P(1.0), "s": P(0.95), "u": cap, "d": cap})
        m.box([lo[0] + c, lo[1], hi[2] - c], [hi[0] - c, hi[1], hi[2]], {"s": P(1.03), "w": P(1.06), "e": P(0.95), "u": cap, "d": cap})
        m.box([lo[0] + c, lo[1], lo[2]], [hi[0] - c, hi[1], lo[2] + c], {"n": P(1.0), "w": P(1.0), "e": P(0.76), "u": cap, "d": cap})


def pipe_path(m, pts, d, rgb, ring=0):
    """Цельная труба по ломаной из центров pts (оси параллельны осям координат): круглые прямые звенья и угловые муфты чуть
    толще трубы; звенья встык, швы только у муфт и они совпадают по высоте на всех гранях."""
    h = d // 2
    n = len(pts)
    for i in range(n - 1):
        p, q = pts[i], pts[i + 1]
        k = next(j for j in range(3) if p[j] != q[j])
        a0, a1 = min(p[k], q[k]), max(p[k], q[k])
        lo_c = (i > 0) if p[k] < q[k] else (i < n - 2)
        hi_c = (i < n - 2) if p[k] < q[k] else (i > 0)
        if lo_c:
            a0 += h + 1
        if hi_c:
            a1 -= h + 1
        lo = [p[j] - h for j in range(3)]
        hi = [p[j] + h for j in range(3)]
        lo[k], hi[k] = a0, a1
        pipe_oct(m, lo, hi, "xyz"[k], rgb)
    for c in pts[1:-1]:
        m.box([c[0] - h - 1, c[1] - h - 1, c[2] - h - 1], [c[0] + h + 1, c[1] + h + 1, c[2] + h + 1], hull(tuple(int(v * 0.85) for v in rgb), 0))


def pipe_run(m, a, b, axis, rgb, ring=8, seg=10):
    """Труба из звеньев с выступающими фланцами между ними (объём вместо гладкой поверхности)."""
    lo = {"x": a[0], "y": a[1], "z": a[2]}[axis]
    hi = {"x": b[0], "y": b[1], "z": b[2]}[axis]
    k = {"x": 0, "y": 1, "z": 2}[axis]
    cur = lo
    while cur < hi:
        end = min(hi, cur + seg)
        if hi - end < 3 and end < hi:
            end = hi
        A, B = list(a), list(b)
        A[k], B[k] = cur, end
        tube_box(m, A, B, axis, rgb, ring)
        if end < hi:
            fa, fb = list(a), list(b)
            fa[k], fb[k] = end, min(hi, end + 2)
            for i in range(3):
                if i != k:
                    fa[i] -= 1
                    fb[i] += 1
            m.box(fa, fb, hull((120, 124, 134), 0))
            cur = min(hi, end + 2)
        else:
            cur = end


def barrel_z(m, cx, cy, size, z0, z1, rgb, t=4, c=3, holes=(), hh=6, pat=None):
    """Кожух турбины - полый барабан вдоль z вокруг оси (cx, cy): верхняя и нижняя плиты со скошенными краями, боковые стенки с
    иллюминаторами (holes - отрезки по z; в проёме стекло), по бокам на уровне оси стыковой фланец с рядом болтов."""
    h = size // 2
    sh = (pat or weld)(rgb)
    m.box([cx - h + c, cy + h - t, z0], [cx + h - c, cy + h, z1], {"u": hull(rgb, 8), "*": sh})
    m.box([cx - h + c, cy - h, z0], [cx + h - c, cy - h + t, z1], {"d": hull(rgb, 8), "*": sh})
    w0, w1 = cy - h + t, cy + h - t
    for sx in (-1, 1):
        xo = cx + sx * h
        x0, x1 = (xo, xo + t) if sx < 0 else (xo - t, xo)
        zs = [z0] + [v for hz in holes for v in hz] + [z1]
        for i in range(0, len(zs) - 1, 2):
            if zs[i + 1] > zs[i]:
                m.box([x0, w0, zs[i]], [x1, w1, zs[i + 1]], sh)
        hy1 = min(cy + 3 + hh, w1 - 1)
        for (za, zb) in holes:
            m.box([x0, w0, za], [x1, cy + 3, zb], sh)
            m.box([x0, hy1, za], [x1, w1, zb], sh)
            m.box([x0 if sx < 0 else x1 - 1, cy + 3, za], [x0 + 1 if sx < 0 else x1, hy1, zb], pane((190, 200, 210), 60))
        fx0, fx1 = (xo - 1, xo) if sx < 0 else (xo, xo + 1)
        for z in range(z0 + 2, z1 - 3, 6):
            m.box([fx0, cy - 2, z], [fx1, cy + 2, z + 4], bolts((176, 178, 184)))
    # скосы по углам: небольшие бруски между плитой и стенкой
    for sy in (-1, 1):
        for sx in (-1, 1):
            xa, xb = (cx - h, cx - h + c) if sx < 0 else (cx + h - c, cx + h)
            ya, yb = (cy + h - t, cy + h - c) if sy > 0 else (cy - h + c, cy - h + t)
            if yb > ya:
                m.box([xa, ya, z0], [xb, yb, z1], sh)


def turbine_hall():
    """Паротурбинный зал 3x7x3 в виде турбоагрегата: на стальных фундаментах цилиндрические кожухи высокого (малый), среднего и
    низкого давления (самый крупный) с иллюминаторами, болтовым стыковым фланцем и круглыми выхлопными патрубками сверху;
    между ними красные корпуса подшипников и арочные паропроводы, сзади красный генератор с клеммной коробкой, спереди красный
    регулятор и щиты управления, слева маслобак и деаэратор, справа подогреватели и конденсатор."""
    m = Big("turbine_hall", 3, 7, 3)
    frame(m)
    RED_H = (178, 78, 64)
    cy = 24
    # фундаменты
    m.box([12, 2, 12], [36, 12, 38], cast((84, 88, 100)))
    m.box([10, 2, 42], [38, 10, 64], cast((80, 84, 96)))
    m.box([10, 2, 68], [38, 7, 98], cast((76, 80, 92)))
    # кожухи
    barrel_z(m, 24, cy, 24, 14, 36, (176, 148, 124), t=4, c=3, holes=((17, 25), (27, 35)), hh=8, pat=paneled)
    barrel_z(m, 24, cy, 28, 42, 64, (178, 178, 182), t=4, c=5, holes=((45, 53), (55, 63)), hh=8)
    barrel_z(m, 24, cy, 34, 68, 98, (206, 210, 218), t=4, c=6, holes=((71, 79), (81, 89), (91, 97)), hh=8, pat=ribs)
    # фланцы-стыки и красные подшипники между кожухами
    m.box([14, 16, 36], [34, 32, 42], weld(RED_H)) if False else None
    for (z0, z1) in ((36, 42), (64, 68)):
        m.box([10, 12, z0], [38, 36, z1], paneled(RED_H)) if z0 == 36 else m.box([6, 8, z0], [42, 40, z1], paneled(RED_H))
        m.box([20, 36, z0 + 1], [28, 38, z1 - 1], "dark") if z0 == 36 else None
    # выхлопные патрубки НД сверху
    for (x0, z0) in ((12, 70), (24, 84)):
        oct_y(m, x0, z0, x0 + 12, z0 + 12, 41, 47, ribs((206, 210, 218)), "dark", c=3)
        m.box([x0 + 5, 47, z0 + 1], [x0 + 7, 48, z0 + 11], "light")
        m.box([x0 + 1, 47, z0 + 5], [x0 + 5, 48, z0 + 7], "light")
        m.box([x0 + 7, 47, z0 + 5], [x0 + 11, 48, z0 + 7], "light")
    # торцы кожухов закрыты крышками: передняя у высокого давления и задняя у низкого
    m.box([16, 16, 14], [32, 32, 16], cast((120, 100, 86)))
    m.box([11, 11, 96], [37, 37, 98], cast((150, 154, 164)))
    # перепускная труба с аркой между высоким и средним давлением (пар входит сверху через порт над высоким давлением)
    pipe_path(m, [(24, 36, 34), (24, 44, 34), (24, 44, 56), (24, 38, 56)], 6, (150, 156, 166), 8)
    # слева: маслобак и деаэратор
    oct_y(m, 4, 20, 10, 36, 2, 26, weld((150, 160, 180)), "light", c=2)
    for y in (8, 18):
        band_sides(m, 4, 20, 10, 36, y, "lbf")
    oct_z(m, 3, 9, 2, 16, 44, 60, corrug((130, 150, 170)), "light", c=2)
    nozzle(m, 6, 26, 28)
    hatch(m, 4, 12, 36, "w", 6) if False else None
    # справа: подогреватели
    oct_z(m, 38, 45, 2, 14, 14, 40, tiles((176, 182, 194)), "light", c=2)
    oct_z(m, 38, 46, 2, 18, 42, 64, paneled((196, 200, 210)), "light", c=2)
    nozzle(m, 40, 14, 24, 3, 3)
    # сзади: красный генератор, возбудитель, трансформатор
    oct_z(m, 8, 40, 6, 42, 100, 109, corrug(RED_H), "light", c=7)
    for z in (102, 106):
        m.box([8, 24, z], [9, 26, z + 1], "dark") if False else None
    m.box([16, 42, 102], [32, 46, 108], cab("n", 3))
    m.box([3, 8, 100], [8, 26, 108], coil())
    m.box([14, 8, 109], [34, 28, 110], {"s": grille(), "*": "dark"})
    m.box([40, 2, 100], [46, 22, 109], cab("nes", 3))
    m.box([41, 22, 102], [45, 28, 107], coil())
    # спереди: красный регулятор и щиты управления
    m.box([14, 2, 3], [34, 18, 12], cast(RED_H))
    dial(m, 20, 8, 25, 13, 3)
    m.box([36, 2, 3], [46, 22, 10], cab("n", 4))
    return m


# ---------------------------------------------------------------- градирня

def cooling_tower():
    """Градирня 5x3x3 из двух секций рядом, как на заводах: ржавая стальная рама-основание, поддон, массивные радиаторы-жалюзи
    на длинных сторонах, корпус из профнастила, площадка с перилами и два больших вентилятора в круглых кожухах на секцию,
    лестница в проходе между секциями, белые стояки по торцам над портами подачи и слива воды, шкаф управления спереди."""
    m = Big("cooling_tower", 5, 3, 3)
    frame(m)
    RUST = (104, 80, 66)
    LIGHT = (176, 180, 190)
    # рама-основание из ржавой стали: продольные балки (спереди с проёмом под шкаф), стойки и поперечины
    for (xa, xb) in ((6, 30), (50, 74)):
        m.box([xa, 2, 4], [xb, 6, 8], weld(RUST))
    m.box([6, 2, 40], [74, 6, 44], weld(RUST))
    for x0 in (6, 38, 70):
        m.box([x0, 2, 8], [x0 + 4, 6, 40], weld(RUST))
    for x0 in (22, 54):
        m.box([x0, 2, 8], [x0 + 4, 6, 40], weld(RUST))
    for x0 in (6, 22, 38, 54, 70):
        m.box([x0, 6, 8], [x0 + 4, 8, 40], cast(RUST))
    # поддон
    m.box([6, 8, 6], [74, 14, 42], paneled(LIGHT))
    for x0 in (6, 44):
        x1 = x0 + 30
        # массивные радиаторы на длинных сторонах: рамка и жалюзи толщиной 8
        for (xa, xb) in ((x0 + 1, x0 + 14), (x0 + 16, x0 + 29)):
            for (za, zb, face) in ((3, 11, "n"), (37, 45, "s")):
                m.box([xa, 14, za], [xb, 32, zb], {face: slats((92, 96, 108)), "u": paneled(LIGHT), "d": "dark", "*": hull((100, 104, 114), 0)})
                for px in (xa, xb - 1, (xa + xb) // 2):
                    m.box([px, 14, za - 1 if face == "n" else zb], [px + 1, 32, za if face == "n" else zb + 1], "steel")
        # корпус секции: профнастил с поясом, площадка
        m.box([x0, 14, 11], [x1, 32, 37], corrug(LIGHT))
        m.box([x0 - 1, 32, 5], [x1 + 1, 34, 43], paneled((150, 156, 168)))
        m.box([x0, 34, 6], [x1, 38, 42], corrug((190, 194, 204)))
        m.box([x0 - 1, 38, 5], [x1 + 1, 40, 43], tread((150, 156, 168)))
        # два больших вентилятора в круглых кожухах
        for (z0, z1) in ((6, 24), (24, 42)):
            m.box([x0 + 6, 40, z0 + 1], [x0 + 24, 46, z1 - 1], {"u": fan((214, 218, 226), 5), "*": hull((170, 176, 188), 8)})
        # перила по краю площадки
        for x in range(x0, x1 + 1, 10):
            for z in (6, 41):
                m.box([x - 1 if x > x0 else x, 40, z], [x if x > x0 else x + 1, 44, z + 1], "light")
        m.box([x0, 44, 6], [x1, 45, 7], "light")
        m.box([x0, 44, 41], [x1, 45, 42], "light")
    # лестница в проходе между секциями
    ladder(m, 38, 43, 6, 40, axis="x")
    # белые стояки по торцам над портами подачи и слива воды
    pipe_oct(m, [1, 16, 22], [5, 38, 26], "y", (150, 156, 166))
    pipe_oct(m, [75, 16, 22], [79, 38, 26], "y", (150, 156, 166))
    # шкаф управления спереди между секциями и панель ламп
    m.box([36, 2, 3], [44, 28, 6], cab("n", 4))
    m.box([36, 28, 3], [44, 30, 6], {"n": lamps(AMBER), "u": lamps(GREEN), "*": hull((50, 52, 58), 0)})
    return m


def platform(m, x0, z0, x1, z1, y, w=4):
    """Обходная площадка с решётчатым настилом вокруг корпуса и перилами по внешнему краю."""
    g = {"u": "grate", "*": "dark"}
    m.box([x0 - w, y, z0 - w], [x1 + w, y + 1, z0], g)
    m.box([x0 - w, y, z1], [x1 + w, y + 1, z1 + w], g)
    m.box([x0 - w, y, z0], [x0, y + 1, z1], g)
    m.box([x1, y, z0], [x1 + w, y + 1, z1], g)
    r = "light"
    ax0, ax1, az0, az1 = x0 - w, x1 + w - 1, z0 - w, z1 + w - 1
    for (px, pz) in ((ax0, az0), (ax1, az0), (ax0, az1), (ax1, az1)):
        m.box([px, y + 1, pz], [px + 1, y + 6, pz + 1], r)
    m.box([ax0 + 1, y + 5, az0], [ax1, y + 6, az0 + 1], r)
    m.box([ax0 + 1, y + 5, az1], [ax1, y + 6, az1 + 1], r)
    m.box([ax0, y + 5, az0 + 1], [ax0 + 1, y + 6, az1], r)
    m.box([ax1, y + 5, az0 + 1], [ax1 + 1, y + 6, az1], r)


def blast_furnace():
    """Доменная печь 5x5x6 в виде литейного завода: стальной корпус (горн, заплечики, шахта) с медными поясами охлаждения и тремя
    обходными площадками, воздушное кольцо, колошник с бункером и скиповым подъёмником, газоотвод в пылеуловитель и скруббер,
    два воздухонагревателя, литейный двор с лётками, жёлобом и ковшами, щиты управления."""
    m = Big("blast_furnace", 5, 5, 6)
    frame(m)
    SH = (88, 94, 106)
    oct_y(m, 18, 18, 62, 62, 2, 6, tread((72, 76, 86)), "light", c=8)
    oct_y(m, 18, 18, 62, 62, 6, 28, cast((74, 70, 76)), "light", c=8)
    for y in (10, 15, 20, 25):
        band_sides(m, 26, 26, 54, 54, y, "") if False else None
    oct_y(m, 20, 20, 60, 60, 28, 46, weld(SH), "light", c=8)
    oct_y(m, 24, 24, 56, 56, 46, 74, ribs((100, 106, 118)), "light", c=8)
    oct_y(m, 28, 28, 52, 52, 74, 84, paneled((112, 118, 130)), "light", c=6)
    for y in (31, 35, 39, 43):
        band_sides(m, 20, 20, 60, 60, y, "lrbf", coil())
    for y in (50, 56, 62, 68):
        band_sides(m, 24, 24, 56, 56, y, "lrbf", coil())
    platform(m, 20, 20, 60, 60, 28)
    platform(m, 24, 24, 56, 56, 46)
    platform(m, 28, 28, 52, 52, 74)
    # опоры под обходными площадками
    for (x0, z0) in ((16, 16), (62, 16), (16, 62), (62, 62)):
        m.box([x0, 2, z0], [x0 + 2, 28, z0 + 2], weld((110, 114, 126)))
    for (x0, z0) in ((20, 20), (58, 20), (20, 58), (58, 58)):
        m.box([x0, 29, z0], [x0 + 2, 46, z0 + 2], weld((110, 114, 126)))
    for (x0, z0) in ((24, 24), (54, 24), (24, 54), (54, 54)):
        m.box([x0, 47, z0], [x0 + 2, 74, z0 + 2], weld((110, 114, 126)))
    # воздушное кольцо вокруг горна и воздуховод от воздухонагревателей
    for (a, b) in (((13, 14, 22), (18, 22, 58)), ((62, 14, 22), (67, 22, 58)), ((22, 14, 62), (58, 22, 67)),
                   ((22, 14, 13), (30, 22, 18)), ((50, 14, 13), (58, 22, 18))):
        m.box(list(a), list(b), coil())
    # колошник: бункер с конусом, подъёмник, газоотвод
    m.box([34, 84, 34], [46, 88, 46], corrug((150, 154, 164)))
    oct_y(m, 30, 30, 50, 50, 88, 94, paneled((176, 182, 194)), "light", c=4)
    pipe_path(m, [(50, 91, 40), (68, 91, 40)], 6, (150, 156, 166), 8)
    # литейный двор: лётка, жёлоб, ковши, щиты
    m.box([30, 6, 8], [50, 28, 18], cast((84, 86, 96)))
    m.box([34, 10, 6], [46, 24, 8], {"n": mouth(), "*": "dark"})
    m.box([36, 6, 3], [44, 9, 8], {"u": melt(), "*": "dark"})
    oct_y(m, 17, 4, 29, 16, 2, 12, cast((86, 76, 72)), melt(), c=2)
    oct_y(m, 51, 4, 63, 16, 2, 12, cast((86, 76, 72)), melt(), c=2)
    m.box([3, 2, 4], [16, 22, 12], cab("n", 4))
    m.box([64, 2, 4], [77, 22, 12], cab("n", 4))
    dial(m, 7, 14, 12, 19, 4)
    dial(m, 68, 14, 73, 19, 4)
    # справа: пылеуловитель и скруббер
    oct_y(m, 68, 28, 77, 48, 2, 92, corrug((170, 176, 188)), "light", c=2)
    for y in (14, 30, 46, 62, 78):
        band_sides(m, 68, 28, 77, 48, y, "lbrf")
    oct_y(m, 68, 54, 77, 70, 2, 52, paneled((150, 156, 168)), "light", c=2)
    for y in (12, 28, 42):
        band_sides(m, 68, 54, 77, 70, y, "lbrf")
    # слева: два воздухонагревателя
    oct_y(m, 3, 26, 13, 46, 2, 70, tiles((190, 196, 206)), "light", c=3)
    oct_y(m, 3, 50, 13, 70, 2, 56, tiles((176, 182, 194)), "light", c=3)
    for y in (14, 28, 42, 56):
        band_sides(m, 3, 26, 13, 46, y, "lbf")
    for y in (14, 28, 42):
        band_sides(m, 3, 50, 13, 70, y, "lb")
    # сзади: воздуходувка
    m.box([56, 2, 70], [64, 22, 77], coil())
    m.box([36, 2, 76], [50, 18, 77], cab("s", 3))
    # детали: домы воздухонагревателей, люки, лестницы, патрубки
    oct_y(m, 5, 28, 11, 44, 70, 76, tiles((200, 206, 216)), "light", c=2)
    oct_y(m, 5, 52, 11, 68, 56, 62, tiles((200, 206, 216)), "light", c=2)
    hatch(m, 3, 20, 36, "w", 6)
    hatch(m, 3, 20, 60, "w", 6)
    ladder(m, 5, 47, 2, 60, axis="x")
    hatch(m, 77, 20, 38, "e", 6)
    hatch(m, 77, 50, 38, "e", 6)
    nozzle(m, 71, 92, 36, 2, 4, False)
    nozzle(m, 71, 52, 60)
    for z in (28, 38, 48):
        m.box([14, 22, z], [16, 26, z + 2], "light")
        m.box([62, 22, z], [64, 26, z + 2], "light")
    # газопровод между пылеуловителем и скруббером, воздушные клапаны на колошнике, жёлоба к ковшам
    pipe_oct(m, [70, 8, 48], [74, 12, 54], "z", (150, 156, 166))
    nozzle(m, 38, 94, 31, 1, 3, False)
    nozzle(m, 38, 94, 47, 1, 3, False)
    m.box([29, 6, 8], [30, 8, 14], "dark")
    m.box([50, 6, 8], [51, 8, 14], "dark")
    return m


SKIP = ("fan", "dial", "wiring", "pane", "liquid", "port", "console", "view", "glow", "lamps", "lamp", "mouth", "melt",
        "hotwin", "crop", "panel", "shade")


def grade(m, amp=0.08):
    """Каждой грани подмешивает плавный свет (сверху слева светлее) и растровую градацию: вместо плоской заливки."""
    for bx in m.boxes:
        for f, v in list(bx.mat.items()):
            if callable(v):
                continue
            if isinstance(v, tuple) and v[0] in SKIP:
                continue
            bx.mat[f] = ("shade", (v, amp))


def _finish(name, fn, wiring):
    """Градация граней и красные/синие провода между агрегатами (как у машин обработки)."""
    from .wires import route_wires

    def build():
        m = fn()
        grade(m)
        for sp in wiring:
            try:
                route_wires(m, (m.X, m.Y, m.Z), [sp])
            except ValueError:
                pass
        return m
    build.__name__ = name
    return build


RAW = {"fusion_reactor": fusion_reactor, "turbine_hall": turbine_hall, "cooling_tower": cooling_tower,
       "blast_furnace": blast_furnace}
from .wires import RED, BLUE  # noqa: E402
WIRING = {"fusion_reactor": [(RED, (14, 14, 14), (4, 10, 12)), (RED, (14, 20, 34), (13, 20, 34)), (BLUE, (40, 3, 2), (64, 6, 10))],
          "turbine_hall": [(RED, (40, 3, 2), (20, 8, 8))], "cooling_tower": [(BLUE, (24, 3, 2), (20, 8, 8))],
          "blast_furnace": [(RED, (40, 3, 2), (10, 8, 8))]}
DESIGNS = {k: _finish(k, RAW[k], WIRING[k]) for k in RAW}
