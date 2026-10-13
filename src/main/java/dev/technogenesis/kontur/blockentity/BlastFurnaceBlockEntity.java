package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.machine.AssemblyShape;
import dev.technogenesis.kontur.machine.AssemblyTracker;
import dev.technogenesis.kontur.machine.MachineKind;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;

/** Доменная печь: обычная перерабатывающая машина с рецептами, но работает только пока собрана башня (см. AssemblyShape). */
public class BlastFurnaceBlockEntity extends ProcessingMachineBlockEntity implements AssemblyController {
    private final AssemblyTracker tracker = new AssemblyTracker(AssemblyShape.BLAST);

    public BlastFurnaceBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.BLAST_FURNACE, pos, state);
    }

    @Override
    public boolean isFormed() {
        return tracker.formed();
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
        super.tickMachine();
    }
}
