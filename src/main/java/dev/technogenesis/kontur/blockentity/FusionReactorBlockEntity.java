package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.AssemblyShape;
import dev.technogenesis.kontur.machine.AssemblyTracker;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturFluids;
import dev.technogenesis.kontur.registry.KonturItems;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Термоядерный реактор: контроллер собранной игроком коробки 5 x 5 x 4 (см. AssemblyShape). Работает, только если схема
 * цела (проверка раз в секунду). Горит смесь водорода (40 мБ/т), разогретая плазмой (20 мБ/т); стенки охлаждает вода
 * (25 мБ/т); литиевый стержень в слоте тратится за 6000 тиков (5 минут) и даёт тритий. Результат - 8000 FE/t.
 * Нет любого из четырёх компонентов - реактор останавливается и называет, чего не хватает.
 */
public class FusionReactorBlockEntity extends MachineBlockEntity implements AssemblyController {
    public static final int OUTPUT_PER_TICK = 8000;
    public static final int HYDROGEN_PER_TICK = 40;
    public static final int PLASMA_PER_TICK = 20;
    public static final int WATER_PER_TICK = 25;
    public static final int ROD_BURN_TICKS = 6000;

    private final AssemblyTracker tracker = new AssemblyTracker(AssemblyShape.FUSION);
    private int rodLeft;

    public FusionReactorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.FUSION_REACTOR, pos, state);
    }

    @Override
    public boolean isFormed() {
        return tracker.formed();
    }

    @Override
    protected boolean acceptsItem(int slot, ItemStack stack) {
        return stack.is(KonturItems.LITHIUM_ROD.get());
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        Fluid f = stack.getFluid();
        return f == KonturFluids.HYDROGEN.source.get() || f == KonturFluids.PLASMA.source.get() || isWater(f);
    }

    @Override
    protected boolean interchangeable(FluidStack a, FluidStack b) {
        return isWater(a.getFluid()) && isWater(b.getFluid());
    }

    private static boolean isWater(Fluid f) {
        return f == Fluids.WATER || f == KonturFluids.TECHNICAL_WATER.source.get();
    }

    private int tankWith(java.util.function.Predicate<Fluid> test) {
        for (int i = 0; i < tanks.length; i++) {
            if (!tanks[i].isEmpty() && test.test(tanks[i].getFluid().getFluid())) {
                return i;
            }
        }
        return -1;
    }

    @Override
    protected void tickMachine() {
        if (tracker.needsCheck() || phaseTick(20)) {
            tracker.revalidate(level, worldPosition, facing());
        }
        if (!tracker.formed()) {
            setStatus(tracker.status());
            return;
        }
        if (rodLeft <= 0) {
            ItemStack rod = inventory.getStackInSlot(0);
            if (rod.isEmpty()) {
                setStatus(MachineStatus.NO_FUEL);
                return;
            }
            rod.shrink(1);
            if (rod.isEmpty()) {
                inventory.setStackInSlot(0, ItemStack.EMPTY);
            }
            rodLeft = ROD_BURN_TICKS;
            setChanged();
        }
        int h = tankWith(f -> f == KonturFluids.HYDROGEN.source.get());
        int p = tankWith(f -> f == KonturFluids.PLASMA.source.get());
        int w = tankWith(FusionReactorBlockEntity::isWater);
        if (h < 0 || p < 0 || tanks[h].getFluidAmount() < HYDROGEN_PER_TICK || tanks[p].getFluidAmount() < PLASMA_PER_TICK) {
            setStatus(MachineStatus.NO_FLUID);
            return;
        }
        if (w < 0 || tanks[w].getFluidAmount() < WATER_PER_TICK) {
            setStatus(MachineStatus.NO_WATER);
            return;
        }
        if (energy.space() < OUTPUT_PER_TICK) {
            setStatus(MachineStatus.FULL);
            return;
        }
        energy.produce(OUTPUT_PER_TICK);
        tanks[h].drain(HYDROGEN_PER_TICK, FluidAction.EXECUTE);
        tanks[p].drain(PLASMA_PER_TICK, FluidAction.EXECUTE);
        tanks[w].drain(WATER_PER_TICK, FluidAction.EXECUTE);
        rodLeft--;
        setStatus(MachineStatus.RUNNING);
        setChanged();
    }

    @Override
    protected void extraSync(int[] data) {
        data[5] = rodLeft;
        data[6] = ROD_BURN_TICKS;
        data[7] = status == MachineStatus.RUNNING ? OUTPUT_PER_TICK : 0;
    }

    @Override
    protected void saveExtra(CompoundTag tag) {
        tag.putInt("rodLeft", rodLeft);
    }

    @Override
    protected void loadExtra(CompoundTag tag) {
        rodLeft = tag.getInt("rodLeft");
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        if (getBlockState().getValue(MachineBlock.ACTIVE) != active) {
            setActive(active);
        }
    }
}
