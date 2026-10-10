package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;

/** Углеродный конденсатор: простой буфер FE ранней игры, уровень заряда виден на передней грани. */
public class CapacitorBlockEntity extends MachineBlockEntity {
    private int lastStored = -1;

    public CapacitorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.CARBON_CAPACITOR, pos, state);
    }

    @Override
    protected void tickMachine() {
        int stored = energy.getEnergyStored();
        if (stored >= energy.getMaxEnergyStored()) {
            setStatus(MachineStatus.FULL);
        } else if (stored != lastStored && lastStored >= 0) {
            setStatus(stored > lastStored ? MachineStatus.CHARGING : MachineStatus.RUNNING);
        } else if (stored == 0) {
            setStatus(MachineStatus.IDLE);
        }
        lastStored = stored;
    }

    /** 0 - пусто, 1..5 - заполнение пятью сегментами. */
    private int chargeLevel() {
        int stored = energy.getEnergyStored();
        if (stored <= 0) {
            return 0;
        }
        return Math.max(1, Math.min(5, (int) Math.ceil(5.0 * stored / energy.getMaxEnergyStored())));
    }

    @Override
    protected void updateBlockState() {
        int lvl = chargeLevel();
        BlockState state = getBlockState();
        if (state.getValue(MachineBlock.CHARGE) != lvl) {
            level.setBlock(worldPosition, state.setValue(MachineBlock.CHARGE, lvl), 3);
        }
    }
}
