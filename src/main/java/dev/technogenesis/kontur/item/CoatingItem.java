package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.machine.CoatingTier;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Покрытие солнечной панели: ставится в слот покрытия улучшенной панели или солнечной фермы. */
public class CoatingItem extends Item {
    private final CoatingTier tier;

    public CoatingItem(Properties properties, CoatingTier tier) {
        super(properties.stacksTo(1));
        this.tier = tier;
    }

    public CoatingTier tier() {
        return tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.coating.efficiency", tier.percent).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.kontur.coating.hint").withStyle(ChatFormatting.DARK_GRAY));
    }
}
