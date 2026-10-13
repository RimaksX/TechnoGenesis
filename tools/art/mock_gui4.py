"""Макет меню машин по текущим числам из MachineKind.java и спрайтам мода (без запуска игры)."""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path("/home/user/TechnoGenesis/src/main")
SRC = (ROOT / "java/dev/technogenesis/kontur/machine/MachineKind.java").read_text()
SP = ROOT / "resources/assets/kontur/textures/gui/sprites"
IT = ROOT / "resources/assets/kontur/textures/item"
S = 3
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8 * S + 1)
FONT_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 6 * S)
BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16 * S)

def spr(n): return Image.open(SP / f"{n}.png").convert("RGBA")
def item(n): return Image.open(IT / f"{n}.png").convert("RGBA")

def nine(im, w, h, b):
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); W, H = im.size
    xs = [(0, b, 0, b), (b, W - b, b, w - b), (W - b, W, w - b, w)]
    ys = [(0, b, 0, b), (b, H - b, b, h - b), (H - b, H, h - b, h)]
    for (sx0, sx1, dx0, dx1) in xs:
        for (sy0, sy1, dy0, dy1) in ys:
            out.paste(im.crop((sx0, sy0, sx1, sy1)).resize((max(1, dx1 - dx0), max(1, dy1 - dy0)), 0), (dx0, dy0))
    return out

def parse():
    kinds = {}
    for m in re.finditer(r'([A-Z_]+)\("([a-z_]+)",.*?MachineDefinition\.builder\(\)(.*?)\.build\(\)\)[,;]', SRC, re.S):
        body = m.group(3)
        d = dict(slots=[], tanks=[], arrow=None, flame=None, module=None, cooler=None, coating=None, kind="CONSUMER")
        for s in re.finditer(r'\.slot\((\d+), (\d+), SlotRole\.(\w+)\)', body):
            d["slots"].append((int(s.group(1)), int(s.group(2)), s.group(3)))
        for t in re.finditer(r'\.tank\((\d+), (\d+), (\d+), (true|false)\)', body):
            d["tanks"].append((int(t.group(1)), int(t.group(2)), t.group(4) == "true"))
        for key in ("arrow", "flame", "module", "cooler", "coating"):
            a = re.search(r'\.%s\((-?\d+), (-?\d+)\)' % key, body)
            if a: d[key] = (int(a.group(1)), int(a.group(2)))
        k = re.search(r'EnergyKind\.(\w+)', body)
        d["kind"] = k.group(1) if k else "NONE"
        kinds[m.group(2)] = d
    return kinds

TITLES = {"jaw_crusher": "Щёковая дробилка", "washing_drum": "Промывочный барабан", "leaching_reactor": "Реактор выщелачивания",
          "steam_turbine": "Паровая турбина", "water_pump": "Водяной насос", "solar_panel_advanced": "Улучшенная солнечная панель",
          "carbon_capacitor": "Углеродный конденсатор", "settling_tank": "Отстойник", "acid_plant": "Завод серной кислоты"}

