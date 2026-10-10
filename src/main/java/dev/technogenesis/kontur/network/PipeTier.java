package dev.technogenesis.kontur.network;

import net.minecraft.util.StringRepresentable;

/**
 * Трубы предметов и жидкостей, по четыре класса каждого вида. Сеть труб работает раз в interval тиков и переносит за
 * раз не больше amount (предметов или мБ). Если в одной сети трубы разных классов, действует самая слабая по
 * пропускной способности в единицах за тик: усиленный участок не ускоряет сеть, а слабый её ограничивает.
 */
public enum PipeTier implements StringRepresentable {
    ITEM_BASIC("item_pipe", ConduitKind.ITEMS, 4, 8),
    ITEM_FAST("item_pipe_fast", ConduitKind.ITEMS, 16, 6),
    ITEM_EXPRESS("item_pipe_express", ConduitKind.ITEMS, 48, 4),
    ITEM_ULTRA("item_pipe_ultra", ConduitKind.ITEMS, 128, 2),
    FLUID_BASIC("fluid_pipe", ConduitKind.FLUIDS, 400, 4),
    FLUID_FAST("fluid_pipe_fast", ConduitKind.FLUIDS, 1200, 4),
    FLUID_HEAVY("fluid_pipe_heavy", ConduitKind.FLUIDS, 4000, 4),
    FLUID_ULTRA("fluid_pipe_ultra", ConduitKind.FLUIDS, 16000, 4);

    public final String id;
    public final ConduitKind kind;
    public final int amount;
    public final int interval;

    PipeTier(String id, ConduitKind kind, int amount, int interval) {
        this.id = id;
        this.kind = kind;
        this.amount = amount;
        this.interval = interval;
    }

    /** Пропускная способность в единицах (предметов или мБ) за тик. */
    public double perTick() {
        return (double) amount / interval;
    }

    @Override
    public String getSerializedName() {
        return id;
    }
}
