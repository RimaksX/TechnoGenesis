"""Объёмные модели машин Контура. Перед машины - сторона north (z=0).
Базовое моделирование на сетке 16x16x16: все координаты целые, наименьший элемент 1 кубик, 1 пиксель текстуры =
1 кубик. Только прямые кубоиды без поворотов, детали лишь соприкасаются, у каждой грани свой участок атласа,
плоскости не совпадают. Сплошные детали объединены в крупные элементы."""
from .model3d import Model

ORANGE = (236, 140, 40)
GREEN = (80, 210, 110)
ACID = (170, 205, 50)
OLIVE = (124, 118, 52)
WATER = (63, 118, 228)
TEAL = (70, 170, 180)
BROWN = (92, 70, 44)
RED = (200, 56, 52)
BLUE = (60, 100, 214)
AMBER = (240, 170, 60)
FRAME = (66, 68, 74)


def panel(rgb):
    return ("panel", (rgb,))


def glow(rgb):
    return lambda frame: ("glow", (rgb, frame))


def lamp(rgb):
    return lambda frame: ("lamp", (rgb, frame is not None))


def console_mat(lamps=(), screen=None):
    def f(frame):
        ls = [(rgb, frame is not None and (on is None or frame in on)) for rgb, on in lamps]
        return ("console", (ls, screen, frame))
    return f


def view_mat(layers):
    return lambda frame: ("view", (layers, frame))


GL = [(GREEN, (0, 2)), (AMBER, (1, 3))]


def hull(rgb=(96, 100, 110), step=8):
    return ("hull", (rgb, step))


def tube(rgb=(150, 154, 164), axis="v", ring=0):
    return ("tube", (rgb, axis, ring))


def winding(rgb=(184, 108, 66), axis="v"):
    return ("winding", (rgb, axis))


def deck(rgb=(96, 100, 108)):
    return ("deck", (rgb,))


def grille(rgb=(120, 124, 132), axis="h"):
    return ("grille", (rgb, axis))


def lamps(rgb=(90, 220, 120)):
    return lambda frame: ("lamps", (rgb, frame))


def fan(rgb=(196, 190, 176), n=5):
    return lambda frame: ("fan", (rgb, n, frame))


def wind2(rgb=(184, 108, 66), axis="v"):
    return ("wind2", (rgb, axis))


def pipe_mat(rgb, lvl):
    return ("pipe", (rgb, lvl))


def slats(rgb=(110, 114, 124)):
    return ("slats", (rgb,))


def corrug(rgb=(150, 154, 164)):
    return ("corrug", (rgb,))


def tread(rgb=(100, 104, 114)):
    return ("tread", (rgb,))


def cast(rgb=(70, 66, 70)):
    return ("cast", (rgb,))


def tiles(rgb=(190, 196, 206)):
    return ("tiles", (rgb,))


def paneled(rgb=(150, 156, 168)):
    return ("paneled", (rgb,))


def ribs(rgb=(98, 104, 116)):
    return ("ribs", (rgb,))


def melt():
    return lambda frame: ("melt", (frame,))


def hotwin(rgb=(255, 150, 70)):
    return lambda frame: ("hotwin", (rgb, frame))


def pane(rgb=(150, 200, 220), alpha=70):
    return ("pane", (rgb, alpha))


def brick(rgb=(150, 70, 52)):
    return ("brick", (rgb,))


def louver(rgb=(120, 124, 132)):
    return ("louver", (rgb,))


def mouth():
    return lambda frame: ("mouth", (frame,))


def weld(rgb=(112, 114, 118)):
    return ("weld", (rgb,))


def ribbed(rgb=(150, 152, 158)):
    return ("ribbed", (rgb,))


def sieve(rgb=(112, 116, 122)):
    return ("sieve", (rgb,))


def insul(rgb=(196, 192, 182)):
    return ("insul", (rgb,))


def bolts(rgb=(100, 104, 112)):
    return ("bolts", (rgb,))


def cloth(rgb=(150, 160, 172)):
    return ("cloth", (rgb,))


