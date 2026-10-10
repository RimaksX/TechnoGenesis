package dev.technogenesis.kontur.recipe;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeInput;
import net.neoforged.neoforge.fluids.FluidStack;

/** Содержимое входов машины: предмет во входном слоте и жидкость во входном баке. */
public record MachineRecipeInput(ItemStack stack, FluidStack fluid) implements RecipeInput {
    @Override
    public ItemStack getItem(int index) {
        return stack;
    }

    @Override
    public int size() {
        return 1;
    }
}
