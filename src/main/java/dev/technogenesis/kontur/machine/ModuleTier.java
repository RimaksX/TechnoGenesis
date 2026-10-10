package dev.technogenesis.kontur.machine;

/** Уровни модуля форсирования: во сколько раз быстрее цикл и сколько процентов энергии он стоит относительно обычного. */
public enum ModuleTier {
    WORKER("worker", 2, 100),
    INDUSTRIAL("industrial", 4, 125),
    PEAK("peak", 8, 150);

    public final String id;
    public final int speed;
    public final int energyPercent;

    ModuleTier(String id, int speed, int energyPercent) {
        this.id = id;
        this.speed = speed;
        this.energyPercent = energyPercent;
    }

    public String itemId() {
        return "module_" + id;
    }
}