def coil(rgb=(178, 100, 62)):
    return ("coil", (rgb,))


def liquid(rgb):
    return lambda frame: ("liquid", (rgb, frame))


def dial(m, x0, y0, x1, y1, z, needle=(196, 52, 48)):
    """Круглый манометр со стрелкой на передней стенке z (выступает на 1)."""
    m.box([x0, y0, z - 1], [x1, y1, z], {"n": ("dial", (needle,)), "*": "dark"})


# ---------------------------------------------------------------- рама и общие части

def base_frame(m, port, fr, socket=True):
    """Основание-рама: четыре балки по периметру, крестовина и нижний разъём 6x6 в центре (как верхний и боковые)."""
    m.box([0, 0, 0], [16, 2, 2], fr)
    m.box([0, 0, 14], [16, 2, 16], fr)
    m.box([0, 0, 2], [2, 2, 14], fr)
    m.box([14, 0, 2], [16, 2, 14], fr)
    m.box([7, 0, 2], [9, 2, 5], fr)                                          # крестовина
    m.box([7, 0, 11], [9, 2, 14], fr)
    m.box([2, 0, 7], [5, 2, 9], fr)
    m.box([11, 0, 7], [14, 2, 9], fr)
    if socket:
        m.box([5, 0, 5], [11, 2, 11], {"d": port("light"), "*": "light"})    # нижний разъём
    else:
        m.box([5, 0, 5], [11, 2, 11], {"d": "grate", "*": "dark"})           # водозабор вместо разъёма


def frame(m, top_y=14, top_port=True, energy=False, bottom_port=True, front=True, trays=False, top_rails=True):
    """Тёмная рама по рёбрам блока и пять одинаковых разъёмов 6x6: лево, право, зад (патрубки до грани блока),
    верх (стойка до верхней грани, садится на верх агрегата), низ (гнездо в основании)."""
    port = lambda base: (("eport" if energy else "port"), (base,))
    fr = "casing"
    base_frame(m, port, fr, bottom_port)                                     # основание: рама, крестовина, гнездо
    for (x, z) in ((0, 0), (14, 0), (0, 14), (14, 14)):                      # стойки
        m.box([x, 2, z], [x + 2, 14, z + 2], fr)
    if top_rails:
        m.box([0, 14, 0], [16, 16, 2], fr)                                   # верхние рёбра
        m.box([0, 14, 14], [16, 16, 16], fr)
        m.box([0, 14, 2], [2, 16, 14], fr)
        m.box([14, 14, 2], [16, 16, 14], fr)
    if top_port:
        m.box([5, top_y, 5], [11, 16, 11], {"u": port("light"), "*": "light"})    # верхний разъём
    m.box([14, 5, 5], [16, 11, 11], {"e": port("light"), "*": "light"})      # правый
    m.box([0, 5, 5], [2, 11, 11], {"w": port("light"), "*": "light"})        # левый
    m.box([5, 5, 14], [11, 11, 16], {"s": port("light"), "*": "light"})      # задний
    if front:
        m.box([5, 5, 0], [11, 11, 2], {"n": port("light"), "*": "light"})    # передний, сидит на панели индикаторов
        lamp_panel(m)
    if trays:
        cable_trays(m)


def cable_trays(m):
    """Кабельные лотки с красным и синим кабелем по задней и боковым стенкам под верхними рёбрами."""
    red, blue = panel((158, 62, 54)), panel((62, 92, 160))
    for (a, b) in (((2, 11, 14), (14, 12, 15)), ((0, 11, 2), (1, 12, 14)), ((15, 11, 2), (16, 12, 14))):
        m.box(list(a), list(b), "dark")
        m.box([a[0], a[1] + 1, a[2]], [b[0], b[1] + 1, b[2]], red)
        m.box([a[0], a[1] + 2, a[2]], [b[0], b[1] + 2, b[2]], blue)


