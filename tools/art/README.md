# Генератор текстур и моделей «Контура»

Python-скрипты, которые рисуют все текстуры, модели блоков и списки ресурсов мода (нужны Python 3.11+, `pip install pillow numpy`).

1. Один раз после клонирования: `python3 tools/art/set_root.py` (прописывает путь к вашей копии проекта).
2. Работать из папки `tools/art`; для воспроизводимых результатов запускать с `PYTHONHASHSEED=0`.
3. Собираемые машины (реактор, турбина, градирня, доменная печь):
   - модели описаны в `kontur_gen/assembly.py` (функции `fusion_reactor`, `turbine_hall`, `cooling_tower`, `blast_furnace`);
   - материалы граней - `kontur_gen/model3d.py` (`paint_face`) и обёртки в `kontur_gen/machines3d.py`;
   - проверка перекрытий и висящих деталей: `python3 chk4.py raw` (все) или с именем машины;
   - превью с двух сторон: `python3 prev_assembly.py out/имя.png имя 35 28 10` и `... 215 28 10` (последнее число - пикселей на единицу);
   - экспорт в ресурсы мода: `python3 export_assembly.py`, затем по порядку `make_assembled.py`, `make_plant.py`, `make_assembly_assets.py`, `lang_ports.py`;
   - проверки: `verify_assets.py`, `check_uv.py`, `check_progression.py`.
4. Не запускайте `generate_assets.py` целиком: он перезапишет вручную доведённые ресурсы.
5. Сборка мода: `./gradlew build` (Java 21, NeoForge 1.21.1); клиент для проверки: `./gradlew runClient`.
