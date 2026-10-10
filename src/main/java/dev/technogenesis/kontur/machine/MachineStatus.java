package dev.technogenesis.kontur.machine;

import net.minecraft.network.chat.Component;

/** Состояние машины; безопасная остановка всегда называет точную причину. */
public enum MachineStatus {
    IDLE(false), RUNNING(false), NO_ENERGY(true), NO_FLUID(true), OUTPUT_FULL(true), FLUID_OUTPUT_FULL(true),
    NO_FUEL(true), FULL(false), CHARGING(false), NO_SKY(true), NO_SUN(false), NO_HEAT(true), NO_WATER(true);

    public final boolean problem;

    MachineStatus(boolean problem) {
        this.problem = problem;
    }

    public Component text() {
        return Component.translatable("status.kontur." + name().toLowerCase(java.util.Locale.ROOT));
    }
}
