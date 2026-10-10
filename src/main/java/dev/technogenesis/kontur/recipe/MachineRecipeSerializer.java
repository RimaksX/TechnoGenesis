package dev.technogenesis.kontur.recipe;

import com.mojang.serialization.MapCodec;
import dev.technogenesis.kontur.registry.KonturRecipes;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.crafting.RecipeSerializer;

public class MachineRecipeSerializer implements RecipeSerializer<MachineRecipe> {
    private final MapCodec<MachineRecipe> codec;
    private final StreamCodec<RegistryFriendlyByteBuf, MachineRecipe> streamCodec;

    public MachineRecipeSerializer(KonturRecipes.Kind kind) {
        this.codec = MachineRecipe.codec(kind);
        this.streamCodec = MachineRecipe.streamCodec(kind);
    }

    @Override
    public MapCodec<MachineRecipe> codec() {
        return codec;
    }

    @Override
    public StreamCodec<RegistryFriendlyByteBuf, MachineRecipe> streamCodec() {
        return streamCodec;
    }
}
