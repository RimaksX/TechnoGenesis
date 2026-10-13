"""Заполнение пустот модели вспомогательным оборудованием: щит питания, насосные блоки, баки, радиаторы, ящики. Всё ставится на
пол у стен с зазором в одну клетку для проводов; зоны перед гнёздами остаются свободными."""
import numpy as np


def occupancy(model, dims):
    X, Y, Z = dims
    occ = np.zeros((X, Y, Z), dtype=np.int32)
    for bx in model.boxes:
        a = [int(round(v)) for v in bx.a]
        b = [int(round(v)) for v in bx.b]
        occ[max(0, a[0]):min(X, b[0]), max(0, a[1]):min(Y, b[1]), max(0, a[2]):min(Z, b[2])] = 1
    return occ


class Grid:
    def __init__(self, occ):
        self.occ = occ.copy()
        self._integral()

    def _integral(self):
        self.I = np.pad(self.occ, ((1, 0), (1, 0), (1, 0))).cumsum(0).cumsum(1).cumsum(2)

    def free(self, a, b):
        X, Y, Z = self.occ.shape
        if min(a) < 0 or b[0] > X or b[1] > Y or b[2] > Z:
            return False
        I = self.I
        s = (I[b[0], b[1], b[2]] - I[a[0], b[1], b[2]] - I[b[0], a[1], b[2]] - I[b[0], b[1], a[2]]
             + I[a[0], a[1], b[2]] + I[a[0], b[1], a[2]] + I[b[0], a[1], a[2]] - I[a[0], a[1], a[2]])
        return s == 0

    def mark(self, a, b):
        self.occ[a[0]:b[0], a[1]:b[1], a[2]:b[2]] = 1
        self._integral()


# ---------------------------------------------------------------- типы узлов: (размер, построитель)

def _cabinet(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 5, y + 8, z + 4], mats["cab"])
    m.box([x + 1, y + 8, z + 1], [x + 4, y + 9, z + 3], mats["vent"])
    return (x + 2, y + 4, z + 2)


def _tank(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 6, y + 8, z + 6], mats["tank"](acc))
    m.box([x + 1, y + 8, z + 1], [x + 5, y + 9, z + 5], "dark")
    m.box([x + 2, y + 9, z + 2], [x + 4, y + 10, z + 4], "light")
    return (x + 3, y + 4, z + 3)


def _pump(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 8, y + 1, z + 5], "dark")
    m.box([x, y + 1, z + 1], [x + 4, y + 4, z + 4], mats["coil"])
    m.box([x + 4, y + 1, z + 1], [x + 7, y + 3, z + 4], "steel")
    m.box([x + 7, y + 1, z + 2], [x + 8, y + 3, z + 3], "light")
    return (x + 2, y + 2, z + 2)


def _radiator(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 3, y + 8, z + 7], mats["ribbed"])
    m.box([x, y + 8, z], [x + 3, y + 9, z + 7], "dark")
    return (x + 1, y + 4, z + 3)


def _drums(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 3, y + 5, z + 4], "steel")
    m.box([x + 4, y, z], [x + 7, y + 4, z + 4], "dark")
    m.box([x, y + 5, z + 1], [x + 3, y + 6, z + 3], "light")
    return (x + 1, y + 2, z + 2)


def _crates(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 5, y + 3, z + 5], "steel")
    m.box([x + 1, y + 3, z + 1], [x + 4, y + 5, z + 4], "dark")
    return (x + 2, y + 1, z + 2)


def _cabinet_small(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 4, y + 7, z + 3], mats["cab"])
    m.box([x, y + 7, z], [x + 4, y + 8, z + 3], "dark")
    return (x + 2, y + 3, z + 1)


def _barrel(m, x, y, z, acc, mats):
    m.box([x, y, z], [x + 3, y + 4, z + 3], mats["tank"](acc))
    m.box([x, y + 4, z], [x + 3, y + 5, z + 3], "dark")
    return (x + 1, y + 2, z + 1)


UNITS = [("cabinet", (5, 9, 4), _cabinet), ("pump", (8, 4, 5), _pump), ("tank", (6, 10, 6), _tank),
         ("radiator", (3, 9, 7), _radiator), ("drums", (7, 6, 4), _drums), ("crates", (5, 5, 5), _crates),
         ("cabinet", (4, 8, 3), _cabinet_small), ("pump", (8, 4, 5), _pump), ("barrel", (3, 5, 3), _barrel),
         ("barrel", (3, 5, 3), _barrel), ("crates", (5, 5, 5), _crates)]


def fill_floor(model, dims, xm, accent, mats, reserve, floor=2, maxunits=10, target=0.7, grid=None):
    """Расставляет узлы на полу. Возвращает список (имя, центральная клетка). Первый узел всегда щит питания (cabinet)."""
    X, Y, Z = dims
    if grid is None:
        grid = Grid(occupancy(model, dims))
    for (a, b) in reserve:
        grid.occ[a[0]:b[0], a[1]:b[1], a[2]:b[2]] = 1
    grid._integral()
    placed = []
    inner = (X - 4) * (Z - 4)

    def floor_fill():
        return float(grid.occ[2:X - 2, floor, 2:Z - 2].sum()) / inner

    cands = []
    for x in range(2, X - 2):
        for z in range(2, Z - 2):
            wall = min(x - 2, z - 2, X - 2 - x, Z - 2 - z)
            cands.append((wall, z, x))
    cands.sort()
    order = list(UNITS)
    idx = 0
    while len(placed) < maxunits and floor_fill() < target:
        name, (sx, sy, sz), build = order[idx % len(order)]
        idx += 1
        if idx > len(order) * 4:
            break
        done = False
        for (_, z, x) in cands:
            a = (x - 1, floor, z - 1)
            b = (x + sx + 1, floor + sy, z + sz + 1)
            if x + sx > X - 2 or z + sz > Z - 2:
                continue
            if grid.free(a, b):
                c = build(model, x, floor, z, accent, mats)
                grid.mark((x, floor, z), (x + sx, floor + sy, z + sz))
                placed.append((name, c))
                done = True
                break
    return placed


def add_decks(model, dims, grid, level_y, mat):
    """Решётчатый настил на уровне пояса между слоями: плитки 4x4 там, где свободно, цепляются к поясу и друг к другу."""
    X, Y, Z = dims
    placed = []
    for x in range(2, X - 2, 4):
        for z in range(2, Z - 2, 4):
            x1, z1 = min(x + 4, X - 2), min(z + 4, Z - 2)
            a, b = (x, level_y - 1, z), (x1, level_y + 1, z1)
            if grid.free(a, b):
                model.box(list(a), list(b), mat)
                grid.mark(a, b)
                placed.append((a, b))
    return placed
