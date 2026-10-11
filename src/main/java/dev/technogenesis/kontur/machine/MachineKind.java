package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.machine.MachineDefinition.EnergyKind;
import dev.technogenesis.kontur.machine.MachineDefinition.SlotRole;
import dev.technogenesis.kontur.registry.KonturRecipes;
import com.mojang.serialization.Codec;
import net.minecraft.util.StringRepresentable;

/** Виды машин ступеней ×2, ×3, ×5, ×8 и энергетики. */
public enum MachineKind implements StringRepresentable {
    // Щёковая дробилка: 16 FE/t, руда -> дроблёная руда + щебень
    JAW_CRUSHER("jaw_crusher", true, false, KonturRecipes.CRUSHING, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 29, SlotRole.OUTPUT).slot(103, 47, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 96, 0, 16).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Промывочный барабан: 12 FE/t, 250 мБ воды на цикл
    WASHING_DRUM("washing_drum", true, false, KonturRecipes.WASHING, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).arrow(66, 42)
            .slot(101, 29, SlotRole.OUTPUT).slot(101, 47, SlotRole.OUTPUT).tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 1200, 72, 0, 12).module(-20, 41).cooler(-20, 63).build()),
    // Магнитно-плотностной сепаратор: 16 FE/t, промытая руда -> концентрат + рудный остаток + фракция
    MAGNETIC_SEPARATOR("magnetic_separator", true, false, KonturRecipes.SEPARATING, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 20, SlotRole.OUTPUT).slot(103, 38, SlotRole.OUTPUT)
            .slot(103, 56, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 96, 0, 16).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Отстойник: загрязнённая вода -> техническая вода + осадок
    SETTLING_TANK("settling_tank", true, false, KonturRecipes.SETTLING, MachineDefinition.builder()
            .tank(36, 20, 4000, false).tank(106, 20, 4000, true).slot(72, 45, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 96, 0, 16).arrow(66, 30).module(-20, 41).cooler(-20, 63).build()),
    // Твердотопливный электрогенератор: 128 FE/t
    SOLID_FUEL_GENERATOR("solid_fuel_generator", true, false, null, MachineDefinition.builder()
            .slot(54, 29, SlotRole.FUEL).slot(90, 29, SlotRole.OUTPUT)
            .module(-20, 41).cooler(-20, 63)
            .energy(EnergyKind.GENERATOR, 48000, 0, 512, 128).flame(56, 50).build()),
    // Углеродный конденсатор: буфер ранней игры
    CARBON_CAPACITOR("carbon_capacitor", false, true, null, MachineDefinition.builder()
            .energy(EnergyKind.STORAGE, 1_200_000, 3072, 3072, 3072).build()),

    // ---- ступень ×3 «Химическая переработка»: химическое извлечение из рудного остатка
    // Роторная мельница остатков: 32 FE/t, рудный остаток -> рудная пыль + минеральная фракция
    TAILINGS_MILL("tailings_mill", true, false, KonturRecipes.MILLING, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 29, SlotRole.OUTPUT).slot(103, 47, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 3200, 192, 0, 32).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Завод серной кислоты: 32 FE/t, серный порошок + вода -> кислота
    ACID_PLANT("acid_plant", true, false, KonturRecipes.ACID_SYNTHESIS, MachineDefinition.builder()
            .tank(30, 20, 4000, false).slot(55, 38, SlotRole.INPUT).tank(112, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 192, 0, 32).arrow(78, 42).module(-20, 41).cooler(-20, 63).build()),
    // Реактор выщелачивания: 32 FE/t, рудная пыль + кислота -> раствор металла + кислотная масса
    LEACHING_REACTOR("leaching_reactor", true, false, KonturRecipes.LEACHING, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).slot(101, 38, SlotRole.OUTPUT)
            .tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 192, 0, 32).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Фильтр-пресс: 16 FE/t, кислотная масса -> сухой остаток + возвращённый раствор
    FILTER_PRESS("filter_press", true, false, KonturRecipes.FILTERING, MachineDefinition.builder()
            .slot(31, 38, SlotRole.INPUT).slot(89, 38, SlotRole.OUTPUT).tank(112, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 1600, 96, 0, 16).arrow(54, 42).module(-20, 41).cooler(-20, 63).build()),
    // Осадительный реактор: 32 FE/t, раствор + осадитель -> осадок металла + маточный раствор
    PRECIPITATION_REACTOR("precipitation_reactor", true, false, KonturRecipes.PRECIPITATION, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).slot(101, 38, SlotRole.OUTPUT)
            .tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 192, 0, 32).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Колонна регенерации кислот: 64 FE/t, возвращает 200 мБ кислоты из 300 мБ отработанного раствора
    ACID_REGENERATION_COLUMN("acid_regeneration_column", true, false, KonturRecipes.ACID_REGENERATION,
            MachineDefinition.builder()
            .tank(36, 20, 4000, false).tank(106, 20, 4000, true).slot(72, 45, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 6400, 384, 0, 64).arrow(66, 30).module(-20, 41).cooler(-20, 63).build()),

    // ---- ступень ×5 «Глубокая переработка»: экстракция, электролиз, регенерация растворителя (из сухого остатка)
    // Экстрактор: 64 FE/t, сухой остаток + растворитель -> насыщенный растворитель + отходы
    EXTRACTOR("extractor", true, false, KonturRecipes.EXTRACTION, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).slot(101, 38, SlotRole.OUTPUT)
            .tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 6400, 384, 0, 64).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Электролизёр: 144 FE/t, насыщенный растворитель -> два слитка + отработанный растворитель
    ELECTROLYZER("electrolyzer", true, false, KonturRecipes.ELECTROLYSIS, MachineDefinition.builder()
            .tank(36, 20, 4000, false).tank(106, 20, 4000, true).slot(72, 45, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 14400, 864, 0, 144).arrow(66, 30).module(-20, 41).cooler(-20, 63).build()),
    // Регенератор растворителя: 64 FE/t, возвращает 400 мБ растворителя из 500 мБ отработанного
    SOLVENT_REGENERATOR("solvent_regenerator", true, false, KonturRecipes.SOLVENT_REGENERATION,
            MachineDefinition.builder()
            .tank(36, 20, 4000, false).tank(106, 20, 4000, true).slot(72, 45, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 6400, 384, 0, 64).arrow(66, 30).module(-20, 41).cooler(-20, 63).build()),

    // ---- ступень ×8 «Переработка под давлением»: аттритор, парогенератор, автоклав
    // Аттритор: 120 FE/t, твёрдый шлак -> шлаковая пыль (сверхтонкое измельчение)
    ATTRITOR("attritor", true, false, KonturRecipes.ATTRITION, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 38, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 12000, 720, 0, 120).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),
    // Парогенератор: 32 FE/t, уголь + вода -> пар (внутренняя жидкость)
    STEAM_GENERATOR("steam_generator", true, false, KonturRecipes.STEAM_GENERATION, MachineDefinition.builder()
            .tank(30, 20, 4000, false).slot(55, 38, SlotRole.INPUT).tank(112, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 192, 0, 32).arrow(78, 42).module(-20, 41).cooler(-20, 63).build()),
    // Автоклав: 240 FE/t, шлаковая пыль + пар под давлением -> три слитка
    AUTOCLAVE("autoclave", true, false, KonturRecipes.AUTOCLAVING, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).slot(101, 38, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 24000, 1440, 0, 240).arrow(66, 42).module(-20, 41).cooler(-20, 63).build()),

    // ---- энергетика: возобновляемые источники и паровая турбина
    // Ветряной ротор: 24..96 FE/t, растёт с высотой и в непогоду; нужны открытое небо и свободные бока
    WIND_ROTOR("wind_rotor", true, false, null, MachineDefinition.builder()
            .energy(EnergyKind.GENERATOR, 24000, 0, 384, 96).build()),
    // Тепловой генератор: лава снизу, вода сбоку; 120 FE/t на каждую водяную сторону, до 480
    THERMAL_GENERATOR("thermal_generator", true, false, null, MachineDefinition.builder()
            .energy(EnergyKind.GENERATOR, 48000, 0, 768, 480).build()),
    // Паровая турбина: вода и топливо; 384 FE/t
    STEAM_TURBINE("steam_turbine", true, false, null, MachineDefinition.builder()
            .tank(40, 20, 4000, false).slot(73, 29, SlotRole.FUEL).slot(105, 29, SlotRole.OUTPUT).module(-20, 41).cooler(-20, 63)
            .energy(EnergyKind.GENERATOR, 96000, 0, 1536, 384).flame(75, 50).build()),
    // Водяной насос: 16 FE/t, 20 мБ воды за тик из источника рядом; вода не заканчивается
    WATER_PUMP("water_pump", true, false, null, MachineDefinition.builder()
            .tank(79, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 1600, 96, 0, 16).build()),
    // Солнечные панели: пик при ясном небе днём; нужны чистое небо над панелью и дневной свет
    SOLAR_PANEL("solar_panel", true, false, null, MachineDefinition.builder()
            .energy(EnergyKind.GENERATOR, 12000, 0, 192, 24).build()),
    SOLAR_PANEL_ADVANCED("solar_panel_advanced", true, false, null, MachineDefinition.builder()
            .coating(-20, 41).energy(EnergyKind.GENERATOR, 48000, 0, 768, 120).build()),
    // Солнечная ферма 3x2: шесть плиток, одна энергосистема
    SOLAR_FARM("solar_farm", true, false, null, MachineDefinition.builder()
            .coating(-20, 41).energy(EnergyKind.GENERATOR, 192000, 0, 3072, 720).build()),
    // Автоматический шахтёр: 160 FE/t при работе, 60 FE/t в движении; 12 слотов буфера добычи, склад наконечников снаружи
    MINER("miner", true, false, null, MachineDefinition.builder()
            .slot(44, 22, SlotRole.OUTPUT).slot(62, 22, SlotRole.OUTPUT).slot(80, 22, SlotRole.OUTPUT)
            .slot(98, 22, SlotRole.OUTPUT).slot(116, 22, SlotRole.OUTPUT).slot(134, 22, SlotRole.OUTPUT)
            .slot(44, 40, SlotRole.OUTPUT).slot(62, 40, SlotRole.OUTPUT).slot(80, 40, SlotRole.OUTPUT)
            .slot(98, 40, SlotRole.OUTPUT).slot(116, 40, SlotRole.OUTPUT).slot(134, 40, SlotRole.OUTPUT)
            .singleOutputChannel().module(-20, 41).cooler(-20, 63)
            .energy(EnergyKind.CONSUMER, 32000, 960, 0, 160).build());

    public static final Codec<MachineKind> CODEC = StringRepresentable.fromEnum(MachineKind::values);

    public final String id;
    public final boolean hasActive;
    public final boolean hasCharge;
    public final KonturRecipes.Kind recipeKind;
    public final MachineDefinition definition;

    MachineKind(String id, boolean hasActive, boolean hasCharge, KonturRecipes.Kind recipeKind,
                MachineDefinition definition) {
        this.id = id;
        this.hasActive = hasActive;
        this.hasCharge = hasCharge;
        this.recipeKind = recipeKind;
        this.definition = definition;
    }

    @Override
    public String getSerializedName() {
        return id;
    }

    /** Нарисован ли на модели разъём с этой стороны (ферма не имеет разъёмов, у панелей нет верхнего). */
    public boolean hasPort(RelativeSide side) {
        if (side == RelativeSide.FRONT || this == SOLAR_FARM) {
            return false;
        }
        if (this == WATER_PUMP && side == RelativeSide.BOTTOM) {
            return false;   // снизу водозабор, а не разъём
        }
        return !(side == RelativeSide.TOP && (this == SOLAR_PANEL || this == SOLAR_PANEL_ADVANCED));
    }

    /** Ступень переработки: ключ названия в языковом файле (x2 «Обогащение», x3 «Химическая переработка», x5 «Глубокая переработка»). */
    public String stage() {
        return switch (this) {
            case JAW_CRUSHER, WASHING_DRUM, MAGNETIC_SEPARATOR, SETTLING_TANK -> "x2";
            case TAILINGS_MILL, ACID_PLANT, LEACHING_REACTOR, FILTER_PRESS, PRECIPITATION_REACTOR,
                 ACID_REGENERATION_COLUMN -> "x3";
            case EXTRACTOR, ELECTROLYZER, SOLVENT_REGENERATOR -> "x5";
            case ATTRITOR, STEAM_GENERATOR, AUTOCLAVE -> "x8";
            case MINER -> "mining";
            default -> "power";
        };
    }

    public SideConfig defaultSides() {
        IoMode energy = switch (definition.energyKind) {
            case CONSUMER -> IoMode.INPUT;
            case GENERATOR -> IoMode.OUTPUT;
            case STORAGE -> IoMode.ALL;
        };
        return new SideConfig(IoMode.ALL, definition.defaultFluidMode(), energy);
    }
}
