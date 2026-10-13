"""Проверка раскладки интерфейса машин по числам из MachineKind.java (без запуска игры):
все элементы в пределах своих областей, без наложений; макет-картинка для глаз."""
import re, sys
from PIL import Image, ImageDraw, ImageFont
SRC = open("/home/user/TechnoGenesis/src/main/java/dev/technogenesis/kontur/machine/MachineKind.java").read()
IMG_W, IMG_H = 176, 184
CONTENT = (8, 18, 144, 56)
ENERGY = (160, 18, 8, 56)
STATUS = (8, 78, 160, 12)
TITLE = (8, 6, 160, 9)
INVLBL = (8, 92, 160, 9)
INV_SLOTS = [(8 + c * 18, 102 + r * 18) for r in range(3) for c in range(9)] + [(8 + c * 18, 160) for c in range(9)]

def parse():
    kinds = {}
    for m in re.finditer(r'([A-Z_]+)\("([a-z_]+)",.*?MachineDefinition\.builder\(\)(.*?)\.build\(\)\)[,;]', SRC, re.S):
        body = m.group(3)
        d = dict(slots=[], tanks=[], arrow=None, flame=None, energy=("energy" in body))
        for s in re.finditer(r'\.slot\((\d+), (\d+), SlotRole\.(\w+)\)', body):
            d["slots"].append((int(s.group(1)), int(s.group(2)), s.group(3)))
        for t in re.finditer(r'\.tank\((\d+), (\d+), (\d+), (true|false)\)', body):
            d["tanks"].append((int(t.group(1)), int(t.group(2)), 18, 52))
        a = re.search(r'\.arrow\((\d+), (\d+)\)', body)
        if a: d["arrow"] = (int(a.group(1)), int(a.group(2)), 28, 8)
        f = re.search(r'\.flame\((\d+), (\d+)\)', body)
        if f: d["flame"] = (int(f.group(1)), int(f.group(2)), 14, 14)
        kinds[m.group(2)] = d
    return kinds

def inside(r, box):
    return r[0] >= box[0] and r[1] >= box[1] and r[0] + r[2] <= box[0] + box[2] and r[1] + r[3] <= box[1] + box[3]

def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

def check(name, d):
    errs = []
    items = []
    for (x, y, role) in d["slots"]:
        items.append((f"слот({x},{y})", (x - 1, y - 1, 18, 18)))
    for i, t in enumerate(d["tanks"]):
        items.append((f"бак{i}", t))
    if d["arrow"]: items.append(("стрелка", d["arrow"]))
    if d["flame"]: items.append(("пламя", d["flame"]))
    # при кликах и подсказках ограничиваем рабочей областью (внутри рамки 1 пикселя)
    inner = CONTENT
    for n, r in items:
        if not inside(r, inner):
            errs.append(f"{name}: {n} {r} вне рабочей области {inner}")
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if overlap(items[i][1], items[j][1]):
                errs.append(f"{name}: {items[i][0]} и {items[j][0]} пересекаются")
    # области панели не пересекаются между собой
    zones = [("энергия", ENERGY), ("рабочая область", CONTENT), ("статус", STATUS), ("заголовок", TITLE), ("подпись инвентаря", INVLBL)]
    for i in range(len(zones)):
        for j in range(i + 1, len(zones)):
            if overlap(zones[i][1], zones[j][1]):
                errs.append(f"зоны {zones[i][0]} и {zones[j][0]} пересекаются")
    for (x, y) in INV_SLOTS:
        r = (x - 1, y - 1, 18, 18)
        if not inside(r, (0, 0, IMG_W, IMG_H)):
            errs.append(f"слот инвентаря {x},{y} вне окна")
        for n, z in zones:
            if overlap(r, z):
                errs.append(f"слот инвентаря {x},{y} задевает зону {n}")
    # порядок слотов: вход, затем выходы (логика машин зависит от индексов)
    return errs, items

def mock(name, d, path):
    S = 4
    im = Image.new("RGB", (IMG_W * S, IMG_H * S), (198, 198, 198))
    dr = ImageDraw.Draw(im)
    def box(r, fill=None, outline=None):
        dr.rectangle([r[0]*S, r[1]*S, (r[0]+r[2])*S-1, (r[1]+r[3])*S-1], fill=fill, outline=outline)
    box(CONTENT, (139, 139, 139), (55, 55, 55))
    box(ENERGY, (30, 30, 30), (55, 55, 55))
    box(STATUS, (30, 30, 30), (55, 55, 55))
    for (x, y, role) in d["slots"]:
        box((x-1, y-1, 18, 18), (139, 139, 139), (55, 55, 55))
    for t in d["tanks"]:
        box(t, (30, 30, 30), (55, 55, 55))
    if d["arrow"]: box(d["arrow"], (90, 90, 90))
    if d["flame"]: box(d["flame"], (200, 120, 40))
    for (x, y) in INV_SLOTS:
        box((x-1, y-1, 18, 18), (139, 139, 139), (55, 55, 55))
    f = ImageFont.load_default()
    dr.text((60*S, 6*S), name, fill=(40,40,40), font=f)
    dr.text((8*S, 92*S), "Inventory", fill=(40,40,40), font=f)
    dr.text((12*S, 80*S), "status ...", fill=(124,224,138), font=f)
    im.save(path)

if __name__ == "__main__":
    kinds = parse()
    allerr = []
    for n, d in kinds.items():
        e, _ = check(n, d)
        allerr += e
    print("машин:", len(kinds))
    for e in allerr: print(" -", e)
    print("ОШИБОК:", len(allerr))
    names = ["washing_drum", "magnetic_separator", "settling_tank", "solid_fuel_generator", "carbon_capacitor", "filter_press"]
    sheet = Image.new("RGB", (IMG_W * 4 * 3, IMG_H * 4 * 2), (60, 60, 66))
    for i, n in enumerate(names):
        mock(n, kinds[n], "/tmp/m.png")
        t = Image.open("/tmp/m.png"); sheet.paste(t, ((i % 3) * IMG_W * 4, (i // 3) * IMG_H * 4))
    sheet.save("/tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/gui_mock.png")
