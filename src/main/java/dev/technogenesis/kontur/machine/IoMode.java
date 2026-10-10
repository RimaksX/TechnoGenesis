package dev.technogenesis.kontur.machine;

/** Режим одной стороны машины для одного типа передачи. */
public enum IoMode {
    NONE("none"), INPUT("input"), OUTPUT("output"), ALL("all");

    public final String key;

    IoMode(String key) {
        this.key = key;
    }

    public boolean canInput() {
        return this == INPUT || this == ALL;
    }

    public boolean canOutput() {
        return this == OUTPUT || this == ALL;
    }

    public IoMode next() {
        return values()[(ordinal() + 1) % values().length];
    }

    public IoMode prev() {
        return values()[(ordinal() + values().length - 1) % values().length];
    }
}