def cab(faces="n", n=3, rgb=(58, 60, 64)):
    """Деталь-шкаф: на указанных гранях плоский рисунок проводки, остальное тёмное."""
    d = {f: ("wiring", (rgb, n)) for f in faces}
    d["*"] = "dark"
    return d


SMALL_WIRING = {                 # узел-приёмник (клетка внутри двигателя, шины и т.п.) и какие гнёзда у машины есть
    "carbon_capacitor": ((4, 15, 4), "RLBFTD"),
    "thermal_generator": ((8, 12, 8), "RLBFTD"),
    "water_pump": ((8, 11, 8), "RLBFT"),
    "wind_rotor": ((8, 11, 9), "RLBTD"),
    "miner": ((8, 11, 8), "RLBTD"),
    "solar_panel": ((8, 10, 8), "RLBFD"),
    "solar_panel_advanced": ((8, 6, 8), "RLBFD"),
}


def wire_small(m, name):
    """Логичная проводка одноблочной машины: красный провод от каждого гнезда к узлу питания (двигателю, шине, инвертору),
    синий - от панели индикаторов к тому же узлу."""
    from .wires import route_wires, RED, BLUE
    hub, sockets = SMALL_WIRING[name]
    src = {"R": (1, 11, 8), "L": (14, 11, 8), "B": (8, 11, 15), "F": (8, 11, 1), "T": (8, 13, 8), "D": (8, 2, 8)}
    specs = []
    if "F" in sockets or name == "miner":
        specs.append((BLUE, (8, 3, 2), hub))
    for k in sockets:
        specs.append((RED, src[k], hub))
    route_wires(m, (16, 16, 16), specs)


def machine_frame():
    """Рама механизма: пустой каркас блока - нижние и верхние рёбра и четыре стойки, без начинки и гнёзд."""
    m = Model("machine_frame")
    fr = "casing"
    for y0 in (0, 14):
        m.box([0, y0, 0], [16, y0 + 2, 2], fr)
        m.box([0, y0, 14], [16, y0 + 2, 16], fr)
        m.box([0, y0, 2], [2, y0 + 2, 14], fr)
        m.box([14, y0, 2], [16, y0 + 2, 14], fr)
    for (x, z) in ((0, 0), (14, 0), (0, 14), (14, 14)):
        m.box([x, 2, z], [x + 2, 14, z + 2], fr)
    return m


def lamp_panel(m):
    """Панель индикаторов под передним гнездом: три лампы, без экрана."""
    m.box([4, 2, 1], [12, 5, 2], {"n": console_mat(GL, None), "*": "dark"})


def pipe_e(m, x0, y0=6, y1=10, z0=6, z1=10, mat="steel"):
    m.box([x0, y0, z0], [14, y1, z1], mat)


def pipe_w(m, x1, y0=6, y1=10, z0=6, z1=10, mat="steel"):
    m.box([2, y0, z0], [x1, y1, z1], mat)


def pipe_s(m, z0, x0=6, x1=10, y0=6, y1=10, mat="steel"):
    m.box([x0, y0, z0], [x1, y1, 14], mat)


def pult(m, *args, **kwargs):
    """Прежний пульт с экраном убран: панель индикаторов и переднее гнездо делает frame()."""


def win(m, x0, y0, x1, y1, zs, layers, bezel="dark"):
    """Окно в рамке: стекло вровень со стенкой zs (выступает на 1), вокруг утопленная на 1 рамка толщиной 2."""
    m.box([x0, y0, zs - 1], [x1, y1, zs], {"n": view_mat(layers), "*": "dark"})
    m.box([x0 - 1, y1, zs - 2], [x1 + 1, y1 + 1, zs], bezel)
    m.box([x0 - 1, y0 - 1, zs - 2], [x1 + 1, y0, zs], bezel)
    m.box([x0 - 1, y0, zs - 2], [x0, y1, zs], bezel)
    m.box([x1, y0, zs - 2], [x1 + 1, y1, zs], bezel)