def render(name, d, show=None):
    show = show or {}
    W, H = 176, 184
    LEFT = 32
    g = Image.new("RGBA", (W + LEFT + 6, H + 6), (0, 0, 0, 0))
    ox, oy = LEFT, 3
    def P(im, x, y): g.alpha_composite(im, (ox + x, oy + y))
    tabslot = d["module"] or d["coating"]
    if tabslot:
        hh = 61 if d["cooler"] else 39 if d["module"] else 30
        P(nine(spr("holder"), 31, hh, 5), -27, 34)
    P(nine(spr("background"), W, H, 4), 0, 0)
    if tabslot:
        if d["module"]:
            P(spr("slot_module"), d["module"][0] - 1, d["module"][1] - 1)
            if show.get("module"): P(item(show["module"]), d["module"][0], d["module"][1])
        if d["coating"]:
            P(spr("slot_module"), d["coating"][0] - 1, d["coating"][1] - 1)
            if show.get("coating"): P(item(show["coating"]), d["coating"][0], d["coating"][1])
        if d["cooler"]:
            P(spr("slot_module"), d["cooler"][0] - 1, d["cooler"][1] - 1)
            if show.get("cooler"): P(item(show["cooler"]), d["cooler"][0], d["cooler"][1])
        if d["module"]:
            by = 34 + (49 if d["cooler"] else 27)
            P(nine(spr("gauge"), 18, 6, 1), -21, by)
            dr = ImageDraw.Draw(g)
            w = int(16 * show.get("heat", 0))
            if w: dr.rectangle([ox - 20, oy + by + 1, ox - 20 + w - 1, oy + by + 4], fill=(80, 220, 120) if w < 8 else (240, 190, 50))
    outs = [i for i, s in enumerate(d["slots"]) if s[2] == "OUTPUT"]
    for (x, y, role) in d["slots"]:
        P(spr("slot_in" if role in ("INPUT", "FUEL") else "slot_out"), x - 1, y - 1)
    for key, nm in show.get("items", {}).items():
        x, y, _ = d["slots"][key]
        P(item(nm), x, y)
    for r in [(8 + c * 18, 102 + rr * 18) for rr in range(3) for c in range(9)] + [(8 + c * 18, 160) for c in range(9)]:
        P(spr("slot"), r[0] - 1, r[1] - 1)
    if d["kind"] != "NONE":
        P(nine(spr("gauge"), 8, 56, 1), 160, 18)
        pw = show.get("power", 0.6); h = int(54 * pw)
        dr = ImageDraw.Draw(g)
        dr.rectangle([ox + 161, oy + 18 + 55 - h, ox + 166, oy + 18 + 54], fill=(217, 138, 30))
    for (x, y, out) in d["tanks"]:
        P(nine(spr("gauge"), 18, 52, 1), x, y)
        fill = show.get("tank_out" if out else "tank_in", 0.5)
        col = show.get("fluid_out" if out else "fluid_in", (60, 130, 210))
        h = int(50 * fill)
        ImageDraw.Draw(g).rectangle([ox + x + 1, oy + y + 51 - h, ox + x + 16, oy + y + 50], fill=col)
        P(spr("tank_overlay"), x + 1, y + 1)
    if d["arrow"]:
        P(spr("arrow_off"), *d["arrow"])
        P(spr("arrow_on").crop((0, 0, int(28 * show.get("progress", 0.5)), 8)), *d["arrow"])
    if d["flame"]:
        shape = ["......##......", ".....###......", ".....####.....", "....#####.#...", "...######.##..", "...#######.##.", "..##########.#", "..############", "..############", "..############", "...##########.", "...##########.", "....########..", ".....######..."]
        fl = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
        for y, row in enumerate(shape):
            for x, ch in enumerate(row):
                if ch == "#":
                    fl.putpixel((x, y), (56, 64, 80, 255) if y < 5 else (240, 150 + y * 4, 40, 255))
        P(fl, d["flame"][0], d["flame"][1])
    info_screen = not d["slots"] and not d["tanks"]
    if info_screen:
        P(nine(spr("gauge"), 128, 52, 1), 16, 20)
    P(nine(spr("gauge"), 160, 12, 1), 8, 78)
    g = g.resize((g.width * S, g.height * S), Image.NEAREST)
    dr = ImageDraw.Draw(g)
    def T(x, y, text, fill, font=FONT): dr.text(((ox + x) * S, (oy + y) * S), text, fill=fill, font=font)
    t = TITLES.get(name, name)
    tw = dr.textlength(t, font=FONT) / S
    T((W - tw) / 2, 5.5, t, (212, 222, 238, 255))
    T(8, 91.5, "Инвентарь", (140, 152, 172, 255))
    T(12, 79.5, show.get("status", "Работа"), (60, 254, 154, 255))
    if d["kind"] == "CONSUMER":
        T(112, 79.5, "-%s FE/т" % show.get("rate", 16), (156, 232, 196, 255))
    if info_screen:
        T(56, 26, show.get("big", "+96"), (60, 254, 154, 255), BIG)
        T(34, 49, "31 200 / 48 000 FE", (60, 254, 154, 255))
    if len(outs) >= 2:
        for n, i in enumerate(outs[:3]):
            x, y, _ = d["slots"][i]
            dr.text(((ox + x + 1) * S + 1, (oy + y + 1) * S), str(n + 1), fill=(232, 196, 106, 255), font=FONT_B)
    canvas = Image.new("RGBA", g.size, (70, 72, 80, 255))
    canvas.alpha_composite(g)
    return canvas

if __name__ == "__main__":
    kinds = parse()
    plans = [
        ("jaw_crusher", dict(module="module_industrial", cooler="radiator_copper", heat=0.45, progress=0.6, rate=29,
                             items={0: "iron_crushed_ore" if False else "copper_crushed_ore"})),
        ("washing_drum", dict(module="module_worker", heat=0.2, items={0: "copper_crushed_ore"}, fluid_in=(60, 130, 210), tank_in=0.7,
                              fluid_out=(110, 100, 70), tank_out=0.35, progress=0.4)),
        ("steam_turbine", dict(module="module_peak", cooler="radiator_aluminum", heat=0.8, kind="x", rate=0,
                               items={0: "graphite"}, tank_in=0.55)),
        ("water_pump", dict(tank_out=0.6, fluid_out=(60, 130, 210), rate=16)),
        ("solar_panel_advanced", dict(coating="coating_gold", big="+120")),
        ("carbon_capacitor", dict(big="65%")),
    ]
    tiles = []
    for name, show in plans:
        d = kinds[name]
        tiles.append(render(name, d, show))
    cols = 3
    tw, th = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (tw * cols, th * rows), (70, 72, 80, 255))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
    out = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/gui_mock4.png")
    sheet.convert("RGB").save(out)
    print(sheet.size)
