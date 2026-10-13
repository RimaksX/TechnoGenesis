"""Единый источник данных для генератора ресурсов мода «Контур».

Здесь описаны металлы, руды, цвета и названия. Java-код (enum Metal / Mineral)
должен совпадать с этими списками; сверяет их tools/verify_assets.py.
"""
from dataclasses import dataclass, field
from typing import Optional

MODID = "kontur"


def hexrgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def ramp(*stops):
    """Рампа цветов от самого тёмного к самому светлому."""
    return [hexrgb(s) for s in stops]


# ---------------------------------------------------------------- металлы

@dataclass
class Metal:
    id: str                 # идентификатор (aluminum)
    ru: str                 # название в именительном падеже (алюминий)
    en: str                 # английское название
    ru_adj: str             # прилагательное для слитка (Алюминиевый)
    ru_block: str           # название блока
    vanilla: bool = False   # железо/медь/золото
    ramp: Optional[list] = None
    block_base: str = "iron_block"   # какую ванильную текстуру блока перекрашивать
    tag: str = ""           # имя в тегах c:ingots/<tag>

    @property
    def ingot_id(self):
        return f"{self.id}_ingot"

    @property
    def raw_item(self):
        return {"iron": "minecraft:raw_iron", "copper": "minecraft:raw_copper",
                "gold": "minecraft:raw_gold"}.get(self.id)

    @property
    def ingot_item(self):
        if self.vanilla:
            return f"minecraft:{self.id}_ingot"
        return f"{MODID}:{self.id}_ingot"


METALS = [
    Metal("iron", "железо", "Iron", "Железный", "Железный блок", vanilla=True),
    Metal("copper", "медь", "Copper", "Медный", "Медный блок", vanilla=True),
    Metal("gold", "золото", "Gold", "Золотой", "Золотой блок", vanilla=True),
    Metal("aluminum", "алюминий", "Aluminum", "Алюминиевый", "Блок алюминия",
          ramp=ramp("#4b5865", "#7e8d9b", "#aebbc7", "#d3dde5", "#f2f7fa"), block_base="iron_block"),
    Metal("nickel", "никель", "Nickel", "Никелевый", "Блок никеля",
          ramp=ramp("#4e4833", "#7d7455", "#aca07a", "#d4c9a3", "#f3ebc9"), block_base="gold_block"),
    Metal("tungsten", "вольфрам", "Tungsten", "Вольфрамовый", "Блок вольфрама",
          ramp=ramp("#14161d", "#2a2e3a", "#444b5c", "#667086", "#8f99ad"), block_base="copper_block"),
    Metal("chromium", "хром", "Chromium", "Хромовый", "Блок хрома",
          ramp=ramp("#2f5565", "#4f8aa0", "#7bbad0", "#b3e3ef", "#effcff"), block_base="gold_block"),
    Metal("manganese", "марганец", "Manganese", "Марганцевый", "Блок марганца",
          ramp=ramp("#4a1d3e", "#7a2f66", "#a8528c", "#cf86b4", "#efbdd8"), block_base="copper_block"),
    Metal("cobalt", "кобальт", "Cobalt", "Кобальтовый", "Блок кобальта",
          ramp=ramp("#0e1f52", "#1a3a8a", "#2c5bc2", "#4f86e8", "#93bcff"), block_base="iron_block"),
    Metal("molybdenum", "молибден", "Molybdenum", "Молибденовый", "Блок молибдена",
          ramp=ramp("#2a3a2f", "#46604f", "#6a8b72", "#98b99e", "#cfe6d0"), block_base="copper_block"),
    Metal("titanium", "титан", "Titanium", "Титановый", "Блок титана",
          ramp=ramp("#3d3552", "#5f5580", "#8a7fb0", "#b7aedb", "#e3ddf5"), block_base="iron_block"),
]
METAL = {m.id: m for m in METALS}
NEW_METALS = [m for m in METALS if not m.vanilla]


# ---------------------------------------------------------------- руды

@dataclass
class Mineral:
    id: str
    ore_id: str
    ore_ru: str
    ore_en: str
    deep_ru: str
    raw_id: str
    raw_ru: str
    raw_en: str
    ramp: list
    mask: str               # ванильная руда, чья форма пятен берётся за основу
    flip: str = ""          # "h", "v", "t" - зеркалирование маски для разнообразия
    metal: Optional[str] = None   # конечный металл (None - не металл)
    product: Optional[str] = None  # для неметаллов: id продукта дробления
    tool: str = "stone"     # stone | iron | diamond
    hardness: float = 3.0
    xp: tuple = (0, 0)
    # генерация
    y_min: int = 0
    y_max: int = 64
    size: int = 8
    count: int = 6
    rarity: int = 0         # >0 - rarity_filter (1 из N чанков)
    biomes: tuple = ("#minecraft:is_overworld",)
    nether: bool = False
    drops: tuple = (1, 1)   # диапазон количества сырья


