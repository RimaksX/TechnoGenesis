package dev.technogenesis.kontur.machine;

import dev.technogenesis.kontur.block.AssemblyCasingBlock;
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
 * Схема машины, которую игрок собирает сам: коробка из корпусных блоков и портов с камерой внутри (пустой или с деталями,
 * как ротор турбины). Контроллер стоит в центре передней стенки на втором ряду (h = 0) и смотрит наружу; машина уходит
 * от него назад. Координаты (a, b, h): a - вправо от контроллера, b - вглубь, h - вверх. Корпус у каждой машины свой,
 * порты у всех общие. Собрав схему, игрок щёлкает ключом по контроллеру: блоки становятся невидимыми, и контроллер
 * рисует вместо них готовую цельную модель машины.
 */
public final class AssemblyShape {
    /**
     * Термоядерный реактор: коробка 5 x 5 x 4, камера 3 x 3 x 2. Шесть портов на строго заданных местах:
     * питание, вода, пар, водород, плазма, литиевый стержень.
     */
    public static final AssemblyShape FUSION = new AssemblyShape("fusion_reactor", 2, 5, 1, 2, 1, 1, 3, 0, 1,
            () -> KonturBlocks.FUSION_CASING.get(), null,
            new int[][]{{-1, 0, -1}, {2, 2, -1}, {0, 4, -1}, {-2, 2, 0}, {2, 2, 0}, {0, 2, 2}});
    /**
     * Доменная печь: башня 5 x 5 x 6, шахта 3 x 3 x 4. Четыре порта: питание, летка (выход), газ (кислород), загрузка сверху.
     */
    public static final AssemblyShape BLAST = new AssemblyShape("blast_furnace", 2, 5, 1, 4, 1, 1, 3, 0, 3,
            () -> KonturBlocks.FURNACE_CASING.get(), null,
            new int[][]{{-2, 0, -1}, {0, 0, -1}, {1, 4, -1}, {0, 2, 4}});
    /** Паротурбинный зал: коробка 3 x 7 x 3, в тоннеле 1 x 5 x 1 стоят блоки ротора. Три порта: пар, конденсат, ток. */
    public static final AssemblyShape TURBINE = new AssemblyShape("turbine_hall", 1, 7, 1, 1, 0, 1, 5, 0, 0,
            () -> KonturBlocks.TURBINE_CASING.get(), () -> KonturBlocks.TURBINE_ROTOR.get(),
            new int[][]{{0, 1, 1}, {1, 3, -1}, {0, 6, 0}});
    /** Градирня: секция 5 x 3 x 3, воздушный канал 3 x 1 x 1. Три порта: конденсат, вода, питание. */
    public static final AssemblyShape TOWER = new AssemblyShape("cooling_tower", 2, 3, 1, 1, 1, 1, 1, 0, 0,
            () -> KonturBlocks.COOLER_CASING.get(), null,
            new int[][]{{-2, 1, -1}, {2, 1, -1}, {1, 0, -1}});

    public static final List<AssemblyShape> ALL = List.of(FUSION, BLAST, TURBINE, TOWER);

    public final String id;
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
    private final Supplier<Block> interiorBlock;
    private final int[][] portSlots;

    private AssemblyShape(String id, int halfWidth, int depth, int below, int above, int innerHalf, int innerB0,
                          int innerB1, int innerH0, int innerH1, Supplier<Block> casing, Supplier<Block> interiorBlock,
                          int[][] portSlots) {
        this.id = id;
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
        this.interiorBlock = interiorBlock;
        this.portSlots = portSlots;
    }

    /** status - null, если машина собрана; problems - число неверных блоков; first - смещение первой ошибки {a, b, h}. */
    public record Result(MachineStatus status, int problems, int[] first, List<BlockPos> ports) {
        public boolean formed() {
            return status == null;
        }
    }