def ring_y(m, x0, z0, x1, z1, y0, mat, gap=None):
    """Бандаж высотой 1 вокруг вертикального корпуса (выступ 1). gap=(xa,xb) - проём спереди; 'none' - без передней планки."""
    y1 = y0 + 1
    m.box([x0 - 1, y0, z1], [x1 + 1, y1, z1 + 1], mat)
    m.box([x0 - 1, y0, z0], [x0, y1, z1], mat)
    m.box([x1, y0, z0], [x1 + 1, y1, z1], mat)
    if gap == "none":
        return
    if gap is None:
        m.box([x0 - 1, y0, z0 - 1], [x1 + 1, y1, z0], mat)
    else:
        m.box([x0 - 1, y0, z0 - 1], [gap[0], y1, z0], mat)
        m.box([gap[1], y0, z0 - 1], [x1 + 1, y1, z0], mat)


# ---------------------------------------------------------------- машины

def carbon_capacitor(level=0):
    m = Model("carbon_capacitor")
    frame(m, 14, energy=True)
    for (x, z) in ((3, 3), (9, 3), (3, 9), (9, 9)):                        # ячейки
        m.box([x, 2, z], [x + 4, 13, z + 4], cab("nsew", 3))
    m.box([7, 2, 3], [9, 13, 13], "steel")                                 # сердечник
    m.box([3, 13, 3], [13, 14, 13], "steel")                               # шина-палуба
    for (x, z) in ((3, 3), (11, 3), (3, 11), (11, 11)):                    # клеммы
        m.box([x, 14, z], [x + 2, 16, z + 2], "copper")
    m.box([5, 14, 3], [11, 15, 5], "copper")                               # шины между клеммами
    m.box([5, 14, 11], [11, 15, 13], "copper")
    m.box([2, 11, 2], [14, 14, 3], {"n": ("meter", (level,)), "*": "dark"})   # шкала заряда над передним гнездом
    pipe_e(m, 13)
    pipe_w(m, 3)
    pipe_s(m, 13)
    wire_small(m, "carbon_capacitor")
    return m










# ---------------------------------------------------------------- энергетика

SOLAR_A = (14, 21, 48)                      # почти чёрный тёмно-синий с лёгкой градацией
SOLAR_B = (11, 17, 40)


def cells(cell, line=(120, 140, 190), step=4, sides=True, flat=False):
    return ("cells", (cell, line, step, sides, flat))


def solar_panel():
    m = Model("solar_panel")
    frame(m, 14, top_port=False, energy=True, top_rails=False)
    m.box([3, 2, 3], [13, 8, 13], cab("nsew", 4))                          # инвертор
    m.box([4, 8, 4], [12, 12, 12], coil())                                 # трансформатор
    m.box([6, 12, 6], [10, 14, 10], "light")                               # стойка панели
    m.box([0, 14, 0], [16, 16, 16], {"u": cells(SOLAR_A, (27, 39, 82), 8, False, False), "*": "steel"})   # панель на всю крышу
    pult(m, 4, 12, 2, 5, 1, 3, screen=None)
    pipe_e(m, 13)
    pipe_w(m, 3)
    pipe_s(m, 13)
    wire_small(m, "solar_panel")
    return m


def solar_panel_advanced():
    m = Model("solar_panel_advanced")
    port = lambda base: ("eport", (base,))
    fr = "casing"
    base_frame(m, port, fr)
    for (x, z) in ((0, 0), (14, 0), (0, 14), (14, 14)):
        m.box([x, 2, z], [x + 2, 11, z + 2], fr)
    m.box([0, 11, 0], [16, 12, 2], fr)
    m.box([0, 11, 14], [16, 12, 16], fr)
    m.box([0, 11, 2], [2, 12, 14], fr)
    m.box([14, 11, 2], [16, 12, 14], fr)
    m.box([14, 5, 5], [16, 11, 11], {"e": port("light"), "*": "light"})
    m.box([0, 5, 5], [2, 11, 11], {"w": port("light"), "*": "light"})
    m.box([5, 5, 14], [11, 11, 16], {"s": port("light"), "*": "light"})
    m.box([5, 5, 0], [11, 11, 2], {"n": port("light"), "*": "light"})      # переднее гнездо на панели индикаторов
    lamp_panel(m)
    m.box([3, 2, 3], [13, 11, 13], cab("nsew", 4))                         # инвертор
    m.box([2, 12, 2], [14, 15, 14], "steel")                               # несущая плита панели
    m.box([0, 12, 0], [16, 15, 2], "light")                                # обод плиты
    m.box([0, 12, 14], [16, 15, 16], "light")
    m.box([0, 12, 2], [2, 15, 14], "light")
    m.box([14, 12, 2], [16, 15, 14], "light")
    m.box([0, 15, 0], [16, 16, 16], {"u": cells(SOLAR_B, (23, 34, 74), 8, False, False), "*": "light"})   # элементы
    pult(m, 4, 12, 2, 5, 1, 3, screen=None)
    wire_small(m, "solar_panel_advanced")
    return m


