"""Спрайты интерфейса машин (textures/gui/sprites): фон, слоты, шкалы, стрелка, пламя, вкладки, ячейки."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/gui/sprites")
SCR = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad")
OUT.mkdir(parents=True, exist_ok=True)

OUTLINE = (18, 19, 23)
HI = (255, 255, 255)
HI2 = (228, 230, 236)
FACE = (198, 200, 206)
SH2 = (150, 153, 162)
SH = (88, 91, 100)
DISP = (30, 32, 37)
DISP_HI = (62, 65, 74)


def img(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def px(im, x, y, c, a=255):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), (*c[:3], a))


def rect(im, x0, y0, x1, y1, c, a=255):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(im, x, y, c, a)


def save(im, name, nine=None):
    im.save(OUT / f"{name}.png")
    meta = OUT / f"{name}.png.mcmeta"
    if nine:
        meta.write_text(json.dumps({"gui": {"scaling": {"type": "nine_slice", "width": im.width, "height": im.height,
                                                          "border": nine}}}, indent=2) + "\n")
    elif meta.exists():
        meta.unlink()


# ---------------------------------------------------------------- фон окна (девятипатч 24x24, граница 4)

def background():
    im = img(24, 24)
    rect(im, 0, 0, 23, 23, FACE)
    for i in range(24):
        px(im, i, 0, OUTLINE); px(im, i, 23, OUTLINE); px(im, 0, i, OUTLINE); px(im, 23, i, OUTLINE)
    for (x, y) in ((0, 0), (23, 0), (0, 23), (23, 23)):          # скруглённые углы
        px(im, x, y, (0, 0, 0), 0)
    for (x, y) in ((1, 1), (22, 1), (1, 22), (22, 22)):
        px(im, x, y, OUTLINE)
    for i in range(2, 22):
        px(im, i, 1, HI); px(im, 1, i, HI)                        # светлая фаска сверху/слева
        px(im, i, 22, SH); px(im, 22, i, SH)                      # тень снизу/справа
    for i in range(3, 21):
        px(im, i, 2, HI2); px(im, 2, i, HI2)
        px(im, i, 21, SH2); px(im, 21, i, SH2)
    px(im, 22, 1, SH2); px(im, 1, 22, SH2)
    save(im, "background", 4)


# ---------------------------------------------------------------- утопленные области

def well():                      # рабочая область: светлое углубление, девятипатч 12x12, граница 2
    im = img(12, 12)
    rect(im, 0, 0, 11, 11, (176, 178, 186))
    for i in range(12):
        px(im, i, 0, SH); px(im, 0, i, SH)
        px(im, i, 11, HI); px(im, 11, i, HI)
    for i in range(1, 11):
        px(im, i, 1, SH2); px(im, 1, i, SH2)
    px(im, 0, 11, FACE); px(im, 11, 0, FACE)
    save(im, "well", 2)


def display():                   # тёмный экран для состояния и шкал, девятипатч 12x12, граница 2
    im = img(12, 12)
    rect(im, 0, 0, 11, 11, DISP)
    for i in range(12):
        px(im, i, 0, OUTLINE); px(im, 0, i, OUTLINE)
        px(im, i, 11, HI2); px(im, 11, i, HI2)
    for i in range(1, 11):
        px(im, i, 1, (20, 21, 25)); px(im, 1, i, (20, 21, 25))
        px(im, i, 10, DISP_HI); px(im, 10, i, DISP_HI)
    px(im, 0, 11, SH2); px(im, 11, 0, SH2)
    save(im, "display", 2)


def slot():
    im = img(18, 18)
    rect(im, 0, 0, 17, 17, (139, 139, 139))
    for i in range(18):
        px(im, i, 0, (55, 55, 55)); px(im, 0, i, (55, 55, 55))
        px(im, i, 17, HI); px(im, 17, i, HI)
    px(im, 0, 17, FACE); px(im, 17, 0, FACE)
    for i in range(1, 17):
        px(im, i, 1, (96, 96, 96)); px(im, 1, i, (96, 96, 96))
    save(im, "slot")


# ---------------------------------------------------------------- шкалы

def energy():
    # заливка 10x54: тёмно-красный снизу, оранжевый и жёлтый сверху, светлая полоса слева, тёмная справа
    fill = img(10, 54)
    for y in range(54):
        t = 1.0 - y / 53.0                         # 0 внизу, 1 вверху
        r = int(150 + 105 * t)
        g = int(24 + 170 * t * t)
        b = int(20 + 30 * t * t)
        for x in range(10):
            k = 1.0
            if x == 0:
                k = 1.25
            elif x == 1:
                k = 1.12
            elif x >= 8:
                k = 0.72
            c = tuple(max(0, min(255, int(v * k))) for v in (r, g, b))
            px(fill, x, y, c)
        if y % 4 == 3:                              # поперечные деления заливки
            for x in range(10):
                px(fill, x, y, tuple(int(v * 0.8) for v in (r, g, b)))
    save(fill, "energy_fill")
    ov = img(12, 56)                                # стекло и деления поверх
    for i in range(8):
        y = 6 + i * 6
        px(ov, 9, y, (0, 0, 0), 120); px(ov, 10, y, (0, 0, 0), 120)
        if i % 2 == 0:
            px(ov, 8, y, (0, 0, 0), 120)
    for y in range(2, 54):
        px(ov, 2, y, (255, 255, 255), 38)
    save(ov, "energy_overlay")


def tank():
    ov = img(16, 52)
    for y in range(2, 50):
        px(ov, 2, y, (255, 255, 255), 56); px(ov, 3, y, (255, 255, 255), 26)
    for i in range(1, 8):
        y = 51 - 1 - i * 50 // 8
        px(ov, 11, y, (0, 0, 0), 150); px(ov, 12, y, (0, 0, 0), 150)
        if i % 2 == 0:
            px(ov, 10, y, (0, 0, 0), 150)
        if i == 4:
            px(ov, 9, y, (0, 0, 0), 150)
    save(ov, "tank_overlay")


# ---------------------------------------------------------------- стрелка прогресса и пламя

def arrow():
    mask = [[False] * 24 for _ in range(16)]
    for y in range(4, 12):
        for x in range(1, 15):
            mask[y][x] = True
    for (x, y0, y1) in ((14, 1, 14), (15, 1, 14), (16, 2, 13), (17, 2, 13), (18, 3, 12), (19, 4, 11), (20, 5, 10),
                        (21, 6, 9), (22, 7, 8)):
        for y in range(y0, y1 + 1):
            mask[y][x] = True
    for state in ("off", "on"):
        im = img(24, 16)
        for y in range(16):
            for x in range(24):
                if not mask[y][x]:
                    continue
                edge = any(not (0 <= x + dx < 24 and 0 <= y + dy < 16 and mask[y + dy][x + dx])
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if edge:
                    px(im, x, y, OUTLINE if state == "off" else (66, 36, 12))
                    continue
                if state == "off":
                    c = (112, 116, 126) if y < 8 else (92, 96, 106)
                else:
                    t = max(0.0, min(1.0, (y - 2) / 11.0))
                    c = (255, int(232 - 100 * t), int(120 - 84 * t))
                    if y <= 5:
                        c = (255, 246, 184)
                px(im, x, y, c)
        save(im, f"arrow_{state}")


def flame():
    shape = [
        "......##......",
        "......###.....",
        ".....####.....",
        "....#####..#..",
        "...######.##..",
        "...#######.##.",
        "..##########.#",
        "..###########.",
        "..###########.",
        "..###########.",
        "...#########..",
        "...#########..",
        "....#######...",
        ".....#####....",
    ]
    for state in ("off", "on"):
        im = img(14, 14)
        for y, row in enumerate(shape):
            for x, ch in enumerate(row):
                if ch != "#":
                    continue
                edge = any(not (0 <= x + dx < 14 and 0 <= y + dy < 14 and shape[y + dy][x + dx] == "#")
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if state == "off":
                    c = OUTLINE if edge else (74, 77, 86)
                else:
                    t = y / 13.0
                    c = (72, 20, 8) if edge else ((255, 236, 130) if t > 0.62 and 3 < x < 10 else (255, int(190 - 120 * t), 40))
                px(im, x, y, c)
        save(im, f"flame_{state}")


# ---------------------------------------------------------------- вкладки и значки

def tabs():
    for name, face, lit in (("tab", (172, 175, 184), False), ("tab_active", FACE, True)):
        im = img(22, 24)
        rect(im, 0, 0, 21, 23, face)
        for i in range(22):
            px(im, i, 0, OUTLINE); px(im, i, 23, OUTLINE)
        for i in range(24):
            px(im, 0, i, OUTLINE)
        for (x, y) in ((0, 0), (0, 23)):
            px(im, x, y, (0, 0, 0), 0)
        px(im, 1, 1, OUTLINE); px(im, 1, 22, OUTLINE)
        for i in range(2, 21):
            px(im, i, 1, HI if lit else HI2)
            px(im, i, 22, SH)
        for i in range(2, 22):
            px(im, 1, i, HI if lit else HI2)
        if lit:                                       # активная вкладка сливается с окном
            for y in range(1, 23):
                px(im, 21, y, FACE)
        else:
            for y in range(1, 23):
                px(im, 21, y, OUTLINE)
        save(im, name)


def icon_config():
    im = img(16, 16)
    cx, cy = 7.5, 7.5
    mask = set()
    for y in range(16):
        for x in range(16):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            ang = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            tooth = (ang % 45) < 22.5
            if (r <= 4.9) or (r <= 6.6 and tooth):
                mask.add((x, y))
    hole = {(x, y) for (x, y) in mask if math.hypot(x - cx, y - cy) < 2.3}
    for (x, y) in mask:
        edge = any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        hole_edge = (x, y) in hole or any((x + dx, y + dy) in hole for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if (x, y) in hole:
            px(im, x, y, (0, 0, 0), 0)
        elif edge or hole_edge:
            px(im, x, y, OUTLINE)
        else:
            lit = (x - cx) + (y - cy)
            px(im, x, y, (214, 218, 228) if lit < -1.5 else ((150, 156, 170) if lit < 2 else (104, 109, 122)))
    save(im, "icon_config")


def cells():
    colors = {"none": (116, 118, 126), "input": (63, 111, 214), "output": (224, 138, 42), "all": (63, 174, 79)}
    for name, c in colors.items():
        im = img(24, 14)
        rect(im, 0, 0, 23, 13, c)
        for i in range(24):
            px(im, i, 0, OUTLINE); px(im, i, 13, OUTLINE)
        for i in range(14):
            px(im, 0, i, OUTLINE); px(im, 23, i, OUTLINE)
        for (x, y) in ((0, 0), (23, 0), (0, 13), (23, 13)):
            px(im, x, y, (0, 0, 0), 0)
        for i in range(1, 23):
            px(im, i, 1, tuple(min(255, int(v * 1.35)) for v in c))
            px(im, i, 12, tuple(int(v * 0.68) for v in c))
        save(im, f"cell_{name}")


def checks():
    for state in ("off", "on"):
        im = img(11, 11)
        rect(im, 0, 0, 10, 10, DISP)
        for i in range(11):
            px(im, i, 0, OUTLINE); px(im, 0, i, OUTLINE)
            px(im, i, 10, HI2); px(im, 10, i, HI2)
        px(im, 0, 10, SH2); px(im, 10, 0, SH2)
        if state == "on":
            for (x, y) in ((2, 5), (3, 6), (4, 7), (5, 6), (6, 5), (7, 4), (8, 3)):
                px(im, x, y, (104, 232, 128)); px(im, x, y + 1, (52, 168, 76))
        save(im, f"check_{state}")


if __name__ == "__main__":
    background(); well(); display(); slot(); energy(); tank(); arrow(); flame(); tabs(); icon_config(); cells(); checks()
    print(sorted(p.name for p in OUT.glob("*")))
