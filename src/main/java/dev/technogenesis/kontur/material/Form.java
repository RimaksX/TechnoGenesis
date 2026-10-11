package dev.technogenesis.kontur.material;

/** Промежуточные формы руды ступеней ×2, ×3 и ×5. У каждой формы есть вариант для каждого металла. */
public enum Form {
    CRUSHED_ORE("crushed_ore"),
    WASHED_ORE("washed_ore"),
    CONCENTRATE("concentrate"),
    TAILINGS_R1("tailings_r1"),
    /** Рудная пыль после роторной мельницы остатков. */
    FINE_TAILINGS("fine_tailings"),
    /** Кислотная масса: влажная смесь после растворения в кислоте, ещё с раствором. */
    WET_CAKE("wet_cake"),
    /** Сухой остаток после фильтр-пресса, сырьё ступени ×5. */
    CAKE_R2("cake_r2"),
    /** Металлсодержащий осадок, из которого плавится слиток. */
    PRECIPITATE("precipitate"),
    /** Твёрдый шлак: отход экстрактора, сырьё ступени ×8. */
    HARD_SLAG("hard_slag"),
    /** Шлаковая пыль: сверхтонко измельчённый шлак для автоклава. */
    SLAG_DUST("slag_dust"),
    /** Спёкшийся остаток: отход автоклава, сырьё ступени ×12. */
    SINTERED_RESIDUE("sintered_residue");

    public final String suffix;

    Form(String suffix) {
        this.suffix = suffix;
    }

    public String itemId(Metal metal) {
        return metal.id() + "_" + suffix;
    }
}
