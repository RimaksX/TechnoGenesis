package dev.technogenesis.kontur.jei;

import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.recipe.MachineRecipe;
import dev.technogenesis.kontur.registry.KonturBlocks;
import java.text.NumberFormat;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.builder.IRecipeSlotBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.drawable.IDrawableAnimated;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.neoforge.NeoForgeTypes;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.neoforged.neoforge.fluids.FluidStack;

/**
 * Универсальная категория JEI для рецептов машин: вход (предмет и/или жидкость) -> стрелка -> выходы
 * (предметы с шансом и жидкости), внизу энергия цикла и время.
 */
final class MachineRecipeCategory implements IRecipeCategory<RecipeHolder<MachineRecipe>> {
    static final int WIDTH = 140;
    static final int HEIGHT = 78;

    private static final int TANK_Y = 4;
    private static final int TANK_W = 16;
    private static final int TANK_H = 56;
    private static final int IN_TANK_X = 26;
    private static final int OUT_TANK_X = 116;
    private static final int ARROW_X = 52;
    private static final int ARROW_Y = 23;
    private static final int OUT_X = 82;

    private final MachineKind kind;
    private final RecipeType<RecipeHolder<MachineRecipe>> type;
    private final IGuiHelper helper;
    private final IDrawable icon;
    private final IDrawable slot;
    private final Map<Integer, IDrawableAnimated> arrows = new HashMap<>();

    MachineRecipeCategory(IGuiHelper helper, MachineKind kind) {
        this.helper = helper;
        this.kind = kind;
        this.type = KonturJeiTypes.of(kind.recipeKind);
        this.icon = helper.createDrawableIngredient(VanillaTypes.ITEM_STACK,
                new ItemStack(KonturBlocks.MACHINES.get(kind).get()));
        this.slot = helper.getSlotDrawable();
    }

    @Override
    public RecipeType<RecipeHolder<MachineRecipe>> getRecipeType() {
        return type;
    }

    @Override
    public Component getTitle() {
        return KonturBlocks.MACHINES.get(kind).get().getName();
    }

    @Override
    public IDrawable getIcon() {
        return icon;
    }

    @Override
    public int getWidth() {
        return WIDTH;
    }

    @Override
    public int getHeight() {
        return HEIGHT;
    }

    @Override
    public ResourceLocation getRegistryName(RecipeHolder<MachineRecipe> recipe) {
        return recipe.id();
    }

    @Override
    public void setRecipe(IRecipeLayoutBuilder builder, RecipeHolder<MachineRecipe> holder, IFocusGroup focuses) {
        MachineRecipe recipe = holder.value();

        recipe.input().ifPresent(in -> {
            List<ItemStack> stacks = Arrays.stream(in.ingredient().getItems())
                    .map(s -> s.copyWithCount(in.count())).toList();
            builder.addSlot(RecipeIngredientRole.INPUT, 5, 24).setBackground(slot, -1, -1).addItemStacks(stacks);
        });
        recipe.fluidInput().ifPresent(f -> {
            List<FluidStack> fluids = f.fluids().stream().map(fl -> new FluidStack(fl, f.amount())).toList();
            builder.addSlot(RecipeIngredientRole.INPUT, IN_TANK_X + 1, TANK_Y + 1)
                    .addIngredients(NeoForgeTypes.FLUID_STACK, fluids)
                    .setFluidRenderer(1000, false, TANK_W - 2, TANK_H - 2);
        });

        List<MachineRecipe.ChanceResult> results = recipe.results();
        int n = results.size();
        int top = 24 - (n - 1) * 9;
        for (int i = 0; i < n; i++) {
            MachineRecipe.ChanceResult r = results.get(i);
            IRecipeSlotBuilder out = builder.addSlot(RecipeIngredientRole.OUTPUT, OUT_X + 1, top + i * 18)
                    .setBackground(slot, -1, -1).addItemStack(r.stack());
            if (r.chance() < 1.0f) {
                int percent = Math.round(r.chance() * 100);
                out.addRichTooltipCallback((view, tooltip) ->
                        tooltip.add(Component.translatable("jei.kontur.chance", percent)));
            }
        }
        int fluidOuts = recipe.fluidResults().size();
        for (int i = 0; i < fluidOuts; i++) {
            builder.addSlot(RecipeIngredientRole.OUTPUT, outTankX(i, fluidOuts) + 1, TANK_Y + 1)
                    .addIngredient(NeoForgeTypes.FLUID_STACK, recipe.fluidResults().get(i).stack())
                    .setFluidRenderer(1000, false, TANK_W - 2, TANK_H - 2);
        }
    }

    @Override
    public void draw(RecipeHolder<MachineRecipe> holder, IRecipeSlotsView slots, GuiGraphics g, double mouseX,
                     double mouseY) {
        MachineRecipe recipe = holder.value();
        if (recipe.fluidInput().isPresent()) {
            tankFrame(g, IN_TANK_X, TANK_Y);
        }
        int fluidOuts = recipe.fluidResults().size();
        for (int i = 0; i < fluidOuts; i++) {
            tankFrame(g, outTankX(i, fluidOuts), TANK_Y);
        }
        arrows.computeIfAbsent(recipe.time(), t -> helper.createAnimatedRecipeArrow(t)).draw(g, ARROW_X, ARROW_Y);

        String energy = NumberFormat.getIntegerInstance(Locale.ROOT).format(recipe.energy()).replace(',', ' ');
        String seconds = String.format(Locale.ROOT, "%.2f", recipe.time() / 20.0).replaceAll("0+$", "").replaceAll("\\.$", "");
        g.drawString(Minecraft.getInstance().font, Component.translatable("jei.kontur.stats", energy, seconds),
                4, HEIGHT - 12, 0xFF555555, false);
    }

    /** Несколько выходных жидкостей (водород и кислород) стоят рядом: последняя у правого края. */
    private static int outTankX(int index, int count) {
        return OUT_TANK_X - (count - 1 - index) * (TANK_W + 4);
    }

    /** Утопленная рамка бака под жидкость в стиле интерфейса машин. */
    private static void tankFrame(GuiGraphics g, int x, int y) {
        g.fill(x, y, x + TANK_W, y + TANK_H, 0xFF8B8B8B);
        g.fill(x, y, x + TANK_W - 1, y + 1, 0xFF373737);
        g.fill(x, y, x + 1, y + TANK_H - 1, 0xFF373737);
        g.fill(x + 1, y + TANK_H - 1, x + TANK_W, y + TANK_H, 0xFFFFFFFF);
        g.fill(x + TANK_W - 1, y + 1, x + TANK_W, y + TANK_H, 0xFFFFFFFF);
    }
}
