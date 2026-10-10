package dev.technogenesis.kontur.network;

import net.minecraft.util.StringRepresentable;

/** Классы кабелей и их пропускная способность (FE/t). Пропускная способность не создаёт энергию. */
public enum CableTier implements StringRepresentable {
    COPPER("copper_wire", 32),
    CERAMIC("ceramic_cable", 128),
    ARMORED("armored_cable", 512),
    SUPERCONDUCTING("superconducting_cable", 4096);

    public final String id;
    public final int throughput;

    CableTier(String id, int throughput) {
        this.id = id;
        this.throughput = throughput;
    }

    @Override
    public String getSerializedName() {
        return id;
    }
}
