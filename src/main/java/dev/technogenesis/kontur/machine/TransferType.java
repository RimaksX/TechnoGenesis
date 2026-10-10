package dev.technogenesis.kontur.machine;

public enum TransferType {
    ITEMS("items"), FLUIDS("fluids"), ENERGY("energy");

    public final String key;

    TransferType(String key) {
        this.key = key;
    }
}
