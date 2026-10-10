package dev.technogenesis.kontur.material;

/** Промежуточные формы руды ступени ×2. У каждой формы есть вариант для каждого металла. */
public enum Form {
    CRUSHED_ORE("crushed_ore"),
    WASHED_ORE("washed_ore"),
    CONCENTRATE("concentrate"),
    TAILINGS_R1("tailings_r1");

    public final String suffix;

    Form(String suffix) {
        this.suffix = suffix;
    }

    public String itemId(Metal metal) {
        return metal.id() + "_" + suffix;
    }
}
