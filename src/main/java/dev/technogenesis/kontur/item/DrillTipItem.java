package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.machine.DrillTier;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Наконечник бура: кладётся в склад шахтёра, головка берёт его сама и меняет, когда он сломался. */
public class DrillTipItem extends Item {
    private final DrillTier tier;

    public DrillTipItem(Properties properties, DrillTier tier) {
        super(properties.durability(tier.durability));
        this.tier = tier;
    }

    public DrillTier tier() {
        return tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.drill_tip.durability", tier.durability)
                .withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.kontur.drill_tip.hint").withStyle(ChatFormatting.DARK_GRAY));
    }
}
