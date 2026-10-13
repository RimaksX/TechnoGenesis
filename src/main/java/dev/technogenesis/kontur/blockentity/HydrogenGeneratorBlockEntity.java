package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturFluids;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Водородный генератор: 480 FE/t за 30 мБ водорода в тик, то есть 16 FE на мБ. Разделитель воды тратит на литр водорода
 * около 19 FE, так что в целом цикл теряет часть энергии: водород - способ запасти и перенести энергию, а не вечный
 * двигатель. Модуль форсирования ускоряет выработку и расход пропорционально. Без водорода или при полном буфере
 * генератор стоит и ничего не расходует.
 */
public class HydrogenGeneratorBlockEntity extends MachineBlockEntity {
    public static final int OUTPUT_PER_TICK = 480;
    public static final int HYDROGEN_PER_TICK = 30;

    public HydrogenGeneratorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.HYDROGEN_GENERATOR, pos, state);
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        return stack.getFluid() == KonturFluids.HYDROGEN.source.get();
    }

    @Override
    protected boolean interchangeable(FluidStack a, FluidStack b) {
        return acceptsFluid(a) && acceptsFluid(b);
    }

    @Override
    protected void tickMachine() {
        int speed = activeSpeed();
        int need = HYDROGEN_PER_TICK * speed;
        if (tanks[0].getFluidAmount() < need) {
            setStatus(MachineStatus.NO_FLUID);
            return;
        }
        int output = OUTPUT_PER_TICK * speed;
        if (energy.space() < output) {
            setStatus(MachineStatus.FULL);
            return;
        }
        energy.produce(output);
        tanks[0].drain(need, FluidAction.EXECUTE);
        setStatus(MachineStatus.RUNNING);
        setChanged();
    }

    @Override
    protected void extraSync(int[] data) {
        data[7] = status == MachineStatus.RUNNING ? OUTPUT_PER_TICK * activeSpeed() : 0;
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        if (getBlockState().getValue(MachineBlock.ACTIVE) != active) {
            setActive(active);
        }
    }
}
