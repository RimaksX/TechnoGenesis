package dev.technogenesis.kontur.machine;

/**
 * Наконечники бура шахтёра: отличаются только запасом прочности, скорость задают модули. Износ за блок - его твёрдость,
 * округлённая вверх (камень 2, обсидиан 50), поэтому железного наконечника хватает примерно на 300 блоков камня.
 */
public enum DrillTier {
    IRON("iron", 600), STEEL("steel", 2400), CARBIDE("carbide", 9600);

    public final String id;
    public final int durability;

    DrillTier(String id, int durability) {
        this.id = id;
        this.durability = durability;
    }

    public String itemId() {
        return "drill_tip_" + id;
    }

    /** Номер класса для передачи на клиент: 0 - наконечника нет. */
    public int code() {
        return ordinal() + 1;
    }

    public static DrillTier byCode(int code) {
        return code >= 1 && code <= values().length ? values()[code - 1] : null;
    }
}
