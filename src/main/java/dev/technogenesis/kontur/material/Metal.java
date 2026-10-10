package dev.technogenesis.kontur.material;

import java.util.Locale;

/** Металлы, участвующие в переработке. */
public enum Metal {
    IRON(true), COPPER(true), GOLD(true),
    ALUMINUM(false), NICKEL(false), TUNGSTEN(false), CHROMIUM(false), MANGANESE(false),
    COBALT(false), MOLYBDENUM(false), TITANIUM(false);

    public final boolean vanilla;

    Metal(boolean vanilla) {
        this.vanilla = vanilla;
    }

    public String id() {
        return name().toLowerCase(Locale.ROOT);
    }
}
