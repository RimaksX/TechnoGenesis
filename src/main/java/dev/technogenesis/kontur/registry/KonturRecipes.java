package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.recipe.MachineRecipe;
import dev.technogenesis.kontur.recipe.MachineRecipeSerializer;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Типы рецептов машин. Каждая машина ступени ×2 имеет собственный тип. */
public final class KonturRecipes {
    public static final DeferredRegister<RecipeType<?>> TYPES = DeferredRegister.create(Registries.RECIPE_TYPE, Kontur.MODID);
    public static final DeferredRegister<RecipeSerializer<?>> SERIALIZERS =
            DeferredRegister.create(Registries.RECIPE_SERIALIZER, Kontur.MODID);

    public static final Kind CRUSHING = new Kind("crushing");
    public static final Kind WASHING = new Kind("washing");
    public static final Kind SEPARATING = new Kind("separating");
    public static final Kind SETTLING = new Kind("settling");
    public static final Kind MILLING = new Kind("milling");
    public static final Kind ACID_SYNTHESIS = new Kind("acid_synthesis");
    public static final Kind LEACHING = new Kind("leaching");
    public static final Kind FILTERING = new Kind("filtering");
    public static final Kind PRECIPITATION = new Kind("precipitation");
    public static final Kind ACID_REGENERATION = new Kind("acid_regeneration");
    public static final Kind EXTRACTION = new Kind("extraction");
    public static final Kind ELECTROLYSIS = new Kind("electrolysis");
    public static final Kind SOLVENT_REGENERATION = new Kind("solvent_regeneration");
    public static final Kind ATTRITION = new Kind("attrition");
    public static final Kind AUTOCLAVING = new Kind("autoclaving");
    public static final Kind STEAM_GENERATION = new Kind("steam_generation");
    public static final Kind PLASMA_GENERATION = new Kind("plasma_generation");
    public static final Kind PLASMA_SMELTING = new Kind("plasma_smelting");
    public static final Kind VACUUM_CASTING = new Kind("vacuum_casting");
    public static final Kind ALLOYING = new Kind("alloying");
    public static final Kind WATER_SPLITTING = new Kind("water_splitting");

    private KonturRecipes() {
    }

    public static final class Kind {
        public final String name;
        public final DeferredHolder<RecipeType<?>, RecipeType<MachineRecipe>> type;
        public final DeferredHolder<RecipeSerializer<?>, MachineRecipeSerializer> serializer;

        private Kind(String name) {
            this.name = name;
            this.type = TYPES.register(name, () -> RecipeType.<MachineRecipe>simple(Kontur.id(name)));
            this.serializer = SERIALIZERS.register(name, () -> new MachineRecipeSerializer(this));
        }
    }
}
