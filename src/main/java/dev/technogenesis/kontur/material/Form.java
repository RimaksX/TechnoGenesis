package dev.technogenesis.kontur.material;

/** Промежуточные формы руды ступени ×2. У каждой формы есть вариант для каждого металла. */
public enum Form {
    CRUSHED_ORE("crushed_ore"),
    WASHED_ORE("washed_ore"),
    CONCENTRATE("concentrate"),
    TAILINGS_R1("tailings_r1"),
    /** Хвосты R1 после роторной мельницы. */
    FINE_TAILINGS("fine_tailings"),
    /** Влажный кек после выщелачивания, ещё с раствором. */
    WET_CAKE("wet_cake"),
    /** Кек R2: сухой остаток для ступени ×5. */
    CAKE_R2("cake_r2"),
    /** Металлсодержащий осадок, из которого плавится слиток. */
    PRECIPITATE("precipitate");

    public final String suffix;

    Form(String suffix) {
        this.suffix = suffix;
    }

    public String itemId(Metal metal) {
        return metal.id() + "_" + suffix;
    }
}
