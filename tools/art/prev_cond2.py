"""Точный предпросмотр кабелей и труб: блокстейт-поворот модели «на север» (текстура едет вместе с геометрией), поворот граней."""
import json, sys
import numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, '.')
from kontur_gen import preview3d as P
A = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur")
S = Path("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad")

NORM = {"north": (0,0,-1), "south": (0,0,1), "east": (1,0,0), "west": (-1,0,0), "up": (0,1,0), "down": (0,-1,0)}
def frame(name, a, b):
    d = b - a
    if name == "north": return np.array([b[0], b[1], a[2]]), (-1,0,0), (0,-1,0)
    if name == "south": return np.array([a[0], b[1], b[2]]), (1,0,0), (0,-1,0)
    if name == "east":  return np.array([b[0], b[1], b[2]]), (0,0,-1), (0,-1,0)
    if name == "west":  return np.array([a[0], b[1], a[2]]), (0,0,1), (0,-1,0)
    if name == "up":    return np.array([a[0], b[1], a[2]]), (1,0,0), (0,0,1)
    return np.array([a[0], a[1], b[2]]), (1,0,0), (0,0,-1)

def mat(rx, ry):
    def rx_m(t):  # MC x:t == матрица с углом -t
        t = np.radians(-t); c, s = np.cos(t), np.sin(t)
        return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    def ry_m(t):
        t = np.radians(-t); c, s = np.cos(t), np.sin(t)
        return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return ry_m(ry) @ rx_m(rx)

def rot_name(n, R):
    v = np.rint(R @ np.array(NORM[n])).astype(int)
    for k, w in NORM.items():
        if tuple(v) == w: return k

class FB:
    pass
class FM:
    def __init__(self): self.boxes = []

DIRS = {"north": (0,0), "east": (0,90), "south": (0,180), "west": (0,270), "up": (270,0), "down": (90,0)}

def build(id_, dirs):
    core = json.loads((A / f"models/block/{id_}_core.json").read_text())
    side = json.loads((A / f"models/block/{id_}_side.json").read_text())
    tex = core["textures"]["t"]
    img = Image.open(A / "textures" / (tex.split(":")[1] + ".png")).convert("RGBA")
    kx, ky = img.width / 16, img.height / 16
    model = FM(); place = {}
    jobs = [(e, (0,0)) for e in core["elements"]] + [(e, DIRS[d]) for d in dirs for e in side["elements"]]
    for bi, (e, (rx, ry)) in enumerate(jobs):
        R = mat(rx, ry)
        a0, b0 = np.array(e["from"], float), np.array(e["to"], float)
        c = np.array([8.0, 8.0, 8.0])
        pa, pb = R @ (a0 - c) + c, R @ (b0 - c) + c
        a, b = np.minimum(pa, pb), np.maximum(pa, pb)
        box = FB(); box.a, box.b, box.rot = list(a), list(b), None
        box.frames, box.frot, box.faces = {}, {}, []
        for fn, f in e["faces"].items():
            O, U, V = frame(fn, a0, b0)
            O2 = R @ (O - c) + c; U2 = R @ np.array(U); V2 = R @ np.array(V)
            g = rot_name(fn, R)
            box.faces.append(g)
            ext = b - a
            lu = abs(U2 @ ext); lv = abs(V2 @ ext)
            box.frames[g] = (O2, U2, V2, lu, lv)
            box.frot[g] = f.get("rotation", 0)
            u0, v0, u1, v1 = f["uv"]
            place[(bi, g)] = (int(round(min(u0,u1)*kx)), int(round(min(v0,v1)*ky)),
                              max(1, int(round(abs(u1-u0)*kx))), max(1, int(round(abs(v1-v0)*ky))))
        model.boxes.append(box)
    return model, img, place

if __name__ == "__main__":
    ids = sys.argv[2:]
    tiles = []
    for id_ in ids:
        for yaw in (35, 215):
            m, at, pl = build(id_, ("north", "south", "east", "west", "up", "down"))
            tiles.append(P.render(m, at, pl, yaw=yaw, pitch=28, px=10, bg=(70, 72, 78)))
    w, h = tiles[0].size
    sheet = Image.new("RGB", (w * 2, h * (len(tiles) // 2)))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * w, (i // 2) * h))
    sheet.save(S / sys.argv[1]); print(sheet.size)
