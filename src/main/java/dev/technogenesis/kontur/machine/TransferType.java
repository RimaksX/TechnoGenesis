package dev.technogenesis.kontur.machine;

/**
 * Типы передачи. ITEMS - входные слоты, OUT1..OUT3 - выходные слоты по порядку: у каждого выхода свои грани, так что,
 * например, дроблёная руда уходит в одну сторону, а порода в другую. FLUIDS и ENERGY - общие для всех баков и энергии.
 */
public enum TransferType {
    ITEMS("items"), FLUIDS("fluids"), ENERGY("energy"), OUT1("out1"), OUT2("out2"), OUT3("out3");

    public static final TransferType[] OUTPUTS = {OUT1, OUT2, OUT3};

    public final String key;

    TransferType(String key) {
        this.key = key;
    }

    public boolean isOutputChannel() {
        return this == OUT1 || this == OUT2 || this == OUT3;
    }

    /** Номер выходного канала (с нуля) или -1. */
    public int outputIndex() {
        return this == OUT1 ? 0 : this == OUT2 ? 1 : this == OUT3 ? 2 : -1;
    }
}
