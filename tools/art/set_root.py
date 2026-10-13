#!/usr/bin/env python3
"""Один раз после клонирования: прописывает в скриптах путь к вашей копии проекта вместо /home/user/TechnoGenesis.
Запуск: python3 tools/art/set_root.py  (из любого места)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
OLD = "/home/user/TechnoGenesis"
n = 0
for p in list(TOOLS.rglob("*.py")) + list(TOOLS.rglob("*.sh")):
    if p.name == "set_root.py":
        continue
    s = p.read_text(encoding="utf-8")
    t = s.replace(OLD, ROOT.as_posix())
    t = re.sub(r"/tmp/claude-0/[^\"' )]*/scratchpad/out", (TOOLS / "out").as_posix(), t)
    t = re.sub(r"/tmp/claude-0/[^\"' )]*/scratchpad/art_tools", TOOLS.as_posix(), t)
    if t != s:
        p.write_text(t, encoding="utf-8")
        n += 1
(TOOLS / "out").mkdir(exist_ok=True)
print(f"путь к проекту: {ROOT}; изменено файлов: {n}")
