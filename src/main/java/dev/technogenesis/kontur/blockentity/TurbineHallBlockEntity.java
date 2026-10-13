package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.AssemblyShape;
import dev.technogenesis.kontur.machine.AssemblyTracker;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturFluids;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Паротурбинный зал: контроллер собранной игроком коробки 3 x 7 x 3 с тоннелем для ротора. Пар из реактора (по газовым трубам
 * в любой порт) вращает ротор: до 160 мБ/т, по 80 FE на мБ, то есть до 12 800 FE/t. Отработавший пар становится конденсатом и
 * уходит в бак слева направо в градирню. Нет места под конденсат или энергию - зал стоит и ничего не расходует.
 */
public class TurbineHallBlockEntity extends MachineBlockEntity implements AssemblyController {
    public static final int MAX_STEAM_PER_TICK = 160;
    public static final int FE_PER_MB = 80;

    private final AssemblyTracker tracker = new AssemblyTracker(AssemblyShape.TURBINE);
    private int lastOutput;

    public TurbineHallBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.TURBINE_HALL, pos, state);
    }

    @Override
    public boolean isFormed() {
        return tracker.formed();
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        return stack.getFluid() == KonturFluids.STEAM.source.get();
    }

    @Override
    protected void tickMachine() {
        lastOutput = 0;
        if (tracker.needsCheck() || phaseTick(20)) {
            tracker.revalidate(level, worldPosition, facing());
        }
        if (!tracker.formed()) {
            setStatus(tracker.status());
            return;
        }
        int steam = Math.min(tanks[0].getFluidAmount(), MAX_STEAM_PER_TICK);
        if (steam <= 0) {
            setStatus(MachineStatus.NO_FLUID);
            return;
        }
        steam = Math.min(steam, energy.space() / FE_PER_MB);
        if (steam <= 0) {
            setStatus(MachineStatus.FULL);
            return;
        }
        FluidStack condensate = new FluidStack(KonturFluids.CONDENSATE.source.get(), steam);
        steam = Math.min(steam, tanks[1].fill(condensate, FluidAction.SIMULATE));
        if (steam <= 0) {
            setStatus(MachineStatus.FLUID_OUTPUT_FULL);
            return;
        }
        tanks[0].drain(steam, FluidAction.EXECUTE);
        tanks[1].fill(condensate.copyWithAmount(steam), FluidAction.EXECUTE);
        lastOutput = steam * FE_PER_MB;
        energy.produce(lastOutput);
        setStatus(MachineStatus.RUNNING);
        setChanged();
    }

    @Override
    protected void extraSync(int[] data) {
        data[7] = lastOutput;
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        if (getBlockState().getValue(MachineBlock.ACTIVE) != active) {
            setActive(active);
        }
    }
}
