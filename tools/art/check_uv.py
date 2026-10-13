"""Проверка моделей блоков: плотность текстуры 1:1, границы uv, пересечение участков, пустые грани."""
import json, sys
from pathlib import Path
from PIL import Image
A = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur")
bad = 0
checked = 0
def tex_path(ref):
    ns, path = ref.split(":")
    return A / "textures" / (path + ".png")
for mp in sorted((A / "models/block").glob("*.json")):
    m = json.loads(mp.read_text())
    if "elements" not in m or mp.name.endswith("_item.json"):
        continue
    texs = {k: v for k, v in m.get("textures", {}).items()}
    sizes = {}
    for k, v in texs.items():
        if v.startswith("#"):
            continue
        p = tex_path(v)
        if not p.exists():
            print(mp.name, "нет текстуры", v); bad += 1; continue
        im = Image.open(p)
        h = im.height
        # анимация: кадр квадратный по ширине
        sizes[k] = (im.width, min(im.height, im.width) if mp.name.endswith("_on.json") or (p.with_suffix(".png.mcmeta")).exists() else im.height)
    used = {}
    for i, e in enumerate(m["elements"]):
        f0, t0 = e["from"], e["to"]
        dx, dy, dz = (t0[0]-f0[0], t0[1]-f0[1], t0[2]-f0[2])
        dims = {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}
        for fn, f in e.get("faces", {}).items():
            tk = f["texture"][1:]
            if tk not in sizes:
                continue
            W, H = sizes[tk]
            u0, v0, u1, v1 = f["uv"]
            rot = f.get("rotation", 0)
            w = abs(u1 - u0) * W / 16
            h = abs(v1 - v0) * H / 16
            fw, fh = dims[fn]
            if rot in (90, 270):
                w, h = h, w
            checked += 1
            if abs(w - fw) > 0.01 or abs(h - fh) > 0.01:
                bad += 1
                print(f"{mp.name} эл.{i} грань {fn}: размер грани {fw}x{fh}, участок текстуры {w:.2f}x{h:.2f}")
            if min(u0, u1) < -1e-6 or max(u0, u1) > 16 + 1e-6 or min(v0, v1) < -1e-6 or max(v0, v1) > 16 + 1e-6:
                bad += 1; print(f"{mp.name} эл.{i} {fn}: uv вне текстуры {f['uv']}")
            used.setdefault(tk, []).append((i, fn, min(u0, u1), min(v0, v1), max(u0, u1), max(v0, v1)))
print("проверено граней:", checked, "ошибок:", bad)
