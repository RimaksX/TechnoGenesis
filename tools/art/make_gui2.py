"""Спрайты интерфейса в стиле Mekanism (свои, нарисованные заново): окно, слот, шкала, экран, кнопки, значки."""
import math
from PIL import Image, ImageDraw
import make_gui as M
from make_gui import img, px, rect, save, OUT, HI, FACE, OUTLINE

DARK = (55, 55, 55)
GLYPH_O = (28, 30, 36)
GLYPH_M = (84, 88, 99)
GLYPH_H = (150, 156, 170)


def gauge():                       # утопленная рамка шкал и экранов: 4x4, граница 1
    im = img(4, 4)
    rect(im, 0, 0, 3, 3, (36, 38, 44))
    for i in range(4):
        px(im, i, 0, DARK); px(im, 0, i, DARK)
        px(im, i, 3, HI); px(im, 3, i, HI)
    px(im, 0, 3, FACE); px(im, 3, 0, FACE)
    save(im, "gauge", 1)


def tank_overlay():                # внутренняя тень и деления на баке 16x50
    im = img(16, 50)
    for i in range(16):
        px(im, i, 0, (0, 0, 0), 110)
    for i in range(50):
        px(im, 0, i, (0, 0, 0), 110)
    for y in range(5, 50, 5):
        ln = 6 if y % 10 == 0 else 3
        for x in range(16 - ln, 16):
            px(im, x, y, (0, 0, 0), 150)
    save(im, "tank_overlay")


def button():                      # светлая кнопка (красится цветом в коде), девятипатч 6x6, граница 2
    im = img(6, 6)
    rect(im, 0, 0, 5, 5, (232, 232, 236))
    for i in range(6):
        px(im, i, 0, OUTLINE); px(im, 0, i, OUTLINE); px(im, i, 5, OUTLINE); px(im, 5, i, OUTLINE)
    for (x, y) in ((0, 0), (5, 0), (0, 5), (5, 5)):
        px(im, x, y, (0, 0, 0), 0)
    for i in range(1, 5):
        px(im, i, 1, HI); px(im, 1, i, HI)
        px(im, i, 4, (150, 152, 160)); px(im, 4, i, (150, 152, 160))
    px(im, 4, 1, (200, 202, 208)); px(im, 1, 4, (200, 202, 208))
    save(im, "button", 2)
    d = img(6, 6)                  # нажатая/выбранная: фаска наоборот
    rect(d, 0, 0, 5, 5, (190, 192, 198))
    for i in range(6):
        px(d, i, 0, OUTLINE); px(d, 0, i, OUTLINE); px(d, i, 5, OUTLINE); px(d, 5, i, OUTLINE)
    for (x, y) in ((0, 0), (5, 0), (0, 5), (5, 5)):
        px(d, x, y, (0, 0, 0), 0)
    for i in range(1, 5):
        px(d, i, 1, (110, 112, 120)); px(d, 1, i, (110, 112, 120))
        px(d, i, 4, (222, 224, 230)); px(d, 4, i, (222, 224, 230))
    save(d, "button_down", 2)


def holder():                      # держатель вкладки слева от окна 26x26, граница 4; правый край открыт в окно
    im = img(26, 26)
    rect(im, 3, 0, 25, 25, FACE)
    for i in range(3, 26):
        px(im, i, 0, OUTLINE); px(im, i, 25, OUTLINE)
        px(im, i, 1, HI)
        px(im, i, 24, (88, 91, 100))
    for i in range(1, 25):
        px(im, 3, i, OUTLINE); px(im, 4, i, HI)
    for (x, y) in ((3, 0), (3, 25)):
        px(im, x, y, (0, 0, 0), 0)
    px(im, 4, 1, OUTLINE); px(im, 4, 24, OUTLINE)
    rect(im, 0, 0, 2, 25, (0, 0, 0), 0)
    for i in range(3, 26):
        px(im, i, 2, (228, 230, 236)); px(im, i, 23, (150, 153, 162))
    save(im, "holder", 4)


