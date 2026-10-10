package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Паровая турбина: 128 FE/t. Топливо греет котёл и горит в 10 раз быстрее печи, поэтому 1 уголь даёт около 20 500 FE,
 * вдвое больше твердотопливного генератора. Расход воды 2 мБ на тик работы (у модуля пропорционально скорости);
 * воду принимает бак слева, её можно лить из ведра или подавать трубой. Без воды турбина стоит и ничего не расходует.
 */
public class SteamTurbineBlockEntity extends SolidFuelGeneratorBlockEntity {
    public static final int OUTPUT = 128;
    public static final int SPEEDUP = 10;
    public static final int WATER_PER_TICK = 2;

    public SteamTurbineBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.STEAM_TURBINE, pos, state);
    }

    @Override
    protected int outputPerTick() {
        return OUTPUT;
    }

    @Override
    protected int burnSpeedup() {
        return SPEEDUP;
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        String path = BuiltInRegistries.FLUID.getKey(stack.getFluid()).getPath();
        return path.equals("water") || path.equals("technical_water");
    }

    @Override
    protected boolean ready(int speed) {
        if (tanks[0].getFluidAmount() < WATER_PER_TICK * speed) {
            setStatus(MachineStatus.NO_WATER);
            return false;
        }
        return true;
    }

    @Override
    protected void consume(int speed) {
        tanks[0].drain(WATER_PER_TICK * speed, FluidAction.EXECUTE);
    }
}
