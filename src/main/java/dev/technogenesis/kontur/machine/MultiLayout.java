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
    /** Реакторы и аппараты 2x2. */
    public static final MultiLayout SQUARE = new MultiLayout(2, 2, 1);
    /** Длинные аппараты 3x2. */
    public static final MultiLayout WIDE = new MultiLayout(3, 2, 1);
    /** Колонны: одна клетка в основании, две в высоту. */
    public static final MultiLayout TALL = new MultiLayout(1, 1, 2);

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

    /** Клетка с разъёмом на данной стороне; -1, если разъёма нет (лицевая сторона). */
    public int portIndex(RelativeSide side) {
        return switch (side) {
            case LEFT -> index(w - 1, 0, 0);
            case RIGHT -> index(0, 0, 0);
            case BACK, BOTTOM -> index(midColumn(), d - 1, 0);
            case TOP -> index(midColumn(), d - 1, h - 1);
            case FRONT -> -1;
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
