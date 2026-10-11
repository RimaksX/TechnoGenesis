package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FluidState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Водяной насос: 16 FE/t и 20 мБ воды за тик. Водозабор ищет источник воды в объёме 5x5 по сторонам и до трёх блоков
 * вниз от насоса (сам насос можно ставить на берегу или над водой). Источник не расходуется. Вода уходит в бак
 * справа от окна, оттуда её забирают жидкостные трубы или соседние баки.
 */
public class WaterPumpBlockEntity extends MachineBlockEntity {
    public static final int WATER_PER_TICK = 20;
    public static final int ENERGY_PER_TICK = 16;
    private static final int RADIUS = 2;
    private static final int DEPTH = 3;

    private boolean hasWater;

    public WaterPumpBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.WATER_PUMP, pos, state);
    }

    private boolean scan() {
        for (int dy = -DEPTH; dy <= 0; dy++) {
            for (int dx = -RADIUS; dx <= RADIUS; dx++) {
                for (int dz = -RADIUS; dz <= RADIUS; dz++) {
                    FluidState fs = level.getFluidState(worldPosition.offset(dx, dy, dz));
                    if (fs.is(FluidTags.WATER) && fs.isSource()) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    @Override
    protected void tickMachine() {
        if (phaseTick(20)) {
            hasWater = scan();
        }
        if (!hasWater) {
            setStatus(MachineStatus.NO_WATER);
            return;
        }
        int speed = activeSpeed();
        FluidStack water = new FluidStack(net.minecraft.world.level.material.Fluids.WATER, WATER_PER_TICK * speed);
        if (tanks[0].fill(water, FluidAction.SIMULATE) < water.getAmount()) {
            setStatus(MachineStatus.FLUID_OUTPUT_FULL);
            return;
        }
        int cost = ENERGY_PER_TICK * speed * activeEnergyPercent() / 100;
        if (energy.getEnergyStored() < cost) {
            setStatus(MachineStatus.NO_ENERGY);
            return;
        }
        energy.consume(cost);
        tanks[0].fill(water, FluidAction.EXECUTE);
        setStatus(MachineStatus.RUNNING);
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        BlockState state = getBlockState();
        if (state.hasProperty(MachineBlock.ACTIVE) && state.getValue(MachineBlock.ACTIVE) != active) {
            level.setBlock(worldPosition, state.setValue(MachineBlock.ACTIVE, active), 3);
        }
    }
}
