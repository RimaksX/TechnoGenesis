"""Последний шаг: тексты схем собираемых машин с чёткими местами портов (перекрывает старые из make_*)."""
import json
from pathlib import Path
A = Path("/home/user/TechnoGenesis/src/main/resources/assets/kontur/lang")
ru = {
 "tooltip.kontur.machine.fusion_reactor": "Собирается из корпуса: коробка 5×5×4 с пустой камерой 3×3×2, контроллер в центре передней стенки на втором ряду. Шесть портов на строго заданных местах (их показывает проекция): питание, вода, пар, водород, плазма, литиевый стержень. Горение требует водород, плазму, воду и стержень (5 минут). 8000 FE/т",
 "tooltip.kontur.machine.blast_furnace": "Собирается из корпуса печи: башня 5×5×6 с шахтой 3×3×4, контроллер в центре передней стенки на втором ряду. Четыре порта на заданных местах: питание, летка (выход), газ (кислород), загрузка сверху. 8 железа, 2 графита и кислород дают 10 стали",
 "tooltip.kontur.machine.turbine_hall": "Собирается из корпуса турбины: коробка 3×7×3, в тоннель 1×5×1 ставятся пять блоков ротора, контроллер в центре передней стенки. Три порта на заданных местах: пар сверху над высоким давлением, конденсат справа внизу, ток сзади. Пар даёт до 12 800 FE/т (80 FE на мБ, до 160 мБ/т). С ключом в руке видна проекция недостающих блоков, а по щелчку ключа машина принимает готовый вид",
 "tooltip.kontur.machine.cooling_tower": "Собирается из корпуса градирни: секция 5×3×3 с воздушным каналом 3×1×1, контроллер в центре передней стенки. Три порта на заданных местах: конденсат слева внизу, вода справа внизу, питание спереди справа внизу. Остужает конденсат до воды (95%, до 200 мБ/т), вентиляторы берут 150 FE/т",
 "message.kontur.assembly_ready": "Схема собрана: щёлкните по контроллеру ключом, и машина примет готовый вид",
 "message.kontur.assembly_problem": "Не собрано: неверных блоков %s. Первый: %s вправо, %s вглубь, %s вверх от контроллера. Порты стоят только на своих местах (жёлтые кубы проекции), на остальных местах стенки - корпус",
}
en = {
 "tooltip.kontur.machine.fusion_reactor": "Built from casing: a 5x5x4 box with an empty 3x3x2 chamber, the controller in the middle of the front wall on the second row. Six ports at fixed places (the projection shows them): power, water, steam, hydrogen, plasma, lithium rod. Burning needs hydrogen, plasma, water and a rod (5 minutes). 8000 FE/t",
 "tooltip.kontur.machine.blast_furnace": "Built from furnace casing: a 5x5x6 tower with a 3x3x4 shaft, the controller in the middle of the front wall on the second row. Four ports at fixed places: power, tap hole (output), gas (oxygen), charge from above. 8 iron, 2 graphite and oxygen make 10 steel",
 "tooltip.kontur.machine.turbine_hall": "Built from turbine casing: a 3x7x3 box, five rotor blocks go into the 1x5x1 tunnel, the controller in the middle of the front wall. Three ports at fixed places: steam on top over the high-pressure casing, condensate bottom right, power at the back. Steam gives up to 12,800 FE/t (80 FE per mB, up to 160 mB/t). With the wrench in hand you see a projection of the missing blocks, and a wrench click gives the finished look",
 "tooltip.kontur.machine.cooling_tower": "Built from cooling tower casing: a 5x3x3 section with a 3x1x1 air duct, the controller in the middle of the front wall. Three ports at fixed places: condensate bottom left, water bottom right, power front bottom right. Cools condensate to water (95%, up to 200 mB/t), the fans take 150 FE/t",
 "message.kontur.assembly_ready": "Structure complete: click the controller with the wrench and the machine takes its finished look",
 "message.kontur.assembly_problem": "Incomplete: %s wrong blocks. First: %s right, %s deep, %s up from the controller. Ports sit only at their own places (yellow cubes of the projection), the rest of the wall is casing",
}
for f, tbl in (("ru_ru.json", ru), ("en_us.json", en)):
    p = A / f
    d = json.loads(p.read_text(encoding="utf8"))
    d.update(tbl)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print("lang ok")
