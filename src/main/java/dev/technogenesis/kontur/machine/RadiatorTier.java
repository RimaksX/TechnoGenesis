package dev.technogenesis.kontur.machine;

/**
 * Радиаторы: ставятся в слот радиатора на вкладке машины и добавляют остывание за тик к собственному (COOL_PASSIVE).
 * Охлаждение больше не требует свободных граней: вода, лёд и снег рядом лишь дают дополнительный бонус.
 */
public enum RadiatorTier {
    COPPER("copper", 6), ALUMINUM("aluminum", 10), TITANIUM("titanium", 16);

    public final String id;
    public final int cooling;

    RadiatorTier(String id, int cooling) {
        this.id = id;
        this.cooling = cooling;
    }

    public String itemId() {
        return "radiator_" + id;
    }
}
