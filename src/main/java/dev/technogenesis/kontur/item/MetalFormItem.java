package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.material.Form;
import dev.technogenesis.kontur.material.Metal;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Форма переработки с идентификатором целевого металла: медный концентрат не заменит никелевый. */
public class MetalFormItem extends Item {
    private final Metal metal;
    private final Form form;

    public MetalFormItem(Properties properties, Metal metal, Form form) {
        super(properties);
        this.metal = metal;
        this.form = form;
    }

    public Metal metal() {
        return metal;
    }

    public Form form() {
        return form;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.kontur.metal",
                Component.translatable("metal.kontur." + metal.id())).withStyle(ChatFormatting.GRAY));
        if (form == Form.TAILINGS_R1) {
            tooltip.add(Component.translatable("tooltip.kontur.tailings").withStyle(ChatFormatting.DARK_GRAY));
        }
    }
}
