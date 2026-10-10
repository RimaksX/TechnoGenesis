package dev.technogenesis.kontur.network;

/**
 * Режим стороны трубы, где она касается инвентаря, бака или машины: автоматически (по умолчанию), отдавать внутрь,
 * забирать наружу, и то и другое или выключено (труба там не соединяется). Автоматический режим у машин Контура
 * работает как "и то и другое" (машина сама пропускает наружу только выходы, а внутрь только входы), у остальных
 * инвентарей и баков - как "отдавать внутрь", чтобы сундуки не перекачивали друг друга.
 */
public enum ConduitMode {
    AUTO("auto", 0x9A9A94), PUSH("push", 0x7088B8), PULL("pull", 0xC09468), BOTH("both", 0x84A486), OFF("off", 0x6E6E78);

    public final String key;
    public final int color;

    ConduitMode(String key, int color) {
        this.key = key;
        this.color = color;
    }

    /** Действующий режим: AUTO превращается в BOTH у машин Контура и в PUSH у всего остального. */
    public ConduitMode resolve(boolean konturMachine) {
        return this == AUTO ? (konturMachine ? BOTH : PUSH) : this;
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
        return i >= 0 && i < values().length ? values()[i] : AUTO;
    }
}
