import sys
sys.path.insert(0, ".")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import check_gui as C
SP = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/gui/sprites")
def spr(n): return Image.open(SP / f"{n}.png").convert("RGBA")
def nine(im, w, h, b):
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    W, H = im.size
    xs = [(0, b, 0, b), (b, W - b, b, w - b), (W - b, W, w - b, w)]
    ys = [(0, b, 0, b), (b, H - b, b, h - b), (H - b, H, h - b, h)]
    for (sx0, sx1, dx0, dx1) in xs:
        for (sy0, sy1, dy0, dy1) in ys:
            tile = im.crop((sx0, sy0, sx1, sy1)).resize((max(1, dx1 - dx0), max(1, dy1 - dy0)), 0)
            out.paste(tile, (dx0, dy0))
    return out
def paste(dst, im, x, y): dst.alpha_composite(im, (x, y))
def render(name, d, cfg=False):
    W, H = 176, 184
    canvas = Image.new("RGBA", (W + 60 + (150 if cfg else 0), H + 10), (70, 72, 80, 255))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste(g, nine(spr("background"), W, H, 4), 0, 0)
    paste(g, nine(spr("well"), 144, 56, 2), 24, 18)
    for (x, y, role) in d["slots"]: paste(g, spr("slot"), x - 1, y - 1)
    for r in [(8 + c * 18, 102 + rr * 18) for rr in range(3) for c in range(9)] + [(8 + c * 18, 160) for c in range(9)]:
        paste(g, spr("slot"), r[0] - 1, r[1] - 1)
    if d["energy"]:
        paste(g, nine(spr("display"), 12, 56, 2), 8, 18)
        f = spr("energy_fill"); h = int(54 * 0.62)
        paste(g, f.crop((0, 54 - h, 10, 54)), 9, 19 + 54 - h)
        paste(g, spr("energy_overlay"), 8, 18)
    for t in d["tanks"]:
        paste(g, nine(spr("display"), 16, 52, 2), t[0], t[1])
        fl = Image.new("RGBA", (14, 30), (60, 130, 200, 255)); paste(g, fl, t[0] + 1, t[1] + 51 - 30)
        paste(g, spr("tank_overlay"), t[0], t[1])
    if d["arrow"]:
        paste(g, spr("arrow_off"), d["arrow"][0], d["arrow"][1])
        paste(g, spr("arrow_on").crop((0, 0, 12, 16)), d["arrow"][0], d["arrow"][1])
    if d["flame"]:
        paste(g, spr("flame_off"), d["flame"][0], d["flame"][1])
        paste(g, spr("flame_on").crop((0, 5, 14, 14)), d["flame"][0], d["flame"][1] + 5)
    paste(g, nine(spr("display"), 160, 12, 2), 8, 78)
    dr = ImageDraw.Draw(g); f = ImageFont.load_default()
    dr.text((12, 80), "Работа", fill=(124, 224, 138), font=f)
    dr.text((60, 6), name, fill=(64, 64, 64), font=f); dr.text((8, 92), "Inventory", fill=(64, 64, 64), font=f)
    canvas.alpha_composite(g, (30, 5))
    paste(canvas, spr("tab_active"), 8, 11); paste(canvas, spr("icon_config"), 11, 15)
    if cfg:
        px0 = 30 + W + 2
        paste(canvas, nine(spr("background"), 144, 130, 4), px0, 5)
        for r in range(5):
            for c in range(3):
                paste(canvas, spr(["cell_none", "cell_input", "cell_output", "cell_all", "cell_input"][(r + c) % 5]), px0 + 60 + c * 26, 5 + 42 + r * 16)
        paste(canvas, spr("check_on"), px0 + 8, 5 + 128 - 40); paste(canvas, spr("check_off"), px0 + 8, 5 + 128 - 26)
    return canvas
if __name__ == "__main__":
    kinds = C.parse()
    names = sys.argv[1:] or ["washing_drum", "jaw_crusher"]
    tiles = [render(n, kinds[n], cfg=(i == 0)) for i, n in enumerate(names)]
    w = max(t.width for t in tiles); h = sum(t.height for t in tiles)
    sh = Image.new("RGBA", (w, h), (70, 72, 80, 255)); y = 0
    for t in tiles: sh.paste(t, (0, y)); y += t.height
    sh = sh.resize((sh.width * 3, sh.height * 3), 0)
    sh.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/gui_mock2.png")