def wind_rotor(blades=False):
    """Корпус ротора без лопастей (они вращаются отдельной моделью); blades=True - вместе с лопастями для предмета."""
    m = Model("wind_rotor")
    frame(m, 13, energy=True, front=False)
    m.box([4, 2, 5], [12, 9, 13], cab("nsew", 3))                          # редуктор и щит управления
    m.box([5, 9, 6], [11, 13, 12], coil())                                 # генератор
    m.box([7, 7, 3], [9, 9, 5], "light")                                   # вал
    m.box([6, 6, 1], [10, 10, 3], "dark")                                  # ступица
    m.box([7, 7, 0], [9, 9, 1], "light")                                   # обтекатель
    m.box([5, 2, 4], [11, 5, 5], {"n": console_mat(GL, None), "*": "dark"})   # индикаторы
    pipe_e(m, 12)
    pipe_w(m, 4)
    pipe_s(m, 13)
    if blades:
        add_blades(m)
    wire_small(m, "wind_rotor")
    return m


def add_blades(m):
    """Четыре одинаковые лопасти крестом вокруг ступицы (центр 8,8): ножка и лопасть с наклоном 22.5 градуса.
    Наклоны согласованы, поэтому при повороте на 90 градусов лопасти совпадают друг с другом."""
    spec = (("y", 22.5, [7, 10, 1], [9, 12, 2], [6, 12, 1], [10, 13, 2], [8, 12.5, 1.5]),
            ("x", -22.5, [4, 7, 1], [6, 9, 2], [3, 6, 1], [4, 10, 2], [3.5, 8, 1.5]),
            ("y", -22.5, [7, 4, 1], [9, 6, 2], [6, 3, 1], [10, 4, 2], [8, 3.5, 1.5]),
            ("x", 22.5, [10, 7, 1], [12, 9, 2], [12, 6, 1], [13, 10, 2], [12.5, 8, 1.5]))
    for axis, angle, sa, sb, pa, pb, origin in spec:
        m.box(sa, sb, "steel")
        m.box(pa, pb, "light", rot={"origin": origin, "axis": axis, "angle": angle})


def wind_rotor_blades():
    m = Model("wind_rotor_blades")
    add_blades(m)
    return m


def wind_rotor_item():
    m = wind_rotor(blades=True)
    m.id = "wind_rotor_item"
    return m


def water_pump():
    """Водяной насос: корпус с бандажами, муфта и мотор сверху, снизу решётка водозабора, синие трубы."""
    m = Model("water_pump")
    frame(m, 14, bottom_port=False)
    BLUE_PIPE = panel((76, 124, 156))
    m.box([4, 2, 4], [12, 9, 12], weld((92, 112, 134)))                    # корпус насоса
    ring_y(m, 4, 4, 12, 12, 3, "dark")                                     # нижний бандаж
    ring_y(m, 4, 4, 12, 12, 8, "dark")                                     # верхний бандаж
    m.box([6, 9, 6], [10, 11, 10], "light")                                # муфта
    m.box([5, 11, 5], [11, 12, 11], "dark")                                # электродвигатель
    m.box([4, 12, 4], [12, 13, 12], coil())
    m.box([5, 13, 5], [11, 14, 11], "dark")
    pipe_e(m, 12, 6, 8, 6, 10, BLUE_PIPE)
    pipe_w(m, 4, 6, 8, 6, 10, BLUE_PIPE)
    pipe_s(m, 12, 6, 10, 6, 8, BLUE_PIPE)
    wire_small(m, "water_pump")
    return m


