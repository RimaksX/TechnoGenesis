package dev.technogenesis.kontur.material;

import java.util.Locale;

/** Металлы, участвующие в переработке. */
public enum Metal {
    IRON(true, 0xFF8FA05A), COPPER(true, 0xFF3A9AD9), GOLD(true, 0xFFE6C84A),
    ALUMINUM(false, 0xFFBFD0E0), NICKEL(false, 0xFF5CB87A), TUNGSTEN(false, 0xFF6A6F8C), CHROMIUM(false, 0xFF4FA37A),
    MANGANESE(false, 0xFFB25FB0), COBALT(false, 0xFFD45A78), MOLYBDENUM(false, 0xFF4A86C9),
    TITANIUM(false, 0xFFB8A8E0);

    public final boolean vanilla;
    /** Цвет раствора этого металла (оттенок ванильной воды). */
    public final int solutionTint;

    Metal(boolean vanilla, int solutionTint) {
        this.vanilla = vanilla;
        this.solutionTint = solutionTint;
    }

    public String id() {
        return name().toLowerCase(Locale.ROOT);
    }
}
