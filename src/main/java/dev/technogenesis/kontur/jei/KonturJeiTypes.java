package dev.technogenesis.kontur.jei;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.recipe.MachineRecipe;
import dev.technogenesis.kontur.registry.KonturRecipes;
import java.util.EnumMap;
import java.util.Map;
import java.util.HashMap;
import mezz.jei.api.recipe.RecipeType;
import net.minecraft.world.item.crafting.RecipeHolder;

/** Типы рецептов JEI для машин Контура (по одному на каждый тип рецепта машины). */
final class KonturJeiTypes {
    private static final Map<String, RecipeType<RecipeHolder<MachineRecipe>>> TYPES = new HashMap<>();

    private KonturJeiTypes() {
    }

    static RecipeType<RecipeHolder<MachineRecipe>> of(KonturRecipes.Kind kind) {
        return TYPES.computeIfAbsent(kind.name, name -> RecipeType.createRecipeHolderType(Kontur.id(name)));
    }
}
