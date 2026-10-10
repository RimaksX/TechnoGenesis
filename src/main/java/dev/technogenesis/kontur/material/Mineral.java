package dev.technogenesis.kontur.material;

/** Новые месторождения. */
public enum Mineral {
    BAUXITE("bauxite_ore", "raw_bauxite", Metal.ALUMINUM, 0, 3.0f, 0, 0, false),
    GARNIERITE("garnierite_ore", "raw_garnierite", Metal.NICKEL, 0, 3.0f, 0, 0, false),
    WOLFRAMITE("wolframite_ore", "raw_wolframite", Metal.TUNGSTEN, 1, 4.0f, 0, 0, false),
    CHROMITE("chromite_ore", "raw_chromite", Metal.CHROMIUM, 1, 3.5f, 0, 0, false),
    PYROLUSITE("pyrolusite_ore", "raw_pyrolusite", Metal.MANGANESE, 0, 3.0f, 0, 0, false),
    COBALTITE("cobaltite_ore", "raw_cobaltite", Metal.COBALT, 1, 4.0f, 0, 0, false),
    MOLYBDENITE("molybdenite_ore", "raw_molybdenite", Metal.MOLYBDENUM, 1, 3.5f, 0, 0, false),
    RUTILE("rutile_ore", "raw_rutile", Metal.TITANIUM, 1, 4.0f, 0, 0, false),
    GRAPHITE("graphite_ore", "raw_graphite", null, 0, 2.5f, 0, 2, false),
    HALITE("halite_ore", "raw_halite", null, 0, 2.0f, 0, 2, false),
    SULFUR("native_sulfur_ore", "raw_sulfur", null, 0, 2.0f, 1, 3, true),
    SPODUMENE("spodumene_ore", "raw_spodumene", null, 2, 4.5f, 2, 5, false);

    public final String oreId;
    public final String rawId;
    /** Конечный металл или null для неметаллического сырья. */
    public final Metal metal;
    /** Требуемый уровень инструмента: 0 - камень, 1 - железо, 2 - алмаз. */
    public final int toolTier;
    public final float hardness;
    public final int xpMin;
    public final int xpMax;
    public final boolean nether;

    Mineral(String oreId, String rawId, Metal metal, int toolTier, float hardness, int xpMin, int xpMax, boolean nether) {
        this.oreId = oreId;
        this.rawId = rawId;
        this.metal = metal;
        this.toolTier = toolTier;
        this.hardness = hardness;
        this.xpMin = xpMin;
        this.xpMax = xpMax;
        this.nether = nether;
    }
}
