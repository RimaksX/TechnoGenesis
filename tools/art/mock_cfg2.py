import sys
sys.path.insert(0, ".")
from PIL import Image, ImageDraw
import mock_gui4 as M
S = M.S
IN, OUT, BOTH, NONE, DIS = (0x94, 0x9E, 0xB3), (0xCA, 0xA3, 0x7D), (0x94, 0xB5, 0x93), (0x2A, 0x2F, 0x3B), (23, 26, 33)
def sh(c, k): return tuple(min(255, int(v * k)) for v in c)
NET = {"В": (1, 0), "Л": (0, 1), "П": (2, 1), "З": (3, 1), "Н": (1, 2)}

def render(name, d, tabs, sel, cells, legend, title, eject=False, tabs_modules=True):
    W, H = 176, 184
    LEFT = 32
    g = Image.new("RGBA", (W + LEFT + 6, H + 6), (0, 0, 0, 0))
    ox, oy = LEFT, 3
    def P(im, x, y): g.alpha_composite(im, (ox + x, oy + y))
    tabY = 34
    if d["module"]:
        hh = 61 if d["cooler"] else 39
        P(M.nine(M.spr("holder"), 31, hh, 5), -27, 34); tabY = 34 + hh + 3
    P(M.nine(M.spr("holder"), 31, 30, 5), -27, tabY)
    P(M.nine(M.spr("background"), W, H, 4), 0, 0)
    if d["module"]:
        P(M.spr("slot_module"), d["module"][0] - 1, d["module"][1] - 1)
        if d["cooler"]: P(M.spr("slot_module"), d["cooler"][0] - 1, d["cooler"][1] - 1)
        P(M.nine(M.spr("gauge"), 18, 6, 1), -21, 34 + (49 if d["cooler"] else 27))
    dr = ImageDraw.Draw(g)
    dr.rectangle([ox - 22, oy + tabY + 5, ox - 3, oy + tabY + 24], fill=(245, 197, 66, 64))
    P(M.item("wrench"), -20, tabY + 7)
    P(M.nine(M.spr("gauge"), 160, 84, 1), 8, 16)
    for r in [(8 + c * 18, 102 + rr * 18) for rr in range(3) for c in range(9)] + [(8 + c * 18, 160) for c in range(9)]:
        P(M.spr("slot"), r[0] - 1, r[1] - 1)
    def box(x, y, w, h, col, light=True):
        dr.rectangle([ox + x, oy + y, ox + x + w - 1, oy + y + h - 1], fill=(16, 19, 26))
        dr.rectangle([ox + x + 1, oy + y + 1, ox + x + w - 2, oy + y + h - 2], fill=col)
        dr.rectangle([ox + x + 1, oy + y + 1, ox + x + w - 2, oy + y + 1], fill=sh(col, 1.18))
        dr.rectangle([ox + x + 1, oy + y + 1, ox + x + 1, oy + y + h - 2], fill=sh(col, 1.18))
        dr.rectangle([ox + x + 1, oy + y + h - 2, ox + x + w - 2, oy + y + h - 2], fill=sh(col, .78))
        dr.rectangle([ox + x + w - 2, oy + y + 1, ox + x + w - 2, oy + y + h - 2], fill=sh(col, .78))
    for i, t in enumerate(tabs):
        box(12 + i * 26, 19, 24, 13, (79, 106, 154) if t == sel else (53, 59, 74))
    box(14 + 20, 38 + 20, 18, 18, DIS)
    for letter, (c, r) in NET.items():
        box(14 + c * 20, 38 + r * 20, 18, 18, cells[letter])
    for i, (col, _) in enumerate(legend):
        box(102, 48 + i * 10, 8, 8, col)
    box(102, 88, 40, 10, (60, 122, 86) if eject else (58, 64, 78))
    g = g.resize((g.width * S, g.height * S), M.Image.NEAREST)
    dr = ImageDraw.Draw(g)
    def T(x, y, text, fill, font=M.FONT): dr.text(((ox + x) * S, (oy + y) * S), text, fill=fill, font=font)
    tt = M.TITLES.get(name, name); tw = dr.textlength(tt, font=M.FONT) / S
    T((W - tw) / 2, 5.5, tt, (212, 222, 238, 255))
    ICON = {"Вход": ["...##...", "...##...", ".######.", "..####..", "...##...", "#......#", "########"],
            "Вых": ["...##...", "..####..", ".######.", "...##...", "...##...", "#......#", "########"],
            "Жидк": ["...##...", "..####..", "..####..", ".######.", ".######.", ".######.", "..####.."],
            "Энер": ["....##..", "...##...", "..##....", ".######.", "...##...", "..##....", ".##....."]}
    DIG = {"1": [".#.", "##.", ".#.", ".#.", "###"], "2": ["##.", "..#", ".#.", "#..", "###"], "3": ["##.", "..#", ".#.", "..#", "##."]}
    COL = {"Жидк": (127, 184, 240), "Энер": (240, 192, 80)}
    for i, t in enumerate(tabs):
        key = t[:3] if t.startswith("Вых") else t
        col = COL.get(t, (230, 236, 248))
        if t != sel: col = tuple(int(v * .6) for v in col)
        dg = t[3] if t.startswith("Вых") else None
        total = 8 + (4 if dg else 0)
        x0 = 12 + i * 26 + (24 - total) // 2
        y0 = 19 + (13 - 7) // 2
        for r, row in enumerate(ICON[key]):
            for c, ch in enumerate(row):
                if ch == "#": dr.rectangle([(ox + x0 + c) * S, (oy + y0 + r) * S, (ox + x0 + c + 1) * S - 1, (oy + y0 + r + 1) * S - 1], fill=col)
        if dg:
            for r, row in enumerate(DIG[dg]):
                for c, ch in enumerate(row):
                    if ch == "#": dr.rectangle([(ox + x0 + 9 + c) * S, (oy + 19 + 4 + r) * S, (ox + x0 + 9 + c + 1) * S - 1, (oy + 19 + 4 + r + 1) * S - 1], fill=col)
    for letter, (c, r) in NET.items():
        w = dr.textlength(letter, font=M.FONT) / S
        T(14 + c * 20 + (18 - w) / 2, 38 + r * 20 + 4.5, letter, (26, 30, 40, 255) if cells[letter] != NONE else (124, 135, 156, 255))
    T(102, 35.5, title, (245, 197, 66, 255))
    for i, (col, label) in enumerate(legend):
        T(114, 48 + i * 10 - 1, label, (196, 204, 218, 255))
    T(112, 87.5, "Авто", (216, 245, 228, 255) if eject else (154, 164, 184, 255))
    canvas = Image.new("RGBA", g.size, (70, 72, 80, 255)); canvas.alpha_composite(g)
    return canvas

kinds = M.parse()
tabs = ["Вход", "Вых1", "Вых2", "Жидк", "Энер"]
a = render("washing_drum", kinds["washing_drum"], tabs, "Вых2",
           {"В": NONE, "Л": OUT, "П": OUT, "З": NONE, "Н": OUT}, [(NONE, "Закрыто"), (OUT, "Выход")], "Выход 2")
b = render("water_pump", {**kinds["water_pump"]}, ["Жидк", "Энер"], "Жидк",
           {"В": BOTH, "Л": BOTH, "П": IN, "З": OUT, "Н": DIS}, [(NONE, "Закрыто"), (IN, "Вход"), (OUT, "Выход"), (BOTH, "Оба")], "Жидкости", eject=True)
sh_ = Image.new("RGBA", (a.width * 2, a.height), (70, 72, 80, 255)); sh_.paste(a, (0, 0)); sh_.paste(b, (a.width, 0))
sh_.convert("RGB").save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/cfg_mock2.png")
M.__name__
