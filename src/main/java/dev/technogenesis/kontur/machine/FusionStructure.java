package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.registry.KonturBlocks;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Схема термоядерного реактора, которую игрок собирает сам: коробка 5 (ширина) x 5 (глубина) x 4 (высота) из корпусных
 * блоков и портов, внутри пустая камера 3 x 3 x 2. Контроллер стоит в центре передней стенки на втором снизу ряду и смотрит
 * наружу; реактор уходит от него назад. Координаты (a, b, h): a - вправо от контроллера, b - вглубь, h - вверх.
 */
public final class FusionStructure {
    public static final int HALF_WIDTH = 2;
    public static final int DEPTH = 5;
    public static final int BELOW = 1;
    public static final int ABOVE = 2;

    private FusionStructure() {
    }

    /** status - null, если реактор собран; problems - число неверных блоков; first - смещение первой ошибки {a, b, h}. */
    public record Result(MachineStatus status, int problems, int[] first, List<BlockPos> ports) {
        public boolean formed() {
            return status == null;
        }
    }

    public static BlockPos at(BlockPos controller, Direction facing, int a, int b, int h) {
        return controller.relative(facing.getClockWise(), a).relative(facing.getOpposite(), b).above(h);
    }

    private static boolean interior(int a, int b, int h) {
        return Math.abs(a) <= 1 && b >= 1 && b <= 3 && h >= 0 && h <= 1;
    }

    public static Result check(Level level, BlockPos controller, Direction facing) {
        int bad = 0;
        int blocked = 0;
        int[] first = null;
        List<BlockPos> ports = new ArrayList<>();
        for (int h = -BELOW; h <= ABOVE; h++) {
            for (int b = 0; b < DEPTH; b++) {
                for (int a = -HALF_WIDTH; a <= HALF_WIDTH; a++) {
                    if (a == 0 && b == 0 && h == 0) {
                        continue;
                    }
                    BlockPos p = at(controller, facing, a, b, h);
                    if (!level.isLoaded(p)) {
                        return new Result(MachineStatus.NOT_CHECKED, 0, new int[]{a, b, h}, List.of());
                    }
                    BlockState state = level.getBlockState(p);
                    boolean ok;
                    if (interior(a, b, h)) {
                        ok = state.isAir();
                        blocked += ok ? 0 : 1;
                    } else if (state.is(KonturBlocks.FUSION_PORT.get())) {
                        ok = true;
                        ports.add(p);
                    } else {
                        ok = state.is(KonturBlocks.FUSION_CASING.get());
                    }
                    if (!ok) {
                        bad++;
                        if (first == null) {
                            first = new int[]{a, b, h};
                        }
                    }
                }
            }
        }
        if (bad == 0) {
            return new Result(null, 0, new int[]{0, 0, 0}, ports);
        }
        return new Result(blocked > 0 ? MachineStatus.STRUCTURE_BLOCKED : MachineStatus.STRUCTURE_MISSING, bad, first, List.of());
    }
}
