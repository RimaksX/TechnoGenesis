package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.machine.ModuleTier;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Модуль форсирования: вставляется в слот модуля машины и ускоряет её цикл. */
public class ModuleItem extends Item {
    private final ModuleTier tier;

    public ModuleItem(Properties properties, ModuleTier tier) {
        super(properties.stacksTo(1));
        this.tier = tier;
    }

    public ModuleTier tier() {
        return tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.module.speed", tier.speed).withStyle(ChatFormatting.GREEN));
        tooltip.add(Component.translatable("tooltip.kontur.module.energy", tier.energyPercent).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.kontur.module.heat", tier.heatPerTick, tier.coolingNeeded())
                .withStyle(ChatFormatting.RED));
        tooltip.add(Component.translatable("tooltip.kontur.module.hint").withStyle(ChatFormatting.DARK_GRAY));
    }
}
