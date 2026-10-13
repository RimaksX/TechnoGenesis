package dev.technogenesis.kontur.item;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Деталь для крафта машин: платы, обмотки, приводы и так далее. Подсказка говорит, для чего деталь и как её получить. */
public class ComponentItem extends Item {
    private final String id;

    public ComponentItem(Properties properties, String id) {
        super(properties);
        this.id = id;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.component." + id).withStyle(ChatFormatting.GRAY));
    }
}
