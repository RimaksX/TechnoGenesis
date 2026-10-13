"""Прокладка проводов: ортогональный маршрут по свободным клеткам 1x1x1 между двумя деталями модели. Провода жмутся к
поверхностям и поворачивают редко; концы упираются в детали (соединение не «висит»), клетки занятых деталей не трогаются."""
import heapq

from .model3d import Box

DIRS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
RED = (158, 62, 54)
BLUE = (62, 92, 160)
GRAY = (122, 128, 136)


def _occupied(model, dims):
    X, Y, Z = dims
    occ = set()
    for bx in model.boxes:
        a = [int(round(v)) for v in bx.a]
        b = [int(round(v)) for v in bx.b]
        for x in range(max(0, a[0]), min(X, b[0])):
            for y in range(max(0, a[1]), min(Y, b[1])):
                for z in range(max(0, a[2]), min(Z, b[2])):
                    occ.add((x, y, z))
    return occ


def _snap(occ, dims, cell, radius=9):
    """Свободная клетка, ближайшая к заданной (если сама занята деталью), чтобы провод упирался в эту деталь."""
    if cell not in occ:
        return cell
    X, Y, Z = dims
    best = None
    for r in range(1, radius + 1):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if abs(dx) + abs(dy) + abs(dz) != r:
                        continue
                    n = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
                    if 0 <= n[0] < X and 0 <= n[1] < Y and 0 <= n[2] < Z and n not in occ:
                        return n
    raise ValueError(f"рядом с {cell} нет свободной клетки")


def _route(occ, dims, start, end):
    X, Y, Z = dims
    start, end = _snap(occ, dims, start), _snap(occ, dims, end)

    def hug(c):
        for d in DIRS:
            n = (c[0] + d[0], c[1] + d[1], c[2] + d[2])
            if n in occ:
                return True
        return False

    best = {}
    heap = [(0.0, start, -1)]
    best[(start, -1)] = 0.0
    prev = {}
    while heap:
        cost, cell, di = heapq.heappop(heap)
        if cost > best.get((cell, di), 1e18):
            continue
        if cell == end:
            path = [cell]
            key = (cell, di)
            while key in prev:
                key = prev[key]
                path.append(key[0])
            return path[::-1]
        for ndi, d in enumerate(DIRS):
            n = (cell[0] + d[0], cell[1] + d[1], cell[2] + d[2])
            if not (0 <= n[0] < X and 0 <= n[1] < Y and 0 <= n[2] < Z) or n in occ:
                continue
            step = 1.0 if hug(n) else 2.6
            if di != -1 and ndi != di:
                step += 1.6
            if d[1] != 0:
                step += 0.3
            nc = cost + step
            key = (n, ndi)
            if nc < best.get(key, 1e18):
                best[key] = nc
                prev[key] = (cell, di)
                heapq.heappush(heap, (nc, n, ndi))
    raise ValueError(f"нет пути для провода {start} -> {end}")


def _boxes(path, mat):
    """Клетки пути -> прямые отрезки-коробки; угловая клетка принадлежит предыдущему отрезку."""
    if len(path) == 1:
        c = path[0]
        return [([c[0], c[1], c[2]], [c[0] + 1, c[1] + 1, c[2] + 1])]
    runs, cur, d0 = [], [path[0]], None
    for i in range(1, len(path)):
        d = tuple(path[i][k] - path[i - 1][k] for k in range(3))
        if d0 is None or d == d0:
            cur.append(path[i])
            d0 = d
        else:
            runs.append(cur)
            cur = [path[i]]
            d0 = None
    runs.append(cur)
    out = []
    for r in runs:
        lo = [min(c[k] for c in r) for k in range(3)]
        hi = [max(c[k] for c in r) + 1 for k in range(3)]
        out.append((lo, hi))
    return out


def route_wires(model, dims, wires):
    """wires: список (цвет-rgb, начало-клетка, конец-клетка). Добавляет коробки-провода в модель, каждый следующий провод
    обходит предыдущие."""
    occ = _occupied(model, dims)
    for (rgb, start, end) in wires:
        path = _route(occ, dims, tuple(start), tuple(end))
        for c in path:
            occ.add(c)
        for lo, hi in _boxes(path, rgb):
            model.box(lo, hi, ("panel", (rgb,)))
    return model
