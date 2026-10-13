#!/usr/bin/env python3
"""Лист спрайтов для сырья: референсы ванили, черновики, палитры и ч/б-проверка контраста."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw
from kontur_gen import textures as T, rawore as RW
from kontur_gen.defs import *

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sprite_sheet.png")
W = H = 1024
sheet = Image.new("RGBA", (W, H), (44, 46, 52, 255))
d = ImageDraw.Draw(sheet)
from PIL import ImageFont
for _f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
    if Path(_f).exists():
        _font = ImageFont.truetype(_f, 13)
        break
else:
    _font = None
_orig_text = d.text
d.text = lambda xy, t, fill=None, **kw: _orig_text(xy, t, fill=fill, font=_font, **kw)


def gray(im):
    g = Image.new("RGBA", im.size)
    for y in range(im.height):
        for x in range(im.width):
            r, gg, b, a = im.getpixel((x, y))
            v = int(0.299 * r + 0.587 * gg + 0.114 * b)
            g.putpixel((x, y), (v, v, v, a))
    return g


def put(im, x, y, size):
    big = im.resize((size, size), Image.NEAREST)
    sheet.paste(big, (x, y), big)


refs = ["raw_iron", "raw_copper", "raw_gold", "amethyst_shard", "quartz", "coal", "lapis_lazuli", "diamond",
        "emerald", "redstone", "glowstone_dust", "netherite_scrap", "flint", "clay_ball", "brick", "echo_shard"]
d.text((6, 2), "1. Референсы ванили (цвет / ч-б)", fill=(230, 230, 230, 255))
for i, n in enumerate(refs):
    try:
        im = T.van("item/" + n)
    except Exception:
        im = Image.new("RGBA", (16, 16))
    put(im, i * 64, 14, 64)
    put(gray(im), i * 64, 78, 64)

d.text((6, 146), "2. Черновики сырья (10x): форма, грани, свет сверху-слева", fill=(230, 230, 230, 255))
sprites = [RW.raw_texture(m) for m in MINERALS]
for i, (m, im) in enumerate(zip(MINERALS, sprites)):
    x, y = (i % 6) * 168 + 8, 160 + (i // 6) * 176
    put(im, x, y, 160)
    d.text((x, y + 162), m.id, fill=(200, 200, 200, 255))

d.text((6, 516), "3. Проверка контраста: чёрно-белый вид", fill=(230, 230, 230, 255))
for i, im in enumerate(sprites):
    x, y = (i % 12) * 84 + 8, 532
    put(gray(im), x, y, 80)
    put(im, x, y + 84, 80)

d.text((6, 706), "4. Палитры (тона 0-8: тени сдвинуты в холодное, света в тёплое)", fill=(230, 230, 230, 255))
for i, m in enumerate(MINERALS):
    rp = RW.ramp9(m.ramp, key=("ore", m.id))
    y = 722 + i * 24
    for j, c in enumerate(rp):
        d.rectangle([8 + j * 26, y, 8 + j * 26 + 24, y + 20], fill=(*c, 255))
    d.text((254, y + 4), m.id, fill=(200, 200, 200, 255))
sheet.save(out)
print("saved", out)
