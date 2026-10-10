package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.block.SolarFarmBlock;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/** Предмет солнечной фермы: ставит сразу все шесть частей, если места хватает. */
public class SolarFarmItem extends BlockItem {
    public SolarFarmItem(SolarFarmBlock block, Properties properties) {
        super(block, properties);
    }

    @Override
    public InteractionResult place(BlockPlaceContext ctx) {
        Level level = ctx.getLevel();
        Direction facing = ctx.getHorizontalDirection().getOpposite();
        BlockPos master = ctx.getClickedPos();
        List<BlockPos> spots = SolarFarmBlock.partPositions(master, facing);
        for (BlockPos p : spots) {
            if (!level.isInWorldBounds(p) || !level.getBlockState(p).canBeReplaced()) {
                if (ctx.getPlayer() != null && !level.isClientSide) {
                    ctx.getPlayer().displayClientMessage(Component.translatable("message.kontur.farm_no_space"), true);
                }
                return InteractionResult.FAIL;
            }
        }
        if (!level.isClientSide) {
            BlockState base = getBlock().defaultBlockState().setValue(SolarFarmBlock.FACING, facing);
            for (int i = 0; i < spots.size(); i++) {
                level.setBlock(spots.get(i), base.setValue(SolarFarmBlock.PART, i), 3);
            }
            level.playSound(null, master, getBlock().defaultBlockState().getSoundType().getPlaceSound(),
                    SoundSource.BLOCKS, 1.0f, 0.9f);
            if (ctx.getPlayer() == null || !ctx.getPlayer().getAbilities().instabuild) {
                ctx.getItemInHand().shrink(1);
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
