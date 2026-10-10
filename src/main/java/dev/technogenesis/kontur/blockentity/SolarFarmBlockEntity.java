package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.SolarFarmBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Солнечная ферма 3x2: шесть плиток под одной энергосистемой. Каждая плитка даёт шестую часть выработки, если над ней
 * чистое небо; закрытые плитки просто не вырабатывают, а если закрыты все - ферма стоит. Принимает те же покрытия.
 */
public class SolarFarmBlockEntity extends SolarPanelBlockEntity {
    private float share;

    public SolarFarmBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.SOLAR_FARM, pos, state);
    }

    @Override
    protected void refreshSky() {
        int clear = 0;
        for (BlockPos p : SolarFarmBlock.partPositions(worldPosition, getBlockState())) {
            if (level.canSeeSky(p.above())) {
                clear++;
            }
        }
        share = clear / (float) SolarFarmBlock.PARTS;
    }

    @Override
    protected float clearShare() {
        return share;
    }
}
