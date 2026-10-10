package dev.technogenesis.kontur.network;

import net.minecraft.util.StringRepresentable;

/**
 * Классы кабелей и их пропускная способность (FE/t) - на сколько кабель может пустить через сеть за тик.
 * Шаг между классами в 4 раза, запас сделан с избытком: медный тянет пять машин без модулей, сверхпроводящий -
 * большую базу с модулями.
 */
public enum CableTier implements StringRepresentable {
    COPPER("copper_wire", 384),
    CERAMIC("ceramic_cable", 1536),
    ARMORED("armored_cable", 6144),
    SUPERCONDUCTING("superconducting_cable", 24576);

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