def arrows():
    for on, name in ((False, "arrow_off"), (True, "arrow_on")):
        im = img(28, 8)
        c = (62, 232, 132) if on else (128, 130, 138)
        d = (30, 150, 84) if on else (96, 98, 106)
        rect(im, 0, 2, 19, 5, c)
        for i in range(8):
            w = 8 - abs(i - 3.5) * 2
            for x in range(20, 28):
                if (x - 20) < 8 - abs(i - 3.5) * 2.2:
                    px(im, x, i, c)
        for x in range(0, 20):
            px(im, x, 5, d)
        save(im, name)


def flames():
    rows = [0, 1, 1, 2, 3, 3, 4, 5, 5, 6, 6, 5, 4]
    for on, name in ((False, "flame_off"), (True, "flame_on")):
        im = img(13, 13)
        for y, h in enumerate(rows):
            for x in range(6 - h, 6 + h + 1):
                if not on:
                    t = 0.55 + 0.1 * (y / 12)
                    px(im, x, y, (int(150 * t + 40), int(152 * t + 40), int(160 * t + 40)))
                else:
                    dx = abs(x - 6) / max(h, 1)
                    inner = y > 5 and dx < 0.5 and y < 12
                    core = y > 8 and dx < 0.28 and y < 11
                    px(im, x, y, (255, 238, 120) if core else (255, 170, 40) if inner else (232, 76, 28))
        save(im, name)


# ---- значки 16x16: контур, заливка, блик
def glyph(name, draw):
    mask = Image.new("L", (16, 16), 0)
    d = ImageDraw.Draw(mask)
    draw(d)
    im = img(16, 16)
    m = mask.load()
    def on(x, y):
        return 0 <= x < 16 and 0 <= y < 16 and m[x, y] > 0
    for y in range(16):
        for x in range(16):
            if not on(x, y):
                continue
            edge = not (on(x - 1, y) and on(x + 1, y) and on(x, y - 1) and on(x, y + 1))
            if edge:
                px(im, x, y, GLYPH_O)
            elif not on(x - 1, y) or not on(x, y - 1) or not on(x - 1, y - 1):
                px(im, x, y, GLYPH_H)
            else:
                px(im, x, y, GLYPH_M)
    # блик сверху-слева: внутренние пиксели рядом с контуром
    for y in range(1, 15):
        for x in range(1, 15):
            if on(x, y) and im.getpixel((x, y))[:3] == GLYPH_M and (im.getpixel((x - 1, y))[:3] == GLYPH_O or im.getpixel((x, y - 1))[:3] == GLYPH_O):
                px(im, x, y, GLYPH_H)
    save(im, name)


def icons():
    glyph("icon_items", lambda d: (d.rectangle((2, 3, 13, 12), fill=255)))
    # сундук: крышка и замок рисуем поверх тёмным
    im = Image.open(OUT / "icon_items.png").convert("RGBA")
    for x in range(3, 13):
        px(im, x, 6, GLYPH_O)
    px(im, 7, 7, GLYPH_O); px(im, 8, 7, GLYPH_O); px(im, 7, 8, GLYPH_H); px(im, 8, 8, GLYPH_H)
    im.save(OUT / "icon_items.png")

    def drop(d):
        pts = [(8, 1), (11, 6), (13, 9), (12, 12), (10, 14), (6, 14), (4, 12), (3, 9), (5, 6)]
        d.polygon(pts, fill=255)
    glyph("icon_fluids", drop)
    glyph("icon_energy", lambda d: d.polygon([(10, 1), (3, 9), (7, 9), (5, 15), (13, 6), (9, 6), (11, 1)], fill=255))
    glyph("icon_eject", lambda d: (d.polygon([(8, 2), (14, 9), (2, 9)], fill=255), d.rectangle((2, 11, 13, 13), fill=255)))

    def cross(d):
        d.line((3, 3, 12, 12), fill=255, width=3)
        d.line((12, 3, 3, 12), fill=255, width=3)
    glyph("icon_clear", cross)


def cleanup():
    for n in ("well", "display", "tab", "tab_active", "energy_fill", "energy_overlay",
              "cell_all", "cell_input", "cell_none", "cell_output", "check_on", "check_off"):
        for ext in (".png", ".png.mcmeta"):
            p = OUT / (n + ext)
            if p.exists():
                p.unlink()


if __name__ == "__main__":
    M.background(); M.slot(); M.icon_config()
    gauge(); tank_overlay(); button(); holder(); arrows(); flames(); icons(); cleanup()
    print(sorted(p.name for p in OUT.iterdir()))
