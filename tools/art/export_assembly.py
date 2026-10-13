#!/usr/bin/env python3
"""Экспорт готовых моделей собираемых машин: клетки 16x16x16 (модель и атлас каждой), анимированный вариант, описание assembly/<id>.json."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kontur_gen import assembly as AS, model3d as M, multi as MU  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(os.environ.get("KONTUR_ROOT", "/home/user/TechnoGenesis"))
A = ROOT / "src/main/resources/assets/kontur"
TEX = A / "textures/block/assembly"
NS = "kontur"


def wj(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def model_json(els, tex):
    return {"render_type": "minecraft:translucent", "textures": {"particle": f"{NS}:block/machine_side", "0": f"{NS}:block/assembly/{tex}"},
            "elements": els}


def export(only):
    TEX.mkdir(parents=True, exist_ok=True)
    for mid, fn in AS.DESIGNS.items():
        if only and mid not in only:
            continue
        big = fn()
        parts = MU.slice_model(big)
        index = []
        for old in list(TEX.glob(f"{mid}_f*")) + list((A / "models/block").glob(f"{mid}_f*.json")):
            old.unlink()
        for idx, pm in sorted(parts.items()):
            if not pm.boxes:
                continue
            try:
                els, imgs_off, _ = M.build(pm)
            except ValueError:
                continue
            if not els:
                continue
            c, r, y = idx % big.w, (idx // big.w) % big.d, idx // (big.w * big.d)
            name = f"{mid}_f{idx}"
            imgs_off[0].save(TEX / f"{name}.png")
            wj(A / f"models/block/{name}.json", model_json(els, name))
            has_on = False
            _, imgs_on, _ = M.build(pm, frames=4)
            if any(im.tobytes() != imgs_off[0].tobytes() for im in imgs_on):
                strip = Image.new("RGBA", (pm.atlas, pm.atlas * 4))
                for i, im in enumerate(imgs_on):
                    strip.paste(im, (0, pm.atlas * i))
                strip.save(TEX / f"{name}_on.png")
                (TEX / f"{name}_on.png.mcmeta").write_text(json.dumps({"animation": {"frametime": 3}}, indent=2) + "\n")
                wj(A / f"models/block/{name}_on.json", model_json(els, f"{name}_on"))
                has_on = True
            index.append({"i": idx, "c": c, "r": r, "y": y, "on": has_on})
        wj(A / f"assembly/{mid}.json", {"w": big.w, "d": big.d, "h": big.h, "parts": index})
        print(f"{mid}: клеток {len(index)}, анимированных {sum(1 for p in index if p['on'])}")


if __name__ == "__main__":
    export(set(filter(None, os.environ.get("KONTUR_ONLY", "").split(","))))
