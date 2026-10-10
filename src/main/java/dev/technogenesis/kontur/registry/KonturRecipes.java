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
