#!/usr/bin/env python3
"""Генератор ресурсов мода «Контур»: текстуры, модели, язык, рецепты, лут, теги, мир.

Запуск из корня репозитория:  python3 tools/generate_assets.py
Ванильные образцы текстур скачиваются в tools/.vanilla при первом запуске (нужны Pillow и numpy).
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kontur_gen import textures as T, designs as D, data as G, machines as M, rawore as RW  # noqa: E402
from kontur_gen.defs import *  # noqa: E402,F403

TEX_B = G.ASSETS / "textures/block"
TEX_I = G.ASSETS / "textures/item"


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not os.environ.get("FORCE_TEXTURES"):
        return
    img.save(path)


def save_anim(frames, path, frametime=3):
    from PIL import Image
    strip = Image.new("RGBA", (16, 16 * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, 16 * i))
    save(strip, path)
    if path.with_name(path.name + ".mcmeta").exists() and not os.environ.get("FORCE_TEXTURES"):
        return
    path.with_name(path.name + ".mcmeta").write_text(
        json.dumps({"animation": {"frametime": frametime}}, indent=2) + "\n")


def textures():
    # --- руды
    for m in MINERALS:
        save(D.ore_texture(m, "stone"), TEX_B / f"{m.ore_id}.png")
        save(D.ore_texture(m, "deepslate"), TEX_B / f"deepslate_{m.ore_id}.png")
        if m.nether:
            save(D.ore_texture(m, "nether"), TEX_B / f"nether_{m.ore_id}.png")
        save(RW.raw_texture(m), TEX_I / f"{m.raw_id}.png")
    # --- металлы
    for me in NEW_METALS:
        save(D.ingot_texture(me), TEX_I / f"{me.id}_ingot.png")
    for me in METALS:
        for form in ("crushed", "washed", "concentrate", "tailings", "fine", "wet", "cake", "precipitate"):
            name = {"crushed": "crushed_ore", "washed": "washed_ore", "concentrate": "concentrate",
                    "tailings": "tailings_r1", "fine": "fine_tailings", "wet": "wet_cake", "cake": "cake_r2",
                    "precipitate": "precipitate"}[form]
            save(T.form_texture(me, form), TEX_I / f"{me.id}_{name}.png")
    # --- прочие предметы
    save(T.gangue_texture(), TEX_I / "gangue.png")
    save(T.ash_texture(), TEX_I / "ash.png")
    save(T.sludge_texture(), TEX_I / "wet_sludge.png")
    save(T.mineral_fraction_texture(), TEX_I / "mineral_fraction.png")
    save(T.salt_texture(), TEX_I / "salt.png")
    save(T.sulfur_powder_texture(), TEX_I / "sulfur_powder.png")
    save(T.crushed_spodumene_texture(), TEX_I / "crushed_spodumene.png")
    save(T.graphite_texture(), TEX_I / "graphite.png")
    save(M.machine_frame_item(), TEX_I / "machine_frame.png")
    for fid, f in FLUIDS.items():
        save(T.bucket_texture(f["rgb"]), TEX_I / f"{fid}_bucket.png")
    # --- строительные блоки
    save(T.recolor(T.van("block/coarse_dirt"), [(78, 74, 72), (110, 105, 100), (140, 134, 128), (166, 160, 152)]),
         TEX_B / "ash_block.png")
    save(T.recolor(T.van("block/gravel"), [(66, 68, 72), (94, 97, 102), (122, 126, 132), (150, 154, 160)]),
         TEX_B / "aggregate_block.png")
    save(M.machine_side(), TEX_B / "machine_side.png")


def models_and_data():
    # блоки с простой кубической моделью
    for bid, r, e, m, kind in G.ore_blocks():
        G.simple_block(bid)
        G.loot_ore(bid, m)
    for bid in ("ash_block", "aggregate_block"):
        G.simple_block(bid)
        G.loot_self(bid)
    G.cable_models()
    for bid in list(G.MACHINES) + ["copper_wire"]:
        G.loot_self(bid)
    # предметы
    items = [m.raw_id for m in MINERALS] + [f"{m.id}_ingot" for m in NEW_METALS] + list(G.MISC_ITEMS)
    items += [f"{me.id}_{fid}" for me in METALS for fid, _, _ in G.FORMS]
    items += [f"{fid}_bucket" for fid in FLUIDS]
    for iid in items:
        G.wj(G.ASSETS / f"models/item/{iid}.json", G.item_generated(iid))
    # жидкости: блоки-жидкости
    for fid in FLUIDS:
        G.wj(G.ASSETS / f"models/block/{fid}.json", {"textures": {"particle": "minecraft:block/water_still"}})
        G.wj(G.ASSETS / f"blockstates/{fid}.json", {"variants": {"": {"model": G.rl(f"block/{fid}")}}})
    # язык
    ru, en = G.lang()
    G.wj(G.ASSETS / "lang/ru_ru.json", ru)
    G.wj(G.ASSETS / "lang/en_us.json", en)
    G.recipes()
    G.tags()
    G.worldgen()


if __name__ == "__main__":
    textures()
    models_and_data()
    print("Готово: ресурсы записаны в", G.RES)
