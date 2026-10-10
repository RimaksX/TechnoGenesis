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
            .slot(44, 35, SlotRole.INPUT).slot(110, 26, SlotRole.OUTPUT).slot(110, 46, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(70, 35).build()),
    // Промывочный барабан: 12 FE/t, 250 мБ воды на цикл
    WASHING_DRUM("washing_drum", true, false, KonturRecipes.WASHING, MachineDefinition.builder()
            .tank(28, 17, 4000, false).slot(54, 35, SlotRole.INPUT)
            .slot(116, 26, SlotRole.OUTPUT).slot(116, 46, SlotRole.OUTPUT).tank(142, 17, 4000, true)
            .energy(EnergyKind.CONSUMER, 1200, 48, 0, 12).arrow(80, 35).build()),
    // Магнитно-плотностной сепаратор: 16 FE/t, промытая руда -> концентрат + хвосты R1 + фракция
    MAGNETIC_SEPARATOR("magnetic_separator", true, false, KonturRecipes.SEPARATING, MachineDefinition.builder()
            .slot(50, 35, SlotRole.INPUT).slot(116, 17, SlotRole.OUTPUT).slot(116, 35, SlotRole.OUTPUT)
            .slot(116, 53, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(76, 35).build()),
    // Отстойник: загрязнённая вода -> техническая вода + осадок
    SETTLING_TANK("settling_tank", true, false, KonturRecipes.SETTLING, MachineDefinition.builder()
            .tank(36, 17, 4000, false).tank(124, 17, 4000, true).slot(80, 58, SlotRole.OUTPUT)
            .energy(EnergyKind.CONSUMER, 1600, 64, 0, 16).arrow(76, 35).build()),
    // Твердотопливный электрогенератор: 48 FE/t
    SOLID_FUEL_GENERATOR("solid_fuel_generator", true, false, null, MachineDefinition.builder()
            .slot(56, 35, SlotRole.FUEL).slot(116, 35, SlotRole.OUTPUT)
            .energy(EnergyKind.GENERATOR, 24000, 0, 256, 48).flame(80, 36).build()),
    // Углеродный конденсатор: буфер ранней игры
    CARBON_CAPACITOR("carbon_capacitor", false, true, null, MachineDefinition.builder()
            .energy(EnergyKind.STORAGE, 400_000, 256, 256, 256).build());

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
