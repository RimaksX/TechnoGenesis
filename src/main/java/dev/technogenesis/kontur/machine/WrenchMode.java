package dev.technogenesis.kontur.machine;

/** Режим ключа: какие стороны он переключает. ALL - сразу все типы, EJECT - авто-вывод вместо сторон. */
public enum WrenchMode {
    ALL("all", null), ITEMS("items", TransferType.ITEMS), OUT1("out1", TransferType.OUT1),
    OUT2("out2", TransferType.OUT2), OUT3("out3", TransferType.OUT3), FLUIDS("fluids", TransferType.FLUIDS),
    ENERGY("energy", TransferType.ENERGY), EJECT("eject", null);

    public final String key;
    /** Тип передачи для одиночных режимов, иначе null. */
    public final TransferType type;

    WrenchMode(String key, TransferType type) {
        this.key = key;
        this.type = type;
    }

    public WrenchMode next() {
        return values()[(ordinal() + 1) % values().length];
    }

    public static WrenchMode byOrdinal(int i) {
        return i >= 0 && i < values().length ? values()[i] : ALL;
    }
}
