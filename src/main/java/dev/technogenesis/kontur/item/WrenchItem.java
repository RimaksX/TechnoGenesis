package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.machine.IoMode;
import dev.technogenesis.kontur.machine.RelativeSide;
import dev.technogenesis.kontur.machine.WrenchMode;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * Ключ для настройки сторон машин. Правый клик по грани переключает режим гнезда (вход, выход, вход и выход, закрыто),
 * с Shift - в обратную сторону; рамка гнезда на модели меняет цвет. Правый клик в воздухе меняет режим ключа:
 * все типы сразу, только предметы, жидкости, энергия или авто-вывод.
 */
public class WrenchItem extends Item {
    private static final String TAG_MODE = "wrench_mode";

    public WrenchItem(Properties properties) {
        super(properties.stacksTo(1));
    }

    public static WrenchMode mode(ItemStack stack) {
        CustomData data = stack.get(DataComponents.CUSTOM_DATA);
        return data == null ? WrenchMode.ALL : WrenchMode.byOrdinal(data.copyTag().getInt(TAG_MODE));
    }

    private static void setMode(ItemStack stack, WrenchMode mode) {
        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> tag.putInt(TAG_MODE, mode.ordinal()));
    }

    public static Component modeName(WrenchMode mode) {
        return Component.translatable("wrench.kontur.mode." + mode.key);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        WrenchMode next = mode(stack).next();
        if (!level.isClientSide) {
            setMode(stack, next);
        }
        player.displayClientMessage(Component.translatable("wrench.kontur.mode_set", modeName(next)), true);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        Level level = ctx.getLevel();
        Player player = ctx.getPlayer();
        if (!(level.getBlockState(ctx.getClickedPos()).getBlock() instanceof MachineBlock)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide || player == null) {
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        if (!(level.getBlockEntity(ctx.getClickedPos()) instanceof MachineBlockEntity be)) {
            return InteractionResult.PASS;
        }
        WrenchMode mode = mode(ctx.getItemInHand());
        if (mode == WrenchMode.EJECT) {
            boolean on = be.toggleEject();
            player.displayClientMessage(Component.translatable(on ? "wrench.kontur.eject_on" : "wrench.kontur.eject_off"), true);
            return InteractionResult.CONSUME;
        }
        RelativeSide side = RelativeSide.of(be.getBlockState().getValue(MachineBlock.FACING), ctx.getClickedFace());
        if (side == RelativeSide.FRONT) {
            player.displayClientMessage(Component.translatable("wrench.kontur.front"), true);
            return InteractionResult.CONSUME;
        }
        IoMode result = be.cycleSide(mode, side, player.isShiftKeyDown());
        if (result == null) {
            player.displayClientMessage(Component.translatable("wrench.kontur.unsupported", modeName(mode)), true);
        } else {
            player.displayClientMessage(Component.translatable("wrench.kontur.side_set",
                    Component.translatable("gui.kontur.side." + side.key),
                    Component.translatable("gui.kontur.mode." + result.key)), true);
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("wrench.kontur.current", modeName(mode(stack))).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("wrench.kontur.hint_side").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("wrench.kontur.hint_shift").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("wrench.kontur.hint_air").withStyle(ChatFormatting.GRAY));
    }
}