MINERALS = [
    Mineral("bauxite", "bauxite_ore", "Бокситовая руда", "Bauxite Ore", "Глубинная бокситовая руда",
            "raw_bauxite", "Необработанный боксит", "Raw Bauxite",
            ramp("#6b3a1e", "#a2561f", "#d27b2c", "#eaa24d", "#f6d28a"), "iron_ore", "",
            metal="aluminum", tool="stone", hardness=3.0,
            y_min=32, y_max=112, size=10, count=8,
            biomes=("#minecraft:is_hill", "#minecraft:is_savanna", "#minecraft:is_badlands", "#minecraft:is_jungle")),
    Mineral("garnierite", "garnierite_ore", "Гарниеритовая руда", "Garnierite Ore", "Глубинная гарниеритовая руда",
            "raw_garnierite", "Необработанный гарниерит", "Raw Garnierite",
            ramp("#1f4a2c", "#2f7a43", "#52a85a", "#8dd275", "#c7f0a0"), "copper_ore", "h",
            metal="nickel", tool="stone", hardness=3.0,
            y_min=-32, y_max=32, size=6, count=4, rarity=2),
    Mineral("wolframite", "wolframite_ore", "Вольфрамитовая руда", "Wolframite Ore", "Глубинная вольфрамитовая руда",
            "raw_wolframite", "Необработанный вольфрамит", "Raw Wolframite",
            ramp("#14110f", "#2a2420", "#453a33", "#6a5a4d", "#a08a73"), "redstone_ore", "",
            metal="tungsten", tool="iron", hardness=4.0,
            y_min=-56, y_max=8, size=4, count=3, rarity=3),
    Mineral("chromite", "chromite_ore", "Хромитовая руда", "Chromite Ore", "Глубинная хромитовая руда",
            "raw_chromite", "Необработанный хромит", "Raw Chromite",
            ramp("#0c1113", "#1c2629", "#31443f", "#5f8374", "#b4e0cc"), "lapis_ore", "v",
            metal="chromium", tool="iron", hardness=3.5,
            y_min=-24, y_max=48, size=6, count=3, rarity=2),
    Mineral("pyrolusite", "pyrolusite_ore", "Пиролюзитовая руда", "Pyrolusite Ore", "Глубинная пиролюзитовая руда",
            "raw_pyrolusite", "Необработанный пиролюзит", "Raw Pyrolusite",
            ramp("#0f1118", "#1b2030", "#2c3550", "#46557e", "#8da0cf"), "coal_ore", "h",
            metal="manganese", tool="stone", hardness=3.0,
            y_min=-48, y_max=32, size=9, count=6),
    Mineral("cobaltite", "cobaltite_ore", "Кобальтитовая руда", "Cobaltite Ore", "Глубинная кобальтитовая руда",
            "raw_cobaltite", "Необработанный кобальтит", "Raw Cobaltite",
            ramp("#4b1f3a", "#7e3366", "#b34f8f", "#e08ab8", "#ffd0ea"), "gold_ore", "v",
            metal="cobalt", tool="iron", hardness=4.0,
            y_min=-48, y_max=-8, size=4, count=3, rarity=3),
    Mineral("molybdenite", "molybdenite_ore", "Молибденитовая руда", "Molybdenite Ore", "Глубинная молибденитовая руда",
            "raw_molybdenite", "Необработанный молибденит", "Raw Molybdenite",
            ramp("#2d3438", "#4a5860", "#6f8590", "#a2bcc6", "#dcecf1"), "emerald_ore", "",
            metal="molybdenum", tool="iron", hardness=3.5,
            y_min=-32, y_max=32, size=5, count=3, rarity=2),
    Mineral("rutile", "rutile_ore", "Рутиловая руда", "Rutile Ore", "Глубинная рутиловая руда",
            "raw_rutile", "Необработанный рутил", "Raw Rutile",
            ramp("#2b0f12", "#531a1f", "#7e2a2c", "#a9473f", "#d98a6c"), "iron_ore", "t",
            metal="titanium", tool="iron", hardness=4.0,
            y_min=-8, y_max=48, size=6, count=3, rarity=2,
            biomes=("#minecraft:is_beach", "#minecraft:is_mountain", "#minecraft:is_taiga", "#minecraft:is_river")),
    Mineral("graphite", "graphite_ore", "Графитовая руда", "Graphite Ore", "Глубинная графитовая руда",
            "raw_graphite", "Необработанный графит", "Raw Graphite",
            ramp("#0b0b0e", "#1d1d23", "#33333d", "#6a6a7a", "#b8b8cc"), "coal_ore", "v",
            product="graphite", tool="stone", hardness=2.5, xp=(0, 2),
            y_min=-48, y_max=64, size=12, count=8, drops=(1, 1)),
    Mineral("halite", "halite_ore", "Галитовая руда", "Halite Ore", "Глубинная галитовая руда",
            "raw_halite", "Необработанный галит", "Raw Halite",
            ramp("#8d8794", "#b9b3c0", "#dcd6e0", "#f3eef6", "#ffffff"), "diamond_ore", "h",
            product="salt", tool="stone", hardness=2.0, xp=(0, 2),
            y_min=-16, y_max=48, size=10, count=6, drops=(2, 4)),
    Mineral("sulfur", "native_sulfur_ore", "Руда самородной серы", "Native Sulfur Ore", "Глубинная руда самородной серы",
            "raw_sulfur", "Самородная сера", "Native Sulfur",
            ramp("#6b5a00", "#a58c00", "#d9be12", "#f3e23a", "#fff98a"), "lapis_ore", "h",
            product="sulfur_powder", tool="stone", hardness=2.0, xp=(1, 3),
            y_min=8, y_max=96, size=7, count=5, nether=True, drops=(2, 4),
            biomes=("#minecraft:is_hill", "#minecraft:is_mountain", "#minecraft:is_badlands", "#minecraft:is_savanna")),
    Mineral("spodumene", "spodumene_ore", "Сподуменовая руда", "Spodumene Ore", "Глубинная сподуменовая руда",
            "raw_spodumene", "Необработанный сподумен", "Raw Spodumene",
            ramp("#6c4a6e", "#9a73a0", "#c49ac8", "#e6c8e8", "#fbeaf8"), "emerald_ore", "v",
            product="crushed_spodumene", tool="diamond", hardness=4.5, xp=(2, 5),
            y_min=-48, y_max=16, size=3, count=2, rarity=6),
]
MINERAL = {m.id: m for m in MINERALS}


