package dev.technogenesis.kontur.recipe;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeInput;
import net.neoforged.neoforge.fluids.FluidStack;

/** Содержимое входов машины: предметы во входных слотах (второй - у сплавной печи) и жидкость во входном баке. */
public record MachineRecipeInput(ItemStack stack, ItemStack stackB, FluidStack fluid) implements RecipeInput {
    public MachineRecipeInput(ItemStack stack, FluidStack fluid) {
        this(stack, ItemStack.EMPTY, fluid);
    }

    @Override
    public ItemStack getItem(int index) {
        return stack;
    }

    @Override
    public int size() {
        return 1;
    }
}
