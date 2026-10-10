package dev.technogenesis.kontur.client;

import dev.technogenesis.kontur.machine.MachineDefinition;
import dev.technogenesis.kontur.machine.MachineDefinition.EnergyKind;
import dev.technogenesis.kontur.machine.MachineDefinition.TankDef;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.menu.MachineMenu;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.Rect2i;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import dev.technogenesis.kontur.machine.ModuleTier;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.FluidStack;

/**
 * Универсальный экран машины в духе Mekanism: светлое окно с чёрной обводкой, утопленные слоты и шкалы, шкала энергии
 * справа, тёмный экран состояния с зелёным текстом, слева вкладка со слотом модуля форсирования. Стороны настраиваются
 * не здесь, а ключом по граням самой машины.
 * Любой текст перед выводом обрезается по доступной ширине, поэтому надписи не наезжают друг на друга.
 */
public class MachineScreen extends AbstractContainerScreen<MachineMenu> {
    public static final int IMAGE_W = 176;
    public static final int IMAGE_H = 184;

    // шкала энергии (справа)
    static final int ENERGY_X = 160;
    static final int ENERGY_Y = 18;
    // рабочая область (без рамки): x 8..152, y 18..74
    static final int CONTENT_Y = 18;
    // экран состояния
    static final int STATUS_X = 8;
    static final int STATUS_Y = 78;
    static final int STATUS_W = 160;
    static final int STATUS_H = 12;
    static final int TITLE_Y = 6;
    static final int INV_LABEL_Y = 92;

    // вкладка слота модуля слева: держатель 26x26 перекрывает край окна на 4 пикселя, слот лежит на нём
    private static final int HOLDER_X = -22;
    private static final int HOLDER_Y = 34;

    private final MachineDefinition def;

    public MachineScreen(MachineMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        this.def = menu.def;
        this.imageWidth = IMAGE_W;
        this.imageHeight = IMAGE_H;
        this.titleLabelY = TITLE_Y;
        this.inventoryLabelY = INV_LABEL_Y;
    }

    private static String fe(long v) {
        return NumberFormat.getIntegerInstance(Locale.ROOT).format(v).replace(',', ' ');
    }

    public MachineKind kind() {
        return menu.kind;
    }

    /** Подпись, обрезанная по ширине: с многоточием, если не помещается. */
    private String fit(String text, int maxWidth) {
        if (maxWidth <= 0) {
            return "";
        }
        if (font.width(text) <= maxWidth) {
            return text;
        }
        int dots = font.width("...");
        return font.plainSubstrByWidth(text, Math.max(0, maxWidth - dots)) + "...";
    }

    /** Области вне основной панели (вкладка модуля): JEI не должен заходить на них своим списком. */
    public List<Rect2i> extraAreas() {
        List<Rect2i> areas = new ArrayList<>();
        if (def.hasModule()) {
            areas.add(new Rect2i(leftPos + HOLDER_X, topPos + HOLDER_Y, 26, 26));
        }
        return areas;
    }

