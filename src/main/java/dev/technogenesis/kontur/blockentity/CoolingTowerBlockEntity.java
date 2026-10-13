package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.AssemblyShape;
import dev.technogenesis.kontur.machine.AssemblyTracker;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturFluids;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Градирня: контроллер собранной игроком башни 3 x 3 x 6. Принимает конденсат из турбины (до 200 мБ/т), вентиляторы
 * (150 FE/t) остужают его, и на выходе обычная вода; 5 процентов уходит в воздух, так что контур нужно подпитывать водяным
 * насосом. Конденсат из турбины приходит по трубам жидкостей, воду для реактора забирают оттуда же.
 */
public class CoolingTowerBlockEntity extends MachineBlockEntity implements AssemblyController {
    public static final int MAX_FLOW = 200;
    public static final int ENERGY_PER_TICK = 150;
    public static final int RETURN_PERCENT = 95;

    private final AssemblyTracker tracker = new AssemblyTracker(AssemblyShape.TOWER);

    public CoolingTowerBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.COOLING_TOWER, pos, state);
    }

    @Override
    public AssemblyTracker tracker() {
        return tracker;
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        return stack.getFluid() == KonturFluids.CONDENSATE.source.get();
    }

    @Override
    protected void tickMachine() {
        if (tracker.needsCheck() || phaseTick(20)) {
            tracker.revalidate(level, worldPosition, facing());
        }
        if (!tracker.active()) {
            setStatus(tracker.status());
            return;
        }
        int flow = Math.min(tanks[0].getFluidAmount(), MAX_FLOW);
        if (flow <= 0) {
            setStatus(MachineStatus.NO_FLUID);
            return;
        }
        int out = flow * RETURN_PERCENT / 100;
        FluidStack water = new FluidStack(Fluids.WATER, out);
        if (tanks[1].fill(water, FluidAction.SIMULATE) < out) {
            setStatus(MachineStatus.FLUID_OUTPUT_FULL);
            return;
        }
        if (energy.getEnergyStored() < ENERGY_PER_TICK) {
            setStatus(MachineStatus.NO_ENERGY);
            return;
        }
        energy.consume(ENERGY_PER_TICK);
        tanks[0].drain(flow, FluidAction.EXECUTE);
        tanks[1].fill(water, FluidAction.EXECUTE);
        setStatus(MachineStatus.RUNNING);
        setChanged();
    }

    @Override
    protected void saveExtra(net.minecraft.nbt.CompoundTag tag) {
        tag.putBoolean("formed", tracker.formed());
    }

    @Override
    protected void loadExtra(net.minecraft.nbt.CompoundTag tag) {
        tracker.load(tag.getBoolean("formed"));
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        if (getBlockState().getValue(MachineBlock.ACTIVE) != active) {
            setActive(active);
        }
    }
}
