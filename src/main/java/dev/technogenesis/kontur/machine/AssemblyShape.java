package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.registry.KonturBlocks;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Схема машины, которую игрок собирает сам: коробка из корпусных блоков и портов с пустой камерой внутри. Контроллер
 * стоит в центре передней стенки на втором ряду (h = 0) и смотрит наружу; машина уходит от него назад. Координаты
 * (a, b, h): a - вправо от контроллера, b - вглубь, h - вверх. Корпус у каждой машины свой, порты у всех общие.
 */
public final class AssemblyShape {
    /** Термоядерный реактор: коробка 5 x 5 x 4, камера 3 x 3 x 2. */
    public static final AssemblyShape FUSION = new AssemblyShape(2, 5, 1, 2, 1, 1, 3, 0, 1,
            () -> KonturBlocks.FUSION_CASING.get());
    /** Доменная печь: башня 5 x 5 x 6, шахта 3 x 3 x 4. */
    public static final AssemblyShape BLAST = new AssemblyShape(2, 5, 1, 4, 1, 1, 3, 0, 3,
            () -> KonturBlocks.FURNACE_CASING.get());

    public final int halfWidth;
    public final int depth;
    public final int below;
    public final int above;
    private final int innerHalf;
    private final int innerB0;
    private final int innerB1;
    private final int innerH0;
    private final int innerH1;
    private final Supplier<Block> casing;

    private AssemblyShape(int halfWidth, int depth, int below, int above, int innerHalf, int innerB0, int innerB1,
                          int innerH0, int innerH1, Supplier<Block> casing) {
        this.halfWidth = halfWidth;
        this.depth = depth;
        this.below = below;
        this.above = above;
        this.innerHalf = innerHalf;
        this.innerB0 = innerB0;
        this.innerB1 = innerB1;
        this.innerH0 = innerH0;
        this.innerH1 = innerH1;
        this.casing = casing;
    }

    /** status - null, если машина собрана; problems - число неверных блоков; first - смещение первой ошибки {a, b, h}. */
    public record Result(MachineStatus status, int problems, int[] first, List<BlockPos> ports) {
        public boolean formed() {
            return status == null;
        }
    }

    public static BlockPos at(BlockPos controller, Direction facing, int a, int b, int h) {
        return controller.relative(facing.getClockWise(), a).relative(facing.getOpposite(), b).above(h);
    }

    private boolean interior(int a, int b, int h) {
        return Math.abs(a) <= innerHalf && b >= innerB0 && b <= innerB1 && h >= innerH0 && h <= innerH1;
    }

    /** Ширина, глубина и высота коробки для подсказок. */
    public int width() {
        return halfWidth * 2 + 1;
    }

    public int height() {
        return below + above + 1;
    }

    public Result check(Level level, BlockPos controller, Direction facing) {
        int bad = 0;
        int blocked = 0;
        int[] first = null;
        List<BlockPos> ports = new ArrayList<>();
        Block shell = casing.get();
        for (int h = -below; h <= above; h++) {
            for (int b = 0; b < depth; b++) {
                for (int a = -halfWidth; a <= halfWidth; a++) {
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
                    } else if (state.is(KonturBlocks.ASSEMBLY_PORT.get())) {
                        ok = true;
                        ports.add(p);
                    } else {
                        ok = state.is(shell);
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
