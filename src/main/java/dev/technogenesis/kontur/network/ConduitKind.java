package dev.technogenesis.kontur.network;

/** Что переносит труба. Энергию переносят кабели (CableTier), здесь - предметы и жидкости. */
public enum ConduitKind {
    ITEMS("items"), FLUIDS("fluids");

    public final String key;

    ConduitKind(String key) {
        this.key = key;
    }
}
