package dev.technogenesis.kontur.jei;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.client.MachineScreen;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.material.Form;
import dev.technogenesis.kontur.material.Metal;
import dev.technogenesis.kontur.recipe.MachineRecipe;
import dev.technogenesis.kontur.registry.KonturBlocks;
import dev.technogenesis.kontur.registry.KonturItems;
import java.util.Collection;
import java.util.List;
import java.util.Objects;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.gui.handlers.IGuiClickableArea;
import mezz.jei.api.gui.handlers.IGuiContainerHandler;
import mezz.jei.api.registration.IGuiHandlerRegistration;
import mezz.jei.api.registration.IRecipeCatalystRegistration;
import mezz.jei.api.registration.IRecipeCategoryRegistration;
import mezz.jei.api.registration.IRecipeRegistration;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.Rect2i;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;

/**
 * Интеграция с JEI: рецепты четырёх машин ступени ×2, машины как катализаторы, клик по стрелке прогресса
 * в интерфейсе машины открывает её рецепты. Классы этого пакета загружает только JEI.
 */
@JeiPlugin
public class KonturJeiPlugin implements IModPlugin {
    @Override
    public ResourceLocation getPluginUid() {
        return ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "jei_plugin");
    }

    private static boolean hasRecipes(MachineKind kind) {
        return kind.recipeKind != null;
    }

    @Override
    public void registerCategories(IRecipeCategoryRegistration registration) {
        for (MachineKind kind : MachineKind.values()) {
            if (hasRecipes(kind)) {
                registration.addRecipeCategories(
                        new MachineRecipeCategory(registration.getJeiHelpers().getGuiHelper(), kind));
            }
        }
    }

    @Override
    public void registerRecipes(IRecipeRegistration registration) {
        var recipes = Objects.requireNonNull(Minecraft.getInstance().level).getRecipeManager();
        for (MachineKind kind : MachineKind.values()) {
            if (hasRecipes(kind)) {
                List<RecipeHolder<MachineRecipe>> list = recipes.getAllRecipesFor(kind.recipeKind.type.get());
                registration.addRecipes(KonturJeiTypes.of(kind.recipeKind), list);
            }
        }
        List<ItemStack> tailings = java.util.Arrays.stream(Metal.values())
                .map(m -> new ItemStack(KonturItems.FORMS.get(Form.TAILINGS_R1).get(m).get())).toList();
        registration.addIngredientInfo(tailings, VanillaTypes.ITEM_STACK, Component.translatable("jei.kontur.info.tailings"));
        List<ItemStack> cakes = java.util.Arrays.stream(Metal.values())
                .map(m -> new ItemStack(KonturItems.FORMS.get(Form.CAKE_R2).get(m).get())).toList();
        registration.addIngredientInfo(cakes, VanillaTypes.ITEM_STACK, Component.translatable("jei.kontur.info.cake_r2"));
    }

    @Override
    public void registerRecipeCatalysts(IRecipeCatalystRegistration registration) {
        for (MachineKind kind : MachineKind.values()) {
            if (hasRecipes(kind)) {
                registration.addRecipeCatalyst(KonturBlocks.MACHINES.get(kind).get(), KonturJeiTypes.of(kind.recipeKind));
            }
        }
    }

    @Override
    public void registerGuiHandlers(IGuiHandlerRegistration registration) {
        registration.addGuiContainerHandler(MachineScreen.class, new IGuiContainerHandler<MachineScreen>() {
            @Override
            public List<Rect2i> getGuiExtraAreas(MachineScreen screen) {
                return screen.extraAreas();
            }

            @Override
            public Collection<IGuiClickableArea> getGuiClickableAreas(MachineScreen screen, double mouseX, double mouseY) {
                MachineKind kind = screen.kind();
                if (!hasRecipes(kind) || !kind.definition.hasArrow()) {
                    return List.of();
                }
                int x = kind.definition.arrowX;
                int y = kind.definition.arrowY;
                if (mouseX >= x && mouseX < x + 28 && mouseY >= y - 2 && mouseY < y + 10) {
                    return List.of(IGuiClickableArea.createBasic(x, y - 2, 28, 12, KonturJeiTypes.of(kind.recipeKind)));
                }
                return List.of();
            }
        });
    }
}
