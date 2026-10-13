import sys
sys.path.insert(0, ".")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import check_gui as C
SP = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/gui/sprites")
def spr(n): return Image.open(SP / f"{n}.png").convert("RGBA")
def nine(im, w, h, b):
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); W, H = im.size
    xs = [(0, b, 0, b), (b, W - b, b, w - b), (W - b, W, w - b, w)]
    ys = [(0, b, 0, b), (b, H - b, b, h - b), (H - b, H, h - b, h)]
    for (sx0, sx1, dx0, dx1) in xs:
        for (sy0, sy1, dy0, dy1) in ys:
            out.paste(im.crop((sx0, sy0, sx1, sy1)).resize((max(1, dx1 - dx0), max(1, dy1 - dy0)), 0), (dx0, dy0))
    return out
def tint(im, rgb):
    r, g, b = rgb; px = im.load(); o = im.copy(); q = o.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]; q[x, y] = (p[0]*r//255, p[1]*g//255, p[2]*b//255, p[3])
    return o
def paste(dst, im, x, y): dst.alpha_composite(im, (x, y))
def btn(c, x, y, w, h, rgb, down=False):
    paste(c, tint(nine(spr("button_down" if down else "button"), w, h, 2), rgb), x, y)
F = ImageFont.load_default()
def render(name, d, cfg=False, fluid=0.6, pwr=0.6):
    W, H = 176, 184
    canvas = Image.new("RGBA", (W + 60, H + 10), (70, 72, 80, 255))
    g = Image.new("RGBA", (W + 30, H), (0, 0, 0, 0))
    ox = 26
    paste(g, nine(spr("background"), W, H, 4), ox, 0)
    paste(g, nine(spr("holder"), 26, 26, 4), ox - 22, 34)
    paste(g, spr("slot_module"), ox - 18, 38)
    paste(g, nine(spr("gauge"), 18, 6, 1), ox - 18, 62); ImageDraw.Draw(g).rectangle([ox-17,63,ox-8,66], fill=(240,190,50))
    def sl(x, y, r="slot"): paste(g, spr(r), ox + x - 1, y - 1)
    for (x, y, role) in d["slots"]: sl(x, y, "slot_in" if role in ("INPUT","FUEL") else "slot_out")
    for r in [(8 + c * 18, 102 + rr * 18) for rr in range(3) for c in range(9)] + [(8 + c * 18, 160) for c in range(9)]: sl(*r)
    if d["energy"]:
        paste(g, nine(spr("gauge"), 8, 56, 1), ox + 160, 18)
        h = int(54 * pwr)
        ImageDraw.Draw(g).rectangle([ox+161, 18+55-h, ox+166, 18+54], fill=(217, 138, 30))
    for t in d["tanks"]:
        paste(g, nine(spr("gauge"), 18, 52, 1), ox + t[0], t[1])
        h = int(50 * fluid)
        ImageDraw.Draw(g).rectangle([ox+t[0]+1, t[1]+51-h, ox+t[0]+16, t[1]+50], fill=(60, 130, 210))
        paste(g, spr("tank_overlay"), ox + t[0] + 1, t[1] + 1)
    if d["arrow"]:
        paste(g, spr("arrow_off"), ox + d["arrow"][0], d["arrow"][1])
        paste(g, spr("arrow_on").crop((0, 0, 14, 8)), ox + d["arrow"][0], d["arrow"][1])
    if d["flame"]:
        paste(g, spr("flame_off"), ox + d["flame"][0], d["flame"][1])
        paste(g, spr("flame_on").crop((0, 5, 13, 13)), ox + d["flame"][0], d["flame"][1] + 5)
    if not d["slots"] and not d["tanks"]:
        paste(g, nine(spr("gauge"), 128, 52, 1), ox + 16, 20)
        ImageDraw.Draw(g).text((ox + 50, 28), "62%", fill=(60, 254, 154), font=F)
    paste(g, nine(spr("gauge"), 160, 12, 1), ox + 8, 78)
    dr = ImageDraw.Draw(g)
    dr.text((ox + 12, 80), "Running", fill=(60, 254, 154), font=F); dr.text((ox + 120, 80), "-16 FE/t", fill=(156, 232, 196), font=F)
    dr.text((ox + 60, 6), name, fill=(212, 222, 238), font=F); dr.text((ox + 8, 92), "Inventory", fill=(212, 222, 238), font=F)
    canvas.alpha_composite(g, (4, 5))
    return canvas
if __name__ == "__main__":
    kinds = C.parse()
    names = sys.argv[1:] or ["washing_drum", "settling_tank", "magnetic_separator", "solid_fuel_generator", "carbon_capacitor", "filter_press"]
    tiles = [render(n, kinds[n], cfg=(i == 0)) for i, n in enumerate(names)]
    cols = 3; rows = (len(tiles) + cols - 1) // cols
    tw, th = tiles[0].size
    sh = Image.new("RGBA", (tw * cols, th * rows), (70, 72, 80, 255))
    for i, t in enumerate(tiles): sh.paste(t, ((i % cols) * tw, (i // cols) * th))
    sh = sh.resize((sh.width * 2, sh.height * 2), 0)
    sh.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/gui_mock3.png")
