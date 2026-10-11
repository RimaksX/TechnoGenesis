package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.block.MultiMachineBlock;
import dev.technogenesis.kontur.machine.MultiLayout;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/** Предмет крупной машины: ставит сразу все части, если места хватает. Главная часть - там, куда нацелен игрок. */
public class MultiMachineItem extends MachineBlockItem {
    private final MultiMachineBlock multi;

    public MultiMachineItem(MultiMachineBlock block, Properties properties) {
        super(block, properties);
        this.multi = block;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip,
                                net.minecraft.world.item.TooltipFlag flag) {
        super.appendHoverText(stack, context, tooltip, flag);
        MultiLayout l = multi.layout;
        tooltip.add(Component.translatable("tooltip.kontur.size", l.w(), l.d(), l.h()).withStyle(ChatFormatting.GRAY));
    }

    @Override
    public InteractionResult place(BlockPlaceContext ctx) {
        Level level = ctx.getLevel();
        Direction facing = ctx.getHorizontalDirection().getOpposite();
        BlockPos master = ctx.getClickedPos();
        List<BlockPos> spots = multi.partPositions(master, facing);
        for (BlockPos p : spots) {
            if (!level.isInWorldBounds(p) || !level.getBlockState(p).canBeReplaced()) {
                if (ctx.getPlayer() != null && !level.isClientSide) {
                    MultiLayout l = multi.layout;
                    ctx.getPlayer().displayClientMessage(
                            Component.translatable("message.kontur.multi_no_space", l.w(), l.d(), l.h()), true);
                }
                return InteractionResult.FAIL;
            }
        }
        if (!level.isClientSide) {
            BlockState base = multi.defaultBlockState().setValue(MachineBlock.FACING, facing);
            for (int i = 0; i < spots.size(); i++) {
                level.setBlock(spots.get(i), base.setValue(MultiMachineBlock.PART, i), 3);
            }
            level.playSound(null, master, multi.defaultBlockState().getSoundType().getPlaceSound(),
                    SoundSource.BLOCKS, 1.0f, 0.9f);
            if (ctx.getPlayer() == null || !ctx.getPlayer().getAbilities().instabuild) {
                ctx.getItemInHand().shrink(1);
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
