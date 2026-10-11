package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.block.MachineBlock;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Предмет машины: в подсказке показывает, к какой ступени переработки она относится. */
public class MachineBlockItem extends BlockItem {
    private final String stage;

    public MachineBlockItem(MachineBlock block, Item.Properties properties) {
        super(block, properties);
        this.stage = block.kind.stage();
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.stage", Component.translatable("tooltip.kontur.stage." + stage))
                .withStyle(ChatFormatting.GRAY));
    }
}
