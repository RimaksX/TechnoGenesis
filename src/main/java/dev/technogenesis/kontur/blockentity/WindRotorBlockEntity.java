package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Ветряной ротор: 8 FE/t у земли и до 32 FE/t на большой высоте (линейно от Y=64 до Y=192); дождь добавляет 25%,
 * гроза 50%, порывы ветра качают выработку на +-15%. Нужны открытое небо над ротором и не более одной глухой
 * стенки рядом: в тесноте ветра нет.
 */
public class WindRotorBlockEntity extends PassiveGeneratorBlockEntity {
    private boolean exposed;

    public WindRotorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.WIND_ROTOR, pos, state);
    }

    private boolean checkExposure() {
        if (!level.canSeeSky(worldPosition.above())) {
            return false;
        }
        int blocked = 0;
        for (Direction d : Direction.Plane.HORIZONTAL) {
            if (level.getBlockState(worldPosition.relative(d)).isSolidRender(level, worldPosition.relative(d))) {
                blocked++;
            }
        }
        return blocked <= 1;
    }

    /** Мощность ветра для высоты y: 8..32 FE/t. */
    public static int baseOutput(int y) {
        double t = Math.max(0, Math.min(1, (y - 64) / 128.0));
        return (int) Math.round(8 + 24 * t);
    }

    @Override
    protected int output() {
        if (level.getGameTime() % 20 == 0 || rate == 0 && !exposed) {
            exposed = checkExposure();
        }
        if (!exposed) {
            setStatus(MachineStatus.NO_SKY);
            return 0;
        }
        double weather = level.isThundering() ? 1.5 : level.isRaining() ? 1.25 : 1.0;
        double gust = 1.0 + 0.15 * Math.sin(level.getGameTime() / 70.0 + (worldPosition.getX() * 31 + worldPosition.getZ() * 17));
        return Math.max(1, (int) Math.round(baseOutput(worldPosition.getY()) * weather * gust));
    }
}
