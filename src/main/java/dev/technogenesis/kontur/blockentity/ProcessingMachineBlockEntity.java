package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.recipe.MachineRecipe;
import dev.technogenesis.kontur.recipe.MachineRecipeInput;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Дробилка, барабан, сепаратор и отстойник: цикл целиком задаётся рецептом.
 * Порядок проверок (как в ТЗ 9.3): входы -> место под ВСЕ выходы -> энергия -> работа. При любой неудаче машина
 * стоит и показывает точную причину, ничего не теряя.
 */
public class ProcessingMachineBlockEntity extends MachineBlockEntity {
    private final int inputSlot;
    private final int[] outputSlots;
    private final int inputTank;
    private final int outputTank;
    private RecipeHolder<MachineRecipe> current;

    public ProcessingMachineBlockEntity(MachineKind kind, BlockPos pos, BlockState state) {
        super(kind, pos, state);
        this.inputSlot = def.inputSlot();
        this.outputSlots = def.outputSlots();
        this.inputTank = def.inputTank();
        this.outputTank = def.outputTank();
    }

    private RecipeType<MachineRecipe> recipeType() {
        return kind.recipeKind.type.get();
    }

    @Override
    protected boolean acceptsItem(int slot, ItemStack stack) {
        if (level == null) {
            return true;
        }
        for (RecipeHolder<MachineRecipe> h : level.getRecipeManager().getAllRecipesFor(recipeType())) {
            if (h.value().input().map(in -> in.test(stack)).orElse(false)) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        if (level == null) {
            return true;
        }
        for (RecipeHolder<MachineRecipe> h : level.getRecipeManager().getAllRecipesFor(recipeType())) {
            if (h.value().fluidInput().map(f -> f.accepts(stack.getFluid())).orElse(false)) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected boolean interchangeable(FluidStack a, FluidStack b) {
        if (level == null) {
            return false;
        }
        for (RecipeHolder<MachineRecipe> h : level.getRecipeManager().getAllRecipesFor(recipeType())) {
            if (h.value().fluidInput().map(f -> f.accepts(a.getFluid()) && f.accepts(b.getFluid())).orElse(false)) {
                return true;
            }
        }
        return false;
    }

    private MachineRecipeInput currentInput() {
        ItemStack in = inputSlot >= 0 ? inventory.getStackInSlot(inputSlot) : ItemStack.EMPTY;
        FluidStack fluid = inputTank >= 0 ? tanks[inputTank].getFluid() : FluidStack.EMPTY;
        return new MachineRecipeInput(in, fluid);
    }

    @Override
    protected void tickMachine() {
        MachineRecipeInput input = currentInput();
        if (current == null || !current.value().matches(input, level)) {
            Optional<RecipeHolder<MachineRecipe>> found = level.getRecipeManager().getRecipeFor(recipeType(), input, level);
            current = found.orElse(null);
            progress = 0;
            if (current == null) {
                totalTime = 0;
                setStatus(missingFluid(input) ? MachineStatus.NO_FLUID : MachineStatus.IDLE);
                return;
            }
        }
        MachineRecipe recipe = current.value();
        totalTime = recipe.time();

        // 1. место под все выходы (включая шансовые - место нужно на худший случай)
        List<MachineRecipe.ChanceResult> results = recipe.results();
        for (int i = 0; i < results.size() && i < outputSlots.length; i++) {
            if (!inventory.insertItem(outputSlots[i], results.get(i).stack(), true).isEmpty()) {
                setStatus(MachineStatus.OUTPUT_FULL);
                return;
            }
        }
        for (MachineRecipe.FluidOutput out : recipe.fluidResults()) {
            if (outputTank < 0 || tanks[outputTank].fill(out.stack(), FluidAction.SIMULATE) < out.amount()) {
                setStatus(MachineStatus.FLUID_OUTPUT_FULL);
                return;
            }
        }
        // 2. энергия этого тика
        // модуль форсирования: за тик выполняется несколько шагов цикла, энергия за них платится сразу
        int steps = Math.max(1, Math.min(activeSpeed(), recipe.time() - progress));
        int base = 0;
        for (int i = 0; i < steps; i++) {
            base += recipe.energyForTick(progress + i);
        }
        int cost = (int) (((long) base * activeEnergyPercent() + 99) / 100);
        if (energy.getEnergyStored() < cost) {
            setStatus(MachineStatus.NO_ENERGY);
            return;
        }
        // 3. работа
        energy.consume(cost);
        progress += steps;
        setStatus(MachineStatus.RUNNING);
        if (progress >= recipe.time()) {
            finish(recipe);
            progress = 0;
        }
        setChanged();
    }

    /** Есть предмет, подходящий под какой-то рецепт, но не хватает жидкости. */
    private boolean missingFluid(MachineRecipeInput input) {
        if (inputTank < 0) {
            return false;
        }
        for (RecipeHolder<MachineRecipe> h : level.getRecipeManager().getAllRecipesFor(recipeType())) {
            MachineRecipe r = h.value();
            if (r.fluidInput().isPresent() && r.matchesItemOnly(input.stack())
                    && (inputSlot < 0 || !input.stack().isEmpty())) {
                return true;
            }
        }
        return false;
    }

    private void finish(MachineRecipe recipe) {
        recipe.input().ifPresent(in -> inventory.extractItem(inputSlot, in.count(), false));
        recipe.fluidInput().ifPresent(f -> tanks[inputTank].drain(f.amount(), FluidAction.EXECUTE));
        List<MachineRecipe.ChanceResult> results = recipe.results();
        for (int i = 0; i < results.size() && i < outputSlots.length; i++) {
            MachineRecipe.ChanceResult r = results.get(i);
            if (r.chance() >= 1.0f || level.random.nextFloat() < r.chance()) {
                inventory.insertItem(outputSlots[i], r.stack(), false);
            }
        }
        for (MachineRecipe.FluidOutput out : recipe.fluidResults()) {
            tanks[outputTank].fill(out.stack(), FluidAction.EXECUTE);
        }
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        BlockState state = getBlockState();
        if (state.getValue(MachineBlock.ACTIVE) != active) {
            level.setBlock(worldPosition, state.setValue(MachineBlock.ACTIVE, active), 3);
        }
    }
}
