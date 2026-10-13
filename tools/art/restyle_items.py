"""Единый контур предметов: чёрная обводка (22,26,36) заменяется тёмным оттенком цвета соседней детали, как в Create."""
from pathlib import Path
from PIL import Image
ITEM = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/textures/item")
OLD = {(22, 26, 36), (22, 24, 31)}
changed = []
for f in sorted(ITEM.glob("*.png")):
    im = Image.open(f).convert("RGBA")
    if im.size != (16, 16):
        continue
    def edge(x, y):
        return any(not (0 <= x + dx < 16 and 0 <= y + dy < 16) or im.getpixel((x + dx, y + dy))[3] == 0
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    outs = [(x, y) for y in range(16) for x in range(16)
            if im.getpixel((x, y))[3] and im.getpixel((x, y))[:3] in OLD and edge(x, y)]
    if not outs:
        continue
    src = im.copy()
    for (x, y) in outs:
        cols = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < 16 and 0 <= n[1] < 16:
                p = src.getpixel(n)
                if p[3] and p[:3] not in OLD:
                    cols.append((p[:3], (dx, dy)))
        if not cols:
            continue
        r = sum(c[0][0] for c in cols) / len(cols)
        g = sum(c[0][1] for c in cols) / len(cols)
        b = sum(c[0][2] for c in cols) / len(cols)
        lit = any(d in ((1, 0), (0, 1)) for _, d in cols)       # деталь снизу-справа от контура -> контур светлее
        k = 0.5 if lit else 0.34
        im.putpixel((x, y), (int(r * k + 6), int(g * k * 0.96 + 6), int(b * k * 1.08 + 14), 255))
    im.save(f)
    changed.append(f.name)
print(len(changed), changed)
