package dev.technogenesis.kontur.machine;

import net.minecraft.network.chat.Component;

/** Состояние машины; безопасная остановка всегда называет точную причину. */
public enum MachineStatus {
    IDLE(false), RUNNING(false), NO_ENERGY(true), NO_FLUID(true), OUTPUT_FULL(true), FLUID_OUTPUT_FULL(true),
    NO_FUEL(true), FULL(false), CHARGING(false), NO_SKY(true), NO_SUN(false), NO_HEAT(true), NO_WATER(true),
    // шахтёр
    FRAME_OPEN(true), FRAME_EXTRA(true), FRAME_SIZE(true), FRAME_CORNER(true), FRAME_FRONT(true), AREA_BLOCKED(true),
    NO_TIPS(true), NO_DEPOT(true), LIQUID(true), MINE_DONE(false), UNLOADED(true), TIP_SWAP(false), NOT_CHECKED(true),
    // термоядерный реактор
    STRUCTURE_MISSING(true), STRUCTURE_BLOCKED(true), SCRAM(true);

    public final boolean problem;

    MachineStatus(boolean problem) {
        this.problem = problem;
    }

    public Component text() {
        return Component.translatable("status.kontur." + name().toLowerCase(java.util.Locale.ROOT));
    }
}