def miner():
    m = Model("miner")
    frame(m, 14, front=False)
    lamp_panel(m)
    m.box([2, 2, 3], [14, 9, 13], {"n": ("wiring", ((104, 108, 116), 4)), "*": "steel"})   # шкаф привода и управления
    m.box([4, 9, 5], [12, 14, 11], coil())                                 # блок подъёмного двигателя
    m.box([3, 9, 4], [4, 12, 12], "dark")                                  # рёбра охлаждения
    m.box([12, 9, 4], [13, 12, 12], "dark")
    m.box([6, 6, 2], [10, 8, 3], {"n": glow(AMBER), "*": "dark"})          # индикатор бура над пультом
    m.box([5, 6, 13], [11, 9, 14], "grate")                                # вентиляция сзади
    pult(m, 4, 12, 2, 5, 1, 3, screen=AMBER)
    wire_small(m, "miner")
    return m


# ---------------------------------------------------------------- подвижные части шахтёра (рисуются рендерером)

def miner_beam():
    m = Model("miner_beam")
    m.box([0, 0, 5], [16, 3, 11], "steel")                                 # балка вдоль X
    m.box([0, 3, 4], [16, 5, 12], "dark")                                  # верхняя полка
    m.box([0, 5, 6], [16, 6, 10], "copper")                                # токоведущая шина
    return m


def miner_truck():
    """Тележка на рельсе: две колёсные пары по обе стороны балки, борта обнимают направляющую (верх рельса на высоте 4)."""
    m = Model("miner_truck")
    for z0, z1, za, zb in ((1, 5, 1, 4), (11, 15, 12, 15)):
        m.box([3, 4, z0], [13, 7, z1], "dark")                             # нижний корпус тележки, вплотную к балке
        m.box([3, 7, za], [13, 10, zb], "steel")                           # верхняя часть вровень с полкой балки
        m.box([3, 0, za], [4, 4, zb], "light")                             # боковые щёки обнимают рельс
        m.box([12, 0, za], [13, 4, zb], "light")
    return m


def miner_carriage():
    m = Model("miner_carriage")
    m.box([2, 12, 2], [14, 16, 14], "dark")                                # каретка под балкой
    m.box([1, 13, 4], [2, 15, 12], "light")                                # ролики
    m.box([14, 13, 4], [15, 15, 12], "light")
    m.box([5, 12, 1], [11, 15, 2], "copper")                               # лицевая планка каретки
    return m


def miner_shaft():
    m = Model("miner_shaft")
    m.box([6, 0, 6], [10, 1, 10], "steel")                                 # звено вала с двумя муфтами, без пересечений
    m.box([5, 1, 5], [11, 2, 11], "light")
    m.box([6, 2, 6], [10, 8, 10], "steel")
    m.box([5, 8, 5], [11, 9, 11], "light")
    m.box([6, 9, 6], [10, 16, 10], "steel")
    return m


def miner_head():
    m = Model("miner_head")
    m.box([6, 5, 6], [10, 6, 10], "dark")                                  # патрон
    m.box([4, 6, 4], [12, 7, 12], "steel")                                 # корпус головки: низ, пояс, верх
    m.box([3, 7, 3], [13, 9, 13], "dark")
    m.box([4, 9, 4], [12, 10, 12], "steel")
    return m


