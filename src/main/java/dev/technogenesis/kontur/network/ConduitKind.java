package dev.technogenesis.kontur.network;

/** Что переносит труба. Энергию переносят кабели (CableTier), здесь - предметы, жидкости и газы. */
public enum ConduitKind {
    ITEMS("items"), FLUIDS("fluids"), GASES("gases");

    public final String key;

    ConduitKind(String key) {
        this.key = key;
    }
}
