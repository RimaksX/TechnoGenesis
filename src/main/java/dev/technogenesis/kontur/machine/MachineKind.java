package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.machine.MachineDefinition.EnergyKind;
import dev.technogenesis.kontur.machine.MachineDefinition.SlotRole;
import dev.technogenesis.kontur.registry.KonturRecipes;
import com.mojang.serialization.Codec;
import net.minecraft.util.StringRepresentable;

/** Виды машин ступени ×2 и энергетики. */
public enum MachineKind implements StringRepresentable {
    // Щёковая дробилка: 16 FE/t, руда -> дроблёная руда + щебень
    JAW_CRUSHER("jaw_crusher", true, false, KonturRecipes.CRUSHING, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 29, SlotRole.OUTPUT).slot(103, 47, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(66, 42).module(-21, 39).build()),
    // Промывочный барабан: 12 FE/t, 250 мБ воды на цикл
    WASHING_DRUM("washing_drum", true, false, KonturRecipes.WASHING, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).arrow(66, 42)
            .slot(101, 29, SlotRole.OUTPUT).slot(101, 47, SlotRole.OUTPUT).tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 1200, 48, 0, 12).module(-21, 39).build()),
    // Магнитно-плотностной сепаратор: 16 FE/t, промытая руда -> концентрат + хвосты R1 + фракция
    MAGNETIC_SEPARATOR("magnetic_separator", true, false, KonturRecipes.SEPARATING, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 20, SlotRole.OUTPUT).slot(103, 38, SlotRole.OUTPUT)
            .slot(103, 56, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(66, 42).module(-21, 39).build()),
    // Отстойник: загрязнённая вода -> техническая вода + осадок
    SETTLING_TANK("settling_tank", true, false, KonturRecipes.SETTLING, MachineDefinition.builder()
            .tank(36, 20, 4000, false).tank(106, 20, 4000, true).slot(72, 45, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(66, 30).module(-21, 39).build()),
    // Твердотопливный электрогенератор: 48 FE/t
    SOLID_FUEL_GENERATOR("solid_fuel_generator", true, false, null, MachineDefinition.builder()
            .slot(54, 29, SlotRole.FUEL).slot(90, 29, SlotRole.OUTPUT)
            .module(-21, 39)
            .energy(EnergyKind.GENERATOR, 24000, 0, 256, 48).flame(56, 50).build()),
    // Углеродный конденсатор: буфер ранней игры
    CARBON_CAPACITOR("carbon_capacitor", false, true, null, MachineDefinition.builder()
            .energy(EnergyKind.STORAGE, 400_000, 1024, 1024, 1024).build()),

    // ---- ступень ×3: химическое извлечение из хвостов R1
    // Роторная мельница хвостов: 32 FE/t, R1 -> тонкая смесь + минеральная фракция
    TAILINGS_MILL("tailings_mill", true, false, KonturRecipes.MILLING, MachineDefinition.builder()
            .slot(41, 38, SlotRole.INPUT).slot(103, 29, SlotRole.OUTPUT).slot(103, 47, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 3200, 128, 0, 32).arrow(66, 42).module(-21, 39).build()),
    // Завод серной кислоты: 32 FE/t, серный порошок + вода -> кислота
    ACID_PLANT("acid_plant", true, false, KonturRecipes.ACID_SYNTHESIS, MachineDefinition.builder()
            .tank(30, 20, 4000, false).slot(55, 38, SlotRole.INPUT).tank(112, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 128, 0, 32).arrow(78, 42).module(-21, 39).build()),
    // Реактор выщелачивания: 32 FE/t, тонкая смесь + кислота -> раствор металла + влажный кек
    LEACHING_REACTOR("leaching_reactor", true, false, KonturRecipes.LEACHING, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).slot(101, 38, SlotRole.OUTPUT)
            .tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 128, 0, 32).arrow(66, 42).module(-21, 39).build()),
    // Фильтр-пресс: 16 FE/t, влажный кек -> кек R2 + возвращённый раствор
    FILTER_PRESS("filter_press", true, false, KonturRecipes.FILTERING, MachineDefinition.builder()
            .slot(31, 38, SlotRole.INPUT).slot(89, 38, SlotRole.OUTPUT).tank(112, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(54, 42).module(-21, 39).build()),
    // Осадительный реактор: 32 FE/t, раствор + осадитель -> осадок металла + маточный раствор
    PRECIPITATION_REACTOR("precipitation_reactor", true, false, KonturRecipes.PRECIPITATION, MachineDefinition.builder()
            .tank(18, 20, 4000, false).slot(43, 38, SlotRole.INPUT).slot(101, 38, SlotRole.OUTPUT)
            .tank(124, 20, 4000, true)
            .energy(EnergyKind.CONSUMER, 3200, 128, 0, 32).arrow(66, 42).module(-21, 39).build()),
    // Колонна регенерации кислот: 64 FE/t, возвращает 200 мБ кислоты из 300 мБ отработанного раствора
    ACID_REGENERATION_COLUMN("acid_regeneration_column", true, false, KonturRecipes.ACID_REGENERATION,
            MachineDefinition.builder()
            .tank(36, 20, 4000, false).tank(106, 20, 4000, true).slot(72, 45, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 6400, 256, 0, 64).arrow(66, 30).module(-21, 39).build());

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

    public SideConfig defaultSides() {
        IoMode energy = switch (definition.energyKind) {
            case CONSUMER -> IoMode.INPUT;
            case GENERATOR -> IoMode.OUTPUT;
            case STORAGE -> IoMode.ALL;
        };
        return new SideConfig(IoMode.ALL, IoMode.ALL, energy);
    }
}