def _tip(name, ramp, point):
    """Бур: ступенчатый конус из квадратов, каждый второй повёрнут на 45 градусов. Вращается целиком, поэтому на ходу
    выглядит винтом. Высота 5, от острия вверх; сверху стыкуется с патроном головки."""
    m = Model(name)
    dark, mid, base, light = ramp
    r45 = lambda y: {"origin": [8, y, 8], "axis": "y", "angle": 45}
    m.box([7, 0, 7], [9, 1, 9], ("panel", (point,)))                       # остриё
    m.box([6, 1, 6], [10, 2, 10], ("panel", (light,)), rot=r45(1.5))
    m.box([5, 2, 5], [11, 3, 11], ("panel", (base,)))
    m.box([5, 3, 5], [11, 4, 11], ("panel", (mid,)), rot=r45(3.5))
    m.box([4, 4, 4], [12, 5, 12], ("panel", (dark,)))                      # плечо у основания
    return m


def miner_tip_iron():
    return _tip("miner_tip_iron", [(52, 54, 62), (96, 98, 108), (146, 148, 158), (192, 194, 204)], (236, 238, 246))


def miner_tip_steel():
    return _tip("miner_tip_steel", [(26, 36, 62), (52, 72, 112), (86, 112, 164), (130, 158, 208)], (224, 236, 255))


def miner_tip_carbide():
    return _tip("miner_tip_carbide", [(24, 22, 38), (50, 44, 74), (84, 74, 120), (132, 118, 174)], (244, 236, 255))


def thermal_generator():
    """Тепловой генератор: теплообменный сосуд с двумя горелками внизу, медные рёбра и паросборник."""
    m = Model("thermal_generator")
    frame(m, 14, energy=True)
    m.box([3, 2, 3], [13, 10, 13], {"n": ("pipework", ((122, 116, 110), (180, 174, 164))), "*": weld((122, 116, 110))})   # теплообменный сосуд
    m.box([3, 3, 2], [5, 5, 3], {"n": glow(ORANGE), "*": "dark"})          # горелки подвода тепла
    m.box([11, 3, 2], [13, 5, 3], {"n": glow(ORANGE), "*": "dark"})
    m.box([4, 10, 4], [12, 11, 12], ribbed((176, 100, 62)))                # рёбра
    m.box([5, 11, 5], [11, 14, 11], "light")                               # паросборник
    pipe_e(m, 13)
    pipe_w(m, 3)
    pipe_s(m, 13)
    wire_small(m, "thermal_generator")
    return m


# ---------------------------------------------------------------- ступень x5

SOLV = (214, 164, 66)         # растворитель: янтарный
SOLV_DEEP = (150, 110, 44)








# ---------------------------------------------------------------- ступень x8: давление

SLAG = (78, 76, 84)
STEAM = (222, 232, 238)






# ---------------------------------------------------------------- ступень x12: плазма

PLASMA = (180, 140, 255)
MELT = (255, 150, 60)








ALL = { "carbon_capacitor": carbon_capacitor,
    "wind_rotor": wind_rotor, "water_pump": water_pump, "miner": miner, "thermal_generator": thermal_generator,
    "solar_panel": solar_panel, "solar_panel_advanced": solar_panel_advanced,
}
EXTRA = {"machine_frame": machine_frame, "wind_rotor_blades": wind_rotor_blades, "wind_rotor_item": wind_rotor_item, "miner_beam": miner_beam,
         "miner_truck": miner_truck, "miner_carriage": miner_carriage, "miner_shaft": miner_shaft,
         "miner_head": miner_head, "miner_tip_iron": miner_tip_iron, "miner_tip_steel": miner_tip_steel,
         "miner_tip_carbide": miner_tip_carbide}
ANIMATED = ["jaw_crusher", "washing_drum", "magnetic_separator", "settling_tank", "solid_fuel_generator",
            "tailings_mill", "acid_plant", "leaching_reactor", "filter_press", "precipitation_reactor",
            "acid_regeneration_column", "extractor", "electrolyzer", "solvent_regenerator", "attritor", "steam_generator",
            "autoclave", "plasma_generator", "plasma_furnace", "vacuum_caster", "water_splitter", "hydrogen_generator", "alloy_furnace", "thermal_generator",
            "steam_turbine", "water_pump", "miner"]
