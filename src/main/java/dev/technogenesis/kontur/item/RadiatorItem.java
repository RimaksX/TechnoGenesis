package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.machine.RadiatorTier;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Радиатор: ставится в слот радиатора на вкладке машины и отводит тепло модуля форсирования. */
public class RadiatorItem extends Item {
    private final RadiatorTier tier;

    public RadiatorItem(Properties properties, RadiatorTier tier) {
        super(properties.stacksTo(1));
        this.tier = tier;
    }

    public RadiatorTier tier() {
        return tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.radiator.cooling", tier.cooling).withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.translatable("tooltip.kontur.radiator.hint").withStyle(ChatFormatting.DARK_GRAY));
    }
}
