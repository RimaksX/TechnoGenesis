package dev.technogenesis.kontur.machine;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;

/**
 * Раскладка крупной машины: w клеток вдоль левой стороны (по часовой от направления лица), d клеток вглубь, h вверх.
 * Номер части = y * (w * d) + r * w + c; часть 0 - главная (передний правый нижний угол, как его видит игрок),
 * только в ней блок-сущность. На каждой стороне один разъём в назначенной клетке: клетки без разъёма к трубам и
 * кабелям не подключаются.
 */
public record MultiLayout(int w, int d, int h) {
    /** Больше всего частей у машины 3x2x2 и 2x3x2. */
    public static final int MAX_PARTS = 12;

    private static final java.util.Map<Integer, MultiLayout> CACHE = new java.util.concurrent.ConcurrentHashMap<>();

    /** Раскладка w x d x h; одинаковые размеры делят один экземпляр. */
    public static MultiLayout of(int w, int d, int h) {
        return CACHE.computeIfAbsent(w * 10000 + d * 100 + h, k -> new MultiLayout(w, d, h));
    }

    public int parts() {
        return w * d * h;
    }

    public int index(int c, int r, int y) {
        return y * (w * d) + r * w + c;
    }

    public int column(int idx) {
        return idx % w;
    }

    public int row(int idx) {
        return (idx / w) % d;
    }

    public int layer(int idx) {
        return idx / (w * d);
    }

    /** Центральный столбец (для чётной ширины - левее центра): сюда выводятся разъёмы зад/верх/низ и индикатор. */
    private int midColumn() {
        return (w - 1) / 2;
    }

    /** Клетка с разъёмом на данной стороне. */
    public int portIndex(RelativeSide side) {
        return switch (side) {
            case LEFT -> index(w - 1, 0, 0);
            case RIGHT -> index(0, 0, 0);
            case BACK, BOTTOM -> index(midColumn(), d - 1, 0);
            case TOP -> index(midColumn(), d - 1, h - 1);
            case FRONT -> index(midColumn(), 0, 0);
        };
    }

    /** Клетка с индикатором состояния на передней грани. */
    public int lightIndex() {
        return index(midColumn(), 0, h - 1);
    }

    public BlockPos cell(BlockPos master, Direction facing, int idx) {
        return master.relative(facing.getClockWise(), column(idx)).relative(facing.getOpposite(), row(idx))
                .above(layer(idx));
    }

    public BlockPos masterOf(BlockPos pos, Direction facing, int idx) {
        return pos.relative(facing.getCounterClockWise(), column(idx)).relative(facing, row(idx)).below(layer(idx));
    }

    public List<BlockPos> cells(BlockPos master, Direction facing) {
        List<BlockPos> out = new ArrayList<>(parts());
        for (int i = 0; i < parts(); i++) {
            out.add(cell(master, facing, i));
        }
        return out;
    }
}