    // ------------------------------------------------------------------ отрисовка

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
        renderCustomTooltips(g, mouseX, mouseY);
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
        String t = fit(title.getString(), IMAGE_W - 16);
        g.drawString(font, t, (imageWidth - font.width(t)) / 2, TITLE_Y, GuiUtil.TITLE_TEXT, false);
        g.drawString(font, fit(playerInventoryTitle.getString(), IMAGE_W - 16), 8, INV_LABEL_Y, GuiUtil.TITLE_TEXT, false);
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        int x = leftPos;
        int y = topPos;
        GuiUtil.background(g, x, y, imageWidth, imageHeight);
        if (def.hasModule()) {
            GuiUtil.holder(g, x + HOLDER_X, y + HOLDER_Y);
        }
        for (Slot slot : menu.slots) {
            GuiUtil.slot(g, x + slot.x, y + slot.y);
        }
        if (def.energyCapacity > 0) {
            GuiUtil.powerBar(g, x + ENERGY_X, y + ENERGY_Y, menu.energy(), menu.energyCapacity());
        }
        for (int i = 0; i < def.tanks.size(); i++) {
            drawTank(g, x, y, def.tanks.get(i), menu.fluid(i));
        }
        if (def.hasArrow()) {
            GuiUtil.arrow(g, x + def.arrowX, y + def.arrowY, menu.progress(), menu.totalTime());
        }
        if (def.hasFlame()) {
            GuiUtil.flame(g, x + def.flameX, y + def.flameY, menu.burnLeft(), menu.burnTotal());
        }
        if (!def.hasItems() && !def.hasFluids()) {
            drawEnergyInfo(g, x, y);
        }
        drawStatusLine(g, x, y);
    }

    private void drawTank(GuiGraphics g, int x, int y, TankDef t, FluidStack fluid) {
        GuiUtil.gauge(g, x + t.x(), y + t.y(), t.width(), t.height());
        int innerW = t.width() - 2;
        int innerH = t.height() - 2;
        int left = x + t.x() + 1;
        int bottom = y + t.y() + t.height() - 1;
        if (!fluid.isEmpty()) {
            int h = Math.max(1, (int) ((long) innerH * fluid.getAmount() / t.capacity()));
            IClientFluidTypeExtensions ext = IClientFluidTypeExtensions.of(fluid.getFluid());
            TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS)
                    .apply(ext.getStillTexture(fluid));
            int tint = ext.getTintColor(fluid);
            float r = ((tint >> 16) & 255) / 255f;
            float gr = ((tint >> 8) & 255) / 255f;
            float b = (tint & 255) / 255f;
            g.enableScissor(left, bottom - h, left + innerW, bottom);
            for (int yy = bottom - 16; yy > bottom - h - 16; yy -= 16) {
                g.blit(left, yy, 0, innerW, 16, sprite, r, gr, b, 1.0f);
            }
            g.disableScissor();
        }
        g.blitSprite(GuiUtil.TANK_OVERLAY, left, y + t.y() + 1, 16, 50);
    }

    /** Накопитель без слотов: зелёный экран с процентом заряда и точными значениями. */
    private void drawEnergyInfo(GuiGraphics g, int x, int y) {
        int sx = x + 16;
        int sy = y + CONTENT_Y + 2;
        int sw = 128;
        int sh = 52;
        GuiUtil.gauge(g, sx, sy, sw, sh);
        int cx = sx + sw / 2;
        long cap = Math.max(1, menu.energyCapacity());
        int pct = (int) (100L * menu.energy() / cap);
        g.pose().pushPose();
        g.pose().translate(cx, sy + 7, 0);
        g.pose().scale(2f, 2f, 1f);
        g.drawCenteredString(font, pct + "%", 0, 0, GuiUtil.SCREEN_TEXT);
        g.pose().popPose();
        String values = fit(fe(menu.energy()) + " / " + fe(cap) + " FE", sw - 8);
        g.drawString(font, values, cx - font.width(values) / 2, sy + 28, GuiUtil.SCREEN_TEXT, false);
        String rate = fit(Component.translatable("gui.kontur.transfer_rate", fe(def.ratePerTick)).getString(), sw - 8);
        g.drawString(font, rate, cx - font.width(rate) / 2, sy + 39, 0xFF8FA39A, false);
    }

    private void drawStatusLine(GuiGraphics g, int x, int y) {
        GuiUtil.gauge(g, x + STATUS_X, y + STATUS_Y, STATUS_W, STATUS_H);
        MachineStatus st = menu.status();
        int color = st.problem ? 0xFFFF6B5E : (st == MachineStatus.RUNNING || st == MachineStatus.CHARGING
                ? GuiUtil.SCREEN_TEXT : 0xFF8FA39A);
        String rate = rateText(st);
        int inner = STATUS_W - 8;
        int rateW = rate.isEmpty() ? 0 : font.width(rate) + 8;
        String text = fit(st.text().getString(), inner - rateW);
        int ty = y + STATUS_Y + (STATUS_H - 8) / 2;
        g.drawString(font, text, x + STATUS_X + 4, ty, color, false);
        if (!rate.isEmpty() && font.width(text) + rateW <= inner) {
            g.drawString(font, rate, x + STATUS_X + STATUS_W - 4 - font.width(rate), ty, 0xFF9CE8C4, false);
        }
    }

    /** Мощность справа в строке состояния: расход при работе с учётом модуля, выработка у генератора. */
    private String rateText(MachineStatus st) {
        if (def.energyKind == EnergyKind.GENERATOR && menu.rate() > 0) {
            return "+" + fe(menu.rate()) + " FE/t";
        }
        if (def.energyKind == EnergyKind.CONSUMER && st == MachineStatus.RUNNING && def.ratePerTick > 0) {
            return "-" + fe(consumption()) + " FE/t";
        }
        return "";
    }

    /** Расход FE/t с учётом модуля форсирования. */
    private long consumption() {
        return (long) def.ratePerTick * menu.moduleSpeed() * menu.moduleEnergyPercent() / 100;
    }

    // ------------------------------------------------------------------ подсказки

    private void renderCustomTooltips(GuiGraphics g, int mx, int my) {
        int x = leftPos;
        int y = topPos;
        if (def.energyCapacity > 0 && inRect(mx, my, x + ENERGY_X, y + ENERGY_Y, GuiUtil.POWER_W, GuiUtil.POWER_H)) {
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable("gui.kontur.energy"));
            lines.add(Component.translatable("gui.kontur.energy_value", fe(menu.energy()), fe(menu.energyCapacity())));
            if (def.energyKind == EnergyKind.CONSUMER) {
                lines.add(Component.translatable("gui.kontur.energy_rate", fe(consumption())));
            } else if (def.energyKind == EnergyKind.GENERATOR) {
                lines.add(Component.translatable("gui.kontur.generating", fe(menu.rate())));
            }
            g.renderComponentTooltip(font, lines, mx, my);
        }
        for (int i = 0; i < def.tanks.size(); i++) {
            TankDef t = def.tanks.get(i);
            if (inRect(mx, my, x + t.x(), y + t.y(), t.width(), t.height())) {
                FluidStack f = menu.fluid(i);
                Component line = f.isEmpty() ? Component.translatable("gui.kontur.fluid_empty")
                        : Component.translatable("gui.kontur.fluid_value", f.getHoverName(), fe(f.getAmount()), fe(t.capacity()));
                g.renderTooltip(font, line, mx, my);
            }
        }
        if (def.hasArrow() && inRect(mx, my, x + def.arrowX, y + def.arrowY - 2, GuiUtil.ARROW_W, GuiUtil.ARROW_H + 4)
                && menu.totalTime() > 0) {
            g.renderTooltip(font, Component.translatable("gui.kontur.progress", 100 * menu.progress() / menu.totalTime()), mx, my);
        }
        if (def.hasModule() && hoveredSlot != null && hoveredSlot.index == def.moduleSlot()
                && !hoveredSlot.hasItem() && menu.getCarried().isEmpty()) {
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable("gui.kontur.module_slot"));
            for (ModuleTier tier : ModuleTier.values()) {
                lines.add(Component.translatable("gui.kontur.module_line",
                        Component.translatable("item.kontur." + tier.itemId()), tier.speed, tier.energyPercent)
                        .withStyle(ChatFormatting.GRAY));
            }
            g.renderComponentTooltip(font, lines, mx, my);
        }
    }

    private static boolean inRect(int mx, int my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }
}
