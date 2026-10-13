package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.blockentity.AssemblyPortBlockEntity;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;

/**
 * Состояние сборки собираемой машины. Схема проверяется раз в секунду; машина работает, только если игрок "замкнул" её ключом
 * (formed) и схема цела (valid). Если схема нарушена, машина распадается обратно на отдельные блоки.
 */
public final class AssemblyTracker {
    private final AssemblyShape shape;
    private boolean formed;
    private boolean valid;
    private MachineStatus status = MachineStatus.NOT_CHECKED;
    private List<BlockPos> ports = List.of();

    public AssemblyTracker(AssemblyShape shape) {
        this.shape = shape;
    }

    public boolean needsCheck() {
        return status == MachineStatus.NOT_CHECKED;
    }

    /** Машина собрана, замкнута и цела: порты работают, цикл идёт. */
    public boolean active() {
        return formed && valid;
    }

    public boolean formed() {
        return formed;
    }

    /** Причина, по которой машина не работает. */
    public MachineStatus status() {
        if (!formed && valid) {
            return MachineStatus.STRUCTURE_READY;
        }
        return status;
    }

    public void revalidate(Level level, BlockPos controller, Direction facing) {
        AssemblyShape.Result r = shape.check(level, controller, facing);
        valid = r.formed();
        status = r.status() == null ? MachineStatus.IDLE : r.status();
        ports = r.ports();
        if (formed && !valid && status != MachineStatus.NOT_CHECKED) {
            setFormed(level, controller, facing, false);       // схема разрушена: машина снова груда блоков
        }
        if (valid) {
            for (BlockPos p : ports) {
                if (level.getBlockEntity(p) instanceof AssemblyPortBlockEntity port) {
                    port.setController(controller);
                }
            }
        }
    }

    /** Игрок щёлкнул ключом: если схема цела, машина собрана (и выглядит как готовая). */
    public boolean tryForm(Level level, BlockPos controller, Direction facing) {
        revalidate(level, controller, facing);
        if (!valid) {
            return false;
        }
        setFormed(level, controller, facing, true);
        return true;
    }

    public void setFormed(Level level, BlockPos controller, Direction facing, boolean value) {
        formed = value;
        shape.setFormed(level, controller, facing, value);
    }

    public void load(boolean formed) {
        this.formed = formed;
    }
}
