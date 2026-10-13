#!/usr/bin/env python3
"""Экспорт объёмных моделей машин: JSON-модели, блокстейты, атласы текстур (в т.ч. анимированные)."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kontur_gen import machines3d as MM, model3d as M, multi as MU  # noqa: E402

ROOT = Path(os.environ.get("KONTUR_ROOT", "/home/user/TechnoGenesis"))
A = ROOT / "src/main/resources/assets/kontur"
ROT = {"north": 0, "east": 90, "south": 180, "west": 270}
NS = "kontur"


def wj(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def model_json(els, tex, glass):
    return {"parent": "minecraft:block/block", "render_type": "minecraft:translucent" if glass else "minecraft:cutout",
            "textures": {"particle": f"{NS}:block/machine_side", "0": f"{NS}:block/machine/{tex}"}, "elements": els}


def export_big(only):
    """Крупные машины: модель каждой клетки (с анимированным вариантом, если он отличается), общая предметная модель и
    мультипарт-блокстейт по направлению, номеру части и признаку работы."""
    from PIL import Image
    for mid, fn in MU.BIG.items():
        if only and mid not in only:
            continue
        big = fn()
        parts = MU.slice_model(big)
        tex_dir = A / "textures/block/machine"
        tex_dir.mkdir(parents=True, exist_ok=True)
        has_on = {}
        for idx, pm in parts.items():
            pid = f"{mid}_p{idx}"
            els, imgs_off, place = M.build(pm)
            imgs_off[0].save(tex_dir / f"{pid}.png")
            wj(A / f"models/block/{pid}.json", model_json(els, pid, pm.glass))
            has_on[idx] = False
            for old in (tex_dir / f"{pid}_on.png", tex_dir / f"{pid}_on.png.mcmeta", A / f"models/block/{pid}_on.json"):
                if old.exists():
                    old.unlink()
            if mid in MM.ANIMATED:
                _, imgs_on, _ = M.build(pm, frames=4)
                if any(im.tobytes() != imgs_off[0].tobytes() for im in imgs_on):
                    strip = Image.new("RGBA", (pm.atlas, pm.atlas * 4))
                    for i, im in enumerate(imgs_on):
                        strip.paste(im, (0, pm.atlas * i))
                    strip.save(tex_dir / f"{pid}_on.png")
                    (tex_dir / f"{pid}_on.png.mcmeta").write_text(
                        json.dumps({"animation": {"frametime": 5}}, indent=2) + "\n")
                    wj(A / f"models/block/{pid}_on.json", model_json(els, f"{pid}_on", pm.glass))
                    has_on[idx] = True
        # предметная модель: вся машина целиком, уменьшенная до одного блока
        k = 16.0 / max(big.X, big.Y, big.Z)
        off = ((16 - big.X * k) / 2, (16 - big.Y * k) / 2, (16 - big.Z * k) / 2)
        els, imgs, _ = M.build(big, scale=k, offset=off)
        imgs[0].save(tex_dir / f"{mid}_item.png")
        wj(A / f"models/block/{mid}_item.json", model_json(els, f"{mid}_item", big.glass))
        wj(A / f"models/item/{mid}.json", {"parent": f"{NS}:block/{mid}_item"})
        mp = []
        for f, y in ROT.items():
            for idx in parts:
                for act in ("false", "true"):
                    model = f"{NS}:block/{mid}_p{idx}" + ("_on" if act == "true" and has_on[idx] else "")
                    apply = {"model": model}
                    if y:
                        apply["y"] = y
                    when = {"facing": f, "part": str(idx)}
                    if mid != "solar_farm":
                        when["active"] = act
                    elif act == "true":
                        continue
                    mp.append({"when": when, "apply": apply})
        wj(A / f"blockstates/{mid}.json", {"multipart": mp})
        # старые одноблочные модели и текстуры больше не нужны
        for old in (A / f"models/block/{mid}.json", A / f"models/block/{mid}_on.json", tex_dir / f"{mid}.png",
                    tex_dir / f"{mid}_on.png", tex_dir / f"{mid}_on.png.mcmeta"):
            if old.exists():
                old.unlink()
        print(f"{mid}: частей {len(parts)}, анимированных {sum(has_on.values())}")


def main():
    only = set(filter(None, os.environ.get("KONTUR_ONLY", "").split(",")))
    export_big(only)
    for mid, fn in MM.ALL.items():
        if mid in MU.BIG:
            continue
        if only and mid not in only:
            continue
        if mid == "carbon_capacitor":
            base = fn(0)
            els, imgs, place = M.build(base)
            for lvl in range(6):
                m = fn(lvl)
                _, im, _ = M.build(m)
                (A / "textures/block/machine").mkdir(parents=True, exist_ok=True)
                im[0].save(A / f"textures/block/machine/{mid}_{lvl}.png")
                wj(A / f"models/block/{mid}_{lvl}.json", model_json(els, f"{mid}_{lvl}", base.glass))
            variants = {}
            for act in ("false", "true"):
                for lvl in range(6):
                    for f, y in ROT.items():
                        v = {"model": f"{NS}:block/{mid}_{lvl}"}
                        if y:
                            v["y"] = y
                        variants[f"active={act},charge={lvl},facing={f}"] = v
            wj(A / f"blockstates/{mid}.json", {"variants": variants})
            wj(A / f"models/item/{mid}.json", {"parent": f"{NS}:block/{mid}_0"})
            continue
        m = fn()
        anim = mid in MM.ANIMATED
        els, imgs_off, place = M.build(m)                       # состояние «выключена»
        (A / "textures/block/machine").mkdir(parents=True, exist_ok=True)
        imgs_off[0].save(A / f"textures/block/machine/{mid}.png")
        wj(A / f"models/block/{mid}.json", model_json(els, mid, m.glass))
        if anim:
            _, imgs_on, _ = M.build(m, frames=4)
            from PIL import Image
            strip = Image.new("RGBA", (m.atlas, m.atlas * 4))
            for i, im in enumerate(imgs_on):
                strip.paste(im, (0, m.atlas * i))
            strip.save(A / f"textures/block/machine/{mid}_on.png")
            (A / f"textures/block/machine/{mid}_on.png.mcmeta").write_text(
                json.dumps({"animation": {"frametime": 5}}, indent=2) + "\n")
            wj(A / f"models/block/{mid}_on.json", model_json(els, f"{mid}_on", m.glass))
        variants = {}
        for act in ("false", "true"):
            for lvl in range(6):
                for f, y in ROT.items():
                    model = f"{NS}:block/{mid}" + ("_on" if act == "true" and anim else "")
                    v = {"model": model}
                    if y:
                        v["y"] = y
                    variants[f"active={act},charge={lvl},facing={f}"] = v
        wj(A / f"blockstates/{mid}.json", {"variants": variants})
        wj(A / f"models/item/{mid}.json", {"parent": f"{NS}:block/{mid}_item" if mid == "wind_rotor" else f"{NS}:block/{mid}"})
    for mid, fn in MM.EXTRA.items():          # отдельные модели: вращающиеся части и предметная модель
        if only and not (only & {mid, mid.rsplit("_", 1)[0], mid.split("_")[0]}):
            continue
        m = fn()
        els, imgs, place = M.build(m)
        (A / "textures/block/machine").mkdir(parents=True, exist_ok=True)
        imgs[0].save(A / f"textures/block/machine/{mid}.png")
        wj(A / f"models/block/{mid}.json", model_json(els, mid, m.glass))
    if only:
        print("экспортировано:", ", ".join(sorted(only)))
        return
    # старые плоские текстуры машин больше не нужны
    for old in list((A / "textures/block").glob("*_front*.png")) + list((A / "textures/block").glob("*_front*.mcmeta")):
        old.unlink()
    for name in ("machine_bottom.png", "carbon_side.png"):
        p = A / "textures/block" / name
        if p.exists():
            p.unlink()
    for p in (A / "textures/block").glob("*_top.png"):
        p.unlink()
    print("экспортировано машин:", len(MM.ALL))


if __name__ == "__main__":
    main()
