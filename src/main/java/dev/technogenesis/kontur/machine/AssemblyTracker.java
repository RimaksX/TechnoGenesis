package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.blockentity.AssemblyPortBlockEntity;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;

/** Состояние сборки собираемой машины: цела ли схема, чем недовольна и где порты. Проверяется контроллером раз в секунду. */
public final class AssemblyTracker {
    private final AssemblyShape shape;
    private boolean formed;
    private MachineStatus status = MachineStatus.NOT_CHECKED;
    private List<BlockPos> ports = List.of();

    public AssemblyTracker(AssemblyShape shape) {
        this.shape = shape;
    }

    public boolean needsCheck() {
        return status == MachineStatus.NOT_CHECKED;
    }

    public boolean formed() {
        return formed;
    }

    /** Причина, по которой машина не собрана. */
    public MachineStatus status() {
        return status;
    }

    public void revalidate(Level level, BlockPos controller, Direction facing) {
        AssemblyShape.Result r = shape.check(level, controller, facing);
        formed = r.formed();
        status = r.status() == null ? MachineStatus.IDLE : r.status();
        ports = r.ports();
        for (BlockPos p : ports) {
            if (level.getBlockEntity(p) instanceof AssemblyPortBlockEntity port) {
                port.setController(controller);
            }
        }
    }
}
