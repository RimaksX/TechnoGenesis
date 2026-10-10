package dev.technogenesis.kontur.machine;

/**
 * Уровни модуля форсирования: во сколько раз быстрее цикл, сколько процентов энергии он стоит и сколько тепла за тик
 * выделяет работающая машина. Без охлаждения нагрев копится и при перегреве модуль отключается, пока машина не остынет.
 */
public enum ModuleTier {
    WORKER("worker", 2, 120, 1),
    INDUSTRIAL("industrial", 4, 180, 5),
    PEAK("peak", 8, 300, 12);

    /** Предел нагрева; при его достижении модуль отключается. */
    public static final int HEAT_MAX = 1000;
    /** Модуль включается снова, когда машина остыла до этого значения. */
    public static final int HEAT_RESUME = 400;
    /** Остывание за тик само по себе и от каждой грани, касающейся воды, льда или снега. */
    public static final int COOL_PASSIVE = 2;
    public static final int COOL_PER_FACE = 4;

    public final String id;
    public final int speed;
    public final int energyPercent;
    public final int heatPerTick;

    ModuleTier(String id, int speed, int energyPercent, int heatPerTick) {
        this.id = id;
        this.speed = speed;
        this.energyPercent = energyPercent;
        this.heatPerTick = heatPerTick;
    }

    public String itemId() {
        return "module_" + id;
    }

    /** Сколько граней с охлаждающим блоком нужно, чтобы машина не грелась бесконечно. */
    public int facesNeeded() {
        int over = heatPerTick - COOL_PASSIVE;
        return over <= 0 ? 0 : (over + COOL_PER_FACE - 1) / COOL_PER_FACE;
    }
}
