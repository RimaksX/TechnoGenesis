package dev.technogenesis.kontur.machine;

import net.minecraft.core.Direction;

/** Сторона относительно передней грани машины (настройка не ломается при повороте). */
public enum RelativeSide {
    FRONT("front"), BACK("back"), LEFT("left"), RIGHT("right"), TOP("top"), BOTTOM("bottom");

    public final String key;

    RelativeSide(String key) {
        this.key = key;
    }

    /** Левая и правая - с точки зрения игрока, смотрящего на переднюю грань. */
    public static RelativeSide of(Direction facing, Direction side) {
        if (side == Direction.UP) {
            return TOP;
        }
        if (side == Direction.DOWN) {
            return BOTTOM;
        }
        if (side == facing) {
            return FRONT;
        }
        if (side == facing.getOpposite()) {
            return BACK;
        }
        return side == facing.getClockWise() ? LEFT : RIGHT;
    }
}
