package dev.technogenesis.kontur.machine;

/** Покрытия солнечных панелей: во сколько процентов от базовой выработки они поднимают эффективность. */
public enum CoatingTier {
    BASIC("basic", 120), ALUMINUM("aluminum", 150), GOLD("gold", 200);

    public final String id;
    public final int percent;

    CoatingTier(String id, int percent) {
        this.id = id;
        this.percent = percent;
    }

    public String itemId() {
        return "coating_" + id;
    }
}
