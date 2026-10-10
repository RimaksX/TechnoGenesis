package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Генератор без топлива: выработка этого тика зависит только от окружения (солнце, ветер, лава и вода). Если условия
 * не выполнены, подкласс выставляет причину в статус и возвращает 0. Полный буфер - не поломка, а состояние "полный".
 */
public abstract class PassiveGeneratorBlockEntity extends MachineBlockEntity {
    protected int rate;

    protected PassiveGeneratorBlockEntity(MachineKind kind, BlockPos pos, BlockState state) {
        super(kind, pos, state);
    }

    /** Выработка FE на этом тике; при невозможности выставляет статус и возвращает 0. */
    protected abstract int output();

    @Override
    protected void tickMachine() {
        rate = 0;
        int out = output();
        if (out <= 0) {
            return;
        }
        int added = energy.produce(out);
        if (added <= 0) {
            setStatus(MachineStatus.FULL);
            return;
        }
        rate = added;
        setStatus(MachineStatus.RUNNING);
    }

    @Override
    protected void extraSync(int[] data) {
        data[7] = status == MachineStatus.RUNNING ? rate : 0;
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