# ---------------------------------------------------------------- прочее

# Цвета жидкостей (ARGB используется в Java; здесь RGB для вёдер)
FLUIDS = {
    "polluted_water": dict(ru="Загрязнённая вода", en="Polluted Water", rgb=hexrgb("#7a6a3a"),
                           bucket_ru="Ведро загрязнённой воды", bucket_en="Polluted Water Bucket"),
    "technical_water": dict(ru="Техническая вода", en="Technical Water", rgb=hexrgb("#4fb6c4"),
                            bucket_ru="Ведро технической воды", bucket_en="Technical Water Bucket"),
}

FLUIDS["sulfuric_acid"] = dict(ru="Серная кислота", en="Sulfuric Acid", rgb=hexrgb("#c9d94a"),
                               bucket_ru="Ведро серной кислоты", bucket_en="Sulfuric Acid Bucket")
FLUIDS["spent_acid"] = dict(ru="Отработанный раствор", en="Spent Solution", rgb=hexrgb("#7c7a3c"),
                            bucket_ru="Ведро отработанного раствора", bucket_en="Spent Solution Bucket")

# Растворы металлов (внутренние жидкости машин, без блока и ведра): цвет раствора
SOLUTION_RGB = {
    "iron": "#8fa05a", "copper": "#3a9ad9", "gold": "#e6c84a", "aluminum": "#bfd0e0", "nickel": "#5cb87a",
    "tungsten": "#6a6f8c", "chromium": "#4fa37a", "manganese": "#b25fb0", "cobalt": "#d45a78",
    "molybdenum": "#4a86c9", "titanium": "#b8a8e0",
}

# Параметры ступени ×2 (энергия и время должны совпадать с рецептами)
# дробилка 1200 FE/75 т, барабан 1000 FE/84 т, сепаратор 1800 FE/113 т = 4000 FE
STAGE2 = dict(
    crush=dict(energy=1200, time=75),
    wash=dict(energy=1000, time=84, water=250, polluted=200),
    separate=dict(energy=1800, time=113),
    settle=dict(energy=800, time=100, polluted=200, technical=160),
)

# Ступень ×3: суммарно 12 000 FE на единицу сырья (мельница 2000 + выщелачивание 3500 + фильтр-пресс 1500
# + осаждение 3000 + регенерация кислоты 2000). Завод кислоты считается отдельно.
STAGE3 = dict(
    mill=dict(energy=2000, time=63),
    leach=dict(energy=3500, time=110, acid=250, solution=250),
    press=dict(energy=1500, time=94, solution=50),
    precip=dict(energy=3000, time=94, solution=300, spent=300),
    regen=dict(energy=2000, time=32, spent=300, acid=200, salt_chance=0.25),
    acid=dict(energy=1600, time=50, water=500, acid=1000),
)
