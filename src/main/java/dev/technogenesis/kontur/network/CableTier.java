package dev.technogenesis.kontur.network;

import net.minecraft.util.StringRepresentable;

/**
 * Классы кабелей и их пропускная способность (FE/t) - на сколько кабель может пустить через сеть за тик.
 * Шаг между классами в 4 раза: медный тянет несколько машин без модулей, сверхпроводящий - целую базу.
 */
public enum CableTier implements StringRepresentable {
    COPPER("copper_wire", 128),
    CERAMIC("ceramic_cable", 512),
    ARMORED("armored_cable", 2048),
    SUPERCONDUCTING("superconducting_cable", 8192);

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
