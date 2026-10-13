"""Собственный стиль меню Контура: тёмная графитовая панель, бирюзовый акцент, слоты входа/выхода разного цвета."""
import json
from pathlib import Path
from PIL import Image
OUT = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/gui/sprites")

BLACK = (9, 11, 15)
HI1 = (98, 110, 130)       # внешняя светлая фаска
HI2 = (64, 72, 88)
BODY = (43, 48, 58)
SH2 = (34, 38, 46)
SH1 = (24, 27, 33)
TEAL = (46, 214, 196)
TEAL_D = (22, 120, 112)
AMBER = (240, 168, 50)
AMBER_D = (128, 82, 20)
STEEL = (84, 94, 112)


def img(w, h): return Image.new("RGBA", (w, h), (0, 0, 0, 0))
def px(im, x, y, c, a=255):
    if 0 <= x < im.width and 0 <= y < im.height: im.putpixel((x, y), (*c[:3], a))
def rect(im, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): px(im, x, y, c)
def save(im, name, nine=None):
    im.save(OUT / f"{name}.png")
    meta = OUT / f"{name}.png.mcmeta"
    if nine:
        meta.write_text(json.dumps({"gui": {"scaling": {"type": "nine_slice", "width": im.width, "height": im.height, "border": nine}}}, indent=2) + "\n")
    elif meta.exists(): meta.unlink()

def ring(im, i, tl, br):
    w, h = im.size
    for x in range(i, w - i):
        px(im, x, i, tl); px(im, x, h - 1 - i, br)
    for y in range(i, h - i):
        px(im, i, y, tl); px(im, w - 1 - i, y, br)

def background():                  # окно: графит, фаска, бирюзовые точки в углах; девятипатч 24x24, граница 4
    im = img(24, 24)
    rect(im, 0, 0, 23, 23, BODY)
    ring(im, 0, BLACK, BLACK)
    for (x, y) in ((0, 0), (23, 0), (0, 23), (23, 23)): px(im, x, y, (0, 0, 0), 0)
    for (x, y) in ((1, 1), (22, 1), (1, 22), (22, 22)): px(im, x, y, BLACK)
    ring(im, 1, HI1, SH1)
    ring(im, 2, HI2, SH2)
    for (x, y) in ((1, 1), (22, 1), (1, 22), (22, 22)): px(im, x, y, BLACK)
    px(im, 22, 1, SH1); px(im, 1, 22, SH1)
    for (x, y) in ((3, 3), (20, 3), (3, 20), (20, 20)): px(im, x, y, TEAL_D)
    save(im, "background", 4)

def slot(name, tl, br, fill=(28, 32, 39)):     # слот 18x18
    im = img(18, 18)
    rect(im, 0, 0, 17, 17, fill)
    ring(im, 0, tl, br)
    ring(im, 1, tuple(max(0, c - 8) for c in fill), tuple(min(255, c + 4) for c in fill))
    save(im, name)

def gauge():                       # утопленная рамка шкал и экранов 4x4, граница 1
    im = img(4, 4)
    rect(im, 0, 0, 3, 3, (17, 20, 25))
    ring(im, 0, BLACK, STEEL)
    px(im, 0, 3, SH2); px(im, 3, 0, SH2)
    save(im, "gauge", 1)

def tank_overlay():
    im = img(16, 50)
    for i in range(16): px(im, i, 0, (0, 0, 0), 120)
    for i in range(50): px(im, 0, i, (0, 0, 0), 120)
    for y in range(5, 50, 5):
        ln = 6 if y % 10 == 0 else 3
        for x in range(16 - ln, 16): px(im, x, y, (255, 255, 255), 90)
    save(im, "tank_overlay")

def holder():                      # держатель вкладки 30x36, граница 5; правые 4 пикселя открыты в окно
    W, H = 30, 36
    im = img(W, H)
    rect(im, 0, 0, W - 1, H - 1, BODY)
    for x in range(0, W):
        px(im, x, 0, BLACK); px(im, x, H - 1, BLACK)
        px(im, x, 1, HI1); px(im, x, H - 2, SH1)
        px(im, x, 2, HI2); px(im, x, H - 3, SH2)
    for y in range(1, H - 1):
        px(im, 0, y, BLACK); px(im, 1, y, HI1); px(im, 2, y, HI2)
    for (x, y) in ((0, 0), (0, H - 1)): px(im, x, y, (0, 0, 0), 0)
    px(im, 1, 1, BLACK); px(im, 1, H - 2, BLACK)
    px(im, 3, 3, TEAL_D)
    save(im, "holder", 5)

def arrows():
    for on, name in ((False, "arrow_off"), (True, "arrow_on")):
        im = img(28, 8)
        c, d = (TEAL, TEAL_D) if on else ((70, 79, 95), (44, 50, 61))
        rect(im, 0, 2, 19, 5, c)
        for i in range(8):
            for x in range(20, 28):
                if (x - 20) < 8 - abs(i - 3.5) * 2.2: px(im, x, i, c)
        for x in range(0, 20): px(im, x, 5, d)
        save(im, name)

def flames():
    rows = [0, 1, 1, 2, 3, 3, 4, 5, 5, 6, 6, 5, 4]
    for on, name in ((False, "flame_off"), (True, "flame_on")):
        im = img(13, 13)
        for y, h in enumerate(rows):
            for x in range(6 - h, 6 + h + 1):
                if not on:
                    t = 0.8 + 0.2 * y / 12
                    px(im, x, y, (int(70 * t), int(79 * t), int(95 * t)))
                else:
                    dx = abs(x - 6) / max(h, 1)
                    inner = y > 5 and dx < 0.5 and y < 12
                    core = y > 8 and dx < 0.28 and y < 11
                    px(im, x, y, (255, 238, 120) if core else (255, 170, 40) if inner else (232, 76, 28))
        save(im, name)

if __name__ == "__main__":
    background(); gauge(); tank_overlay(); holder(); arrows()
    slot("slot", (12, 14, 18), (78, 88, 106))
    slot("slot_in", TEAL_D, (36, 176, 162), (26, 36, 40))
    slot("slot_out", AMBER_D, (214, 140, 40), (40, 33, 26))
    slot("slot_module", (60, 40, 90), (150, 110, 220), (32, 28, 44))
