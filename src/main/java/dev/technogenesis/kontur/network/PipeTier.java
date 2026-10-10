package dev.technogenesis.kontur.network;

import net.minecraft.util.StringRepresentable;

/**
 * Трубы предметов и жидкостей. Сеть труб работает раз в interval тиков и переносит за раз не больше amount
 * (предметов или мБ) - по самой слабой трубе сети.
 */
public enum PipeTier implements StringRepresentable {
    ITEM_BASIC("item_pipe", ConduitKind.ITEMS, 4, 8),
    ITEM_FAST("item_pipe_fast", ConduitKind.ITEMS, 32, 4),
    FLUID_BASIC("fluid_pipe", ConduitKind.FLUIDS, 400, 4),
    FLUID_FAST("fluid_pipe_fast", ConduitKind.FLUIDS, 4000, 4);

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

    /** Пропускная способность в единицах (предметов или мБ) за тик, для подсказок. */
    public int perTick() {
        return Math.max(1, amount / interval);
    }

    @Override
    public String getSerializedName() {
        return id;
    }
}
