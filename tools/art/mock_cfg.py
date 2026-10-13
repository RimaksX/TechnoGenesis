import sys
sys.path.insert(0, ".")
from PIL import Image, ImageDraw
import mock_gui4 as M
S = M.S
COLS = ["Зад", "Лев", "Прав", "Верх", "Низ"]
IN, OUT, BOTH, NONE = (0x94, 0x9E, 0xB3), (0xCA, 0xA3, 0x7D), (0x94, 0xB5, 0x93), (0x2A, 0x2F, 0x3B)

def sh(c, k): return tuple(min(255, int(v * k)) for v in c)

def render(name, rows, d):
    W, H = 176, 184
    LEFT = 30
    g = Image.new("RGBA", (W + LEFT + 6, H + 6), (0, 0, 0, 0))
    ox, oy = LEFT, 3
    def P(im, x, y): g.alpha_composite(im, (ox + x, oy + y))
    tabY = 34
    if d["module"]:
        hh = 58 if d["cooler"] else 36
        P(M.nine(M.spr("holder"), 30, hh, 5), -26, 34); tabY = 34 + hh + 3
    P(M.nine(M.spr("holder"), 30, 27, 5), -26, tabY)
    P(M.nine(M.spr("background"), W, H, 4), 0, 0)
    if d["module"]:
        P(M.spr("slot_module"), d["module"][0] - 1, d["module"][1] - 1)
        if d["cooler"]: P(M.spr("slot_module"), d["cooler"][0] - 1, d["cooler"][1] - 1)
    P(M.item("wrench"), -21, tabY + 5)
    dr = ImageDraw.Draw(g)
    dr.rectangle([ox - 23, oy + tabY + 3, ox - 4, oy + tabY + 22], fill=(245, 197, 66, 64))
    P(M.nine(M.spr("gauge"), 160, 84, 1), 8, 16)
    for r in [(8 + c * 18, 102 + rr * 18) for rr in range(3) for c in range(9)] + [(8 + c * 18, 160) for c in range(9)]:
        P(M.spr("slot"), r[0] - 1, r[1] - 1)
    def cell(x, y, col):
        dr.rectangle([ox + x, oy + y, ox + x + 15, oy + y + 8], fill=(16, 19, 26))
        dr.rectangle([ox + x + 1, oy + y + 1, ox + x + 14, oy + y + 7], fill=col)
        dr.rectangle([ox + x + 1, oy + y + 1, ox + x + 14, oy + y + 1], fill=sh(col, 1.18))
        dr.rectangle([ox + x + 1, oy + y + 1, ox + x + 1, oy + y + 7], fill=sh(col, 1.18))
        dr.rectangle([ox + x + 1, oy + y + 7, ox + x + 14, oy + y + 7], fill=sh(col, .78))
        dr.rectangle([ox + x + 14, oy + y + 1, ox + x + 14, oy + y + 7], fill=sh(col, .78))
    dr.rectangle([ox + 12, oy + 18, ox + 57, oy + 28], fill=(16, 19, 26))
    dr.rectangle([ox + 13, oy + 19, ox + 56, oy + 27], fill=(60, 122, 86))
    for r, (label, vals) in enumerate(rows):
        for c, v in enumerate(vals):
            cell(64 + c * 20, 32 + r * 11, {"i": IN, "o": OUT, "b": BOTH, "n": NONE, "x": (23, 26, 33)}[v])
    g = g.resize((g.width * S, g.height * S), M.Image.NEAREST)
    dr = ImageDraw.Draw(g)
    def T(x, y, text, fill, font=M.FONT): dr.text(((ox + x) * S, (oy + y) * S), text, fill=fill, font=font)
    t = M.TITLES.get(name, name); tw = dr.textlength(t, font=M.FONT) / S
    T((W - tw) / 2, 5.5, t, (212, 222, 238, 255))
    T(14, 19.5, "Авто-вывод", (216, 245, 228, 255))
    for c, n in enumerate(COLS):
        w = dr.textlength(n, font=M.FONT) / S
        T(64 + c * 20 + (16 - w) / 2, 19.5, n, (140, 152, 172, 255))
    for r, (label, vals) in enumerate(rows):
        T(12, 32 + r * 11 + .5, label, (196, 204, 218, 255))
    canvas = Image.new("RGBA", g.size, (70, 72, 80, 255)); canvas.alpha_composite(g)
    return canvas

kinds = M.parse()
a = render("washing_drum", [("Входы", "iiiii"), ("Выход 1", "oonoo"), ("Выход 2", "nooxn"), ("Жидкости", "bbbbb"), ("Энергия", "innnn")], kinds["washing_drum"])
b = render("magnetic_separator", [("Входы", "iiiii"), ("Выход 1", "ooooo"), ("Выход 2", "nnnno"), ("Выход 3", "nnnon"), ("Энергия", "innnn")], kinds["magnetic_separator"])
sh_ = Image.new("RGBA", (a.width * 2, a.height), (70, 72, 80, 255)); sh_.paste(a, (0, 0)); sh_.paste(b, (a.width, 0))
sh_.convert("RGB").save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/cfg_mock.png")
print(sh_.size)