    /** Позиция, где схема нарушена: wrong - стоит чужой блок (а не просто пусто). */
    public record Gap(BlockPos pos, boolean wrong, boolean port) {
    }

    public static BlockPos at(BlockPos controller, Direction facing, int a, int b, int h) {
        return controller.relative(facing.getClockWise(), a).relative(facing.getOpposite(), b).above(h);
    }

    /** Место порта: на этих позициях стенки стоит только порт, на остальных только корпус. */
    public boolean isPortSlot(int a, int b, int h) {
        for (int[] s : portSlots) {
            if (s[0] == a && s[1] == b && s[2] == h) {
                return true;
            }
        }
        return false;
    }

    public int portCount() {
        return portSlots.length;
    }

    private boolean interior(int a, int b, int h) {
        return Math.abs(a) <= innerHalf && b >= innerB0 && b <= innerB1 && h >= innerH0 && h <= innerH1;
    }

    public int width() {
        return halfWidth * 2 + 1;
    }

    public int height() {
        return below + above + 1;
    }

    /** Подходит ли блок в эту позицию схемы (в состоянии любой сборки). */
    private boolean fits(BlockState state, boolean inside, Block shell, boolean slot) {
        if (inside) {
            return interiorBlock == null ? state.isAir() : state.is(interiorBlock.get());
        }
        return slot ? state.is(KonturBlocks.ASSEMBLY_PORT.get()) : state.is(shell);
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
                    boolean inside = interior(a, b, h);
                    boolean ok = fits(state, inside, shell, isPortSlot(a, b, h));
                    if (ok && state.is(KonturBlocks.ASSEMBLY_PORT.get())) {
                        ports.add(p);
                    }
                    if (!ok) {
                        bad++;
                        if (inside && interiorBlock == null && !state.isAir()) {
                            blocked++;
                        }
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

    /** Все места, где схема не выполнена (для призрачной проекции у игрока с ключом в руке). */
    public List<Gap> gaps(Level level, BlockPos controller, Direction facing) {
        List<Gap> out = new ArrayList<>();
        Block shell = casing.get();
        for (int h = -below; h <= above; h++) {
            for (int b = 0; b < depth; b++) {
                for (int a = -halfWidth; a <= halfWidth; a++) {
                    if (a == 0 && b == 0 && h == 0) {
                        continue;
                    }
                    BlockPos p = at(controller, facing, a, b, h);
                    if (!level.isLoaded(p)) {
                        continue;
                    }
                    BlockState state = level.getBlockState(p);
                    boolean slot = isPortSlot(a, b, h);
                    if (!fits(state, interior(a, b, h), shell, slot)) {
                        boolean hole = state.isAir() || state.canBeReplaced();
                        if (interior(a, b, h) && interiorBlock == null && !state.isAir()) {
                            out.add(new Gap(p, true, false));
                        } else if (hole) {
                            if (!interior(a, b, h) || interiorBlock != null) {
                                out.add(new Gap(p, false, slot));
                            }
                        } else {
                            out.add(new Gap(p, true, slot));
                        }
                    }
                }
            }
        }
        return out;
    }

    /** Переключает у всех блоков схемы (включая контроллер) признак "собрано": невидимые блоки и готовая модель. */
    public void setFormed(Level level, BlockPos controller, Direction facing, boolean formed) {
        for (int h = -below; h <= above; h++) {
            for (int b = 0; b < depth; b++) {
                for (int a = -halfWidth; a <= halfWidth; a++) {
                    BlockPos p = at(controller, facing, a, b, h);
                    if (!level.isLoaded(p)) {
                        continue;
                    }
                    BlockState state = level.getBlockState(p);
                    if (state.hasProperty(AssemblyCasingBlock.FORMED) && state.getValue(AssemblyCasingBlock.FORMED) != formed) {
                        level.setBlock(p, state.setValue(AssemblyCasingBlock.FORMED, formed), 3);
                    }
                }
            }
        }
    }
}
