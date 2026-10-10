package dev.technogenesis.kontur.network;

/**
 * Режим стороны трубы, где она касается инвентаря, бака или машины: отдавать внутрь, забирать наружу, и то и другое
 * или выключено (труба там не соединяется).
 */
public enum ConduitMode {
    PUSH("push", 0x3C6EE6), PULL("pull", 0xEB8C28), BOTH("both", 0x46C864), OFF("off", 0x6E6E78);

    public final String key;
    public final int color;

    ConduitMode(String key, int color) {
        this.key = key;
        this.color = color;
    }

    public boolean pushes() {
        return this == PUSH || this == BOTH;
    }

    public boolean pulls() {
        return this == PULL || this == BOTH;
    }

    public ConduitMode next() {
        return values()[(ordinal() + 1) % values().length];
    }

    public ConduitMode prev() {
        return values()[(ordinal() + values().length - 1) % values().length];
    }

    public static ConduitMode byOrdinal(int i) {
        return i >= 0 && i < values().length ? values()[i] : PUSH;
    }
}
