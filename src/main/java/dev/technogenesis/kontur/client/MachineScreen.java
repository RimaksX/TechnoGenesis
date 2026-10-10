package dev.technogenesis.kontur.client;

import dev.technogenesis.kontur.machine.IoMode;
import dev.technogenesis.kontur.machine.MachineDefinition;
import dev.technogenesis.kontur.machine.MachineDefinition.EnergyKind;
import dev.technogenesis.kontur.machine.MachineDefinition.TankDef;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.machine.RelativeSide;
import dev.technogenesis.kontur.machine.SideConfig;
import dev.technogenesis.kontur.machine.TransferType;
import dev.technogenesis.kontur.menu.MachineMenu;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.sounds.SoundEvents;
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
 * Универсальный экран машины: тёмная панель, слоты входа и выхода разного цвета, шкала энергии справа, экран
 * состояния, слева вкладка со слотом модуля форсирования. Стороны настраиваются ключом по граням машины, не в меню.
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

    // вкладка слота модуля слева: держатель шириной 29 перекрывает край окна на 4 пикселя; слот и шкала нагрева лежат на нём
    private static final int HOLDER_X = -25;
    private static final int HOLDER_Y = 34;

    // панель настройки сторон перекрывает рабочую область окна: сверху кнопки типов, слева развёртка куба из пяти клеток
    // (верх, низ, право, лево, зад; лицевой нет), справа пояснение цветов и кнопка авто-вывода
    private static final int CFG_X = 8;
    private static final int CFG_Y = 16;
    private static final int CFG_W = 160;
    private static final int CFG_H = 84;
    private static final int TB_X = 12;
    private static final int TB_Y = 19;
    private static final int TB_W = 24;
    private static final int TB_H = 11;
    private static final int TB_STEP = 26;
    private static final int NET_X = 14;
    private static final int NET_Y = 38;
    private static final int CELL = 18;
    private static final int NET_STEP = 20;
    private static final int LG_X = 102;
    private static final int EJ_X = 102;
    private static final int EJ_Y = 88;
    private static final int EJ_W = 40;
    private static final int EJ_H = 10;
    private static final RelativeSide[] NET_SIDES = {RelativeSide.TOP, RelativeSide.LEFT, RelativeSide.RIGHT,
            RelativeSide.BACK, RelativeSide.BOTTOM};
    /** Колонка и строка клетки в развёртке: верх над лицом, низ под ним, лево и право по бокам, зад справа от права. */
    private static final int[][] NET_POS = {{1, 0}, {0, 1}, {2, 1}, {3, 1}, {1, 2}};
    private static final TransferType[] ROW_ORDER = {TransferType.ITEMS, TransferType.OUT1, TransferType.OUT2,
            TransferType.OUT3, TransferType.FLUIDS, TransferType.ENERGY};
    /** Только клиент: какой тип сейчас настраивает панель. */
    private TransferType cfgType;

    private static final net.minecraft.resources.ResourceLocation WRENCH_ICON =
            net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(dev.technogenesis.kontur.Kontur.MODID,
                    "textures/item/wrench.png");

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
        if (def.tabSlot() >= 0) {
            areas.add(new Rect2i(leftPos + HOLDER_X, topPos + HOLDER_Y, 29, holderHeight()));
        }
        if (hasConfigTab()) {
            areas.add(new Rect2i(leftPos + HOLDER_X, topPos + configTabY(), 29, CFG_TAB_H));
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
        if (menu.configOpen()) {
            return;
        }
        g.drawString(font, fit(playerInventoryTitle.getString(), IMAGE_W - 16), 8, INV_LABEL_Y, GuiUtil.LABEL_TEXT, false);
        // номера выходов: у каждого свои грани, которые настраиваются ключом
        int[] outs = def.outputSlots();
        for (int i = 0; outs.length >= 2 && i < outs.length && i < 3; i++) {
            Slot sl = menu.slots.get(outs[i]);
            g.pose().pushPose();
            g.pose().translate(sl.x + 1, sl.y + 1, 300);
            g.pose().scale(0.6f, 0.6f, 1f);
            g.drawString(font, String.valueOf(i + 1), 0, 0, 0xFFE8C46A, true);
            g.pose().popPose();
        }
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        int x = leftPos;
        int y = topPos;
        // вкладка рисуется под окном: правые 4 пикселя прячутся под его рамкой и стык выходит ровным
        if (def.tabSlot() >= 0) {
            GuiUtil.holder(g, x + HOLDER_X, y + HOLDER_Y, holderHeight());
        }
        if (hasConfigTab()) {
            GuiUtil.holder(g, x + HOLDER_X, y + configTabY(), CFG_TAB_H);
        }
        GuiUtil.background(g, x, y, imageWidth, imageHeight);
        for (Slot slot : menu.slots) {
            if (!slot.isActive()) {
                continue;
            }
            MachineDefinition.SlotRole role = slot.index < def.slots.size() ? def.slots.get(slot.index).role() : null;
            GuiUtil.slot(g, x + slot.x, y + slot.y, role);
        }
        if (def.hasModule() && (menu.slots.get(def.moduleSlot()).hasItem() || menu.heatPercent() > 0)) {
            GuiUtil.heatBar(g, x + HOLDER_X + 5, y + HOLDER_Y + heatBarOffset(), menu.heatPercent());
        }
        if (hasConfigTab()) {
            boolean open = menu.configOpen();
            if (open || inRect(mouseX, mouseY, x + HOLDER_X + 4, y + configTabY() + 4, 20, 18)) {
                g.fill(x + HOLDER_X + 4, y + configTabY() + 4, x + HOLDER_X + 24, y + configTabY() + 22,
                        open ? 0x40F5C542 : 0x30FFFFFF);
            }
            g.blit(WRENCH_ICON, x + HOLDER_X + 6, y + configTabY() + 5, 0f, 0f, 16, 16, 16, 16);
        }
        if (menu.configOpen()) {
            drawConfig(g, x, y, mouseX, mouseY);
            return;
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

    /**
     * Накопитель или источник без слотов: зелёный экран. У накопителя крупно процент заряда, у источника крупно
     * текущая выработка; ниже точные значения и предел.
     */
    private void drawEnergyInfo(GuiGraphics g, int x, int y) {
        int sx = x + 16;
        int sy = y + CONTENT_Y + 2;
        int sw = 128;
        int sh = 52;
        GuiUtil.gauge(g, sx, sy, sw, sh);
        int cx = sx + sw / 2;
        long cap = Math.max(1, menu.energyCapacity());
        boolean source = def.energyKind == EnergyKind.GENERATOR;
        String big = source ? (menu.rate() > 0 ? "+" + fe(menu.rate()) : "0") : (int) (100L * menu.energy() / cap) + "%";
        g.pose().pushPose();
        g.pose().translate(cx, sy + 7, 0);
        g.pose().scale(2f, 2f, 1f);
        g.drawCenteredString(font, big, 0, 0, GuiUtil.SCREEN_TEXT);
        g.pose().popPose();
        String values = fit(fe(menu.energy()) + " / " + fe(cap) + " FE", sw - 8);
        g.drawString(font, values, cx - font.width(values) / 2, sy + 28, GuiUtil.SCREEN_TEXT, false);
        String second = source
                ? Component.translatable("gui.kontur.gen_peak", fe(def.ratePerTick)).getString()
                : Component.translatable("gui.kontur.transfer_rate", fe(def.ratePerTick)).getString();
        String rate = fit(second, sw - 8);
        g.drawString(font, rate, cx - font.width(rate) / 2, sy + 39, 0xFF8FA39A, false);
    }

    private void drawStatusLine(GuiGraphics g, int x, int y) {
        GuiUtil.gauge(g, x + STATUS_X, y + STATUS_Y, STATUS_W, STATUS_H);
        MachineStatus st = menu.status();
        int color = st.problem || menu.overheated() ? 0xFFFF6B5E : (st == MachineStatus.RUNNING || st == MachineStatus.CHARGING
                ? GuiUtil.SCREEN_TEXT : 0xFF8FA39A);
        String rate = rateText(st);
        int inner = STATUS_W - 8;
        int rateW = rate.isEmpty() ? 0 : font.width(rate) + 8;
        String text = fit(st.text().getString(), inner - rateW);
        int ty = y + STATUS_Y + (STATUS_H - 8) / 2;
        g.drawString(font, text, x + STATUS_X + 4, ty, color, false);
        if (!rate.isEmpty() && font.width(text) + rateW <= inner) {
            g.drawString(font, rate, x + STATUS_X + STATUS_W - 4 - font.width(rate),
                    ty, menu.overheated() ? 0xFFFF6B5E : 0xFF9CE8C4, false);
        }
    }

    /** Мощность справа в строке состояния: расход при работе с учётом модуля, выработка у генератора. */
    private String rateText(MachineStatus st) {
        if (menu.overheated()) {
            return Component.translatable("gui.kontur.overheat").getString();
        }
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
        if (hasConfigTab() && inRect(mx, my, x + HOLDER_X + 4, y + configTabY() + 4, 20, 18)) {
            g.renderComponentTooltip(font, List.of(Component.translatable("gui.kontur.config_tab"),
                    Component.translatable("gui.kontur.config_tab_hint").withStyle(ChatFormatting.GRAY)), mx, my);
        }
        if (menu.configOpen()) {
            renderConfigTooltips(g, x, y, mx, my);
            return;
        }
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
                List<Component> lines = new ArrayList<>();
                lines.add(line);
                if (!f.isEmpty()) {
                    lines.add(Component.translatable("gui.kontur.void_tank").withStyle(ChatFormatting.DARK_GRAY));
                }
                g.renderComponentTooltip(font, lines, mx, my);
            }
        }
        if (def.hasArrow() && inRect(mx, my, x + def.arrowX, y + def.arrowY - 2, GuiUtil.ARROW_W, GuiUtil.ARROW_H + 4)
                && menu.totalTime() > 0) {
            g.renderTooltip(font, Component.translatable("gui.kontur.progress", 100 * menu.progress() / menu.totalTime()), mx, my);
        }
        if (def.hasModule() && inRect(mx, my, x + HOLDER_X + 5, y + HOLDER_Y + heatBarOffset(), 18, 6)) {
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable("gui.kontur.heat", menu.heatPercent()));
            lines.add(Component.translatable("gui.kontur.cooling", menu.cooling()).withStyle(ChatFormatting.GRAY));
            if (menu.overheated()) {
                lines.add(Component.translatable("gui.kontur.overheat_hint").withStyle(ChatFormatting.RED));
            }
            g.renderComponentTooltip(font, lines, mx, my);
        }
        if (def.hasCoating() && hoveredSlot != null && hoveredSlot.index == def.coatingSlot()
                && !hoveredSlot.hasItem() && menu.getCarried().isEmpty()) {
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable("gui.kontur.coating_slot"));
            for (dev.technogenesis.kontur.machine.CoatingTier tier : dev.technogenesis.kontur.machine.CoatingTier.values()) {
                lines.add(Component.translatable("gui.kontur.coating_line",
                        Component.translatable("item.kontur." + tier.itemId()), tier.percent)
                        .withStyle(ChatFormatting.GRAY));
            }
            g.renderComponentTooltip(font, lines, mx, my);
        }
        if (hoveredSlot != null && !hoveredSlot.hasItem() && menu.getCarried().isEmpty()
                && hoveredSlot.index < def.slots.size() && def.outputSlots().length >= 2) {
            int[] outs = def.outputSlots();
            for (int i = 0; i < outs.length && i < 3; i++) {
                if (outs[i] == hoveredSlot.index) {
                    g.renderComponentTooltip(font, List.of(Component.translatable("gui.kontur.out_slot", i + 1),
                            Component.translatable("gui.kontur.out_slot_hint", i + 1).withStyle(ChatFormatting.GRAY)), mx, my);
                }
            }
        }
        if (def.hasCooler() && hoveredSlot != null && hoveredSlot.index == def.coolerSlot()
                && !hoveredSlot.hasItem() && menu.getCarried().isEmpty()) {
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable("gui.kontur.cooler_slot"));
            for (dev.technogenesis.kontur.machine.RadiatorTier tier : dev.technogenesis.kontur.machine.RadiatorTier.values()) {
                lines.add(Component.translatable("gui.kontur.cooler_line",
                        Component.translatable("item.kontur." + tier.itemId()), tier.cooling)
                        .withStyle(ChatFormatting.GRAY));
            }
            g.renderComponentTooltip(font, lines, mx, my);
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

    // ------------------------------------------------------------------ панель настройки сторон

    private static final int CFG_TAB_H = 26;

    /** Есть ли у машины хоть одна грань с разъёмом (у фермы разъёмы особые, панель ей не нужна). */
    private boolean hasConfigTab() {
        for (RelativeSide s : NET_SIDES) {
            if (menu.kind.hasPort(s)) {
                return true;
            }
        }
        return false;
    }

    /** Вкладка настройки стоит под вкладкой модуля или покрытия, а без неё - на её месте. */
    private int configTabY() {
        return def.tabSlot() >= 0 ? HOLDER_Y + holderHeight() + 3 : HOLDER_Y;
    }

    private List<TransferType> configRows() {
        List<TransferType> rows = new ArrayList<>();
        for (TransferType t : ROW_ORDER) {
            if (def.supports(t)) {
                rows.add(t);
            }
        }
        return rows;
    }

    /** Выбранный тип: по умолчанию первый из имеющихся у машины. */
    private TransferType selectedType() {
        List<TransferType> rows = configRows();
        if (cfgType == null || !rows.contains(cfgType)) {
            cfgType = rows.isEmpty() ? TransferType.ENERGY : rows.get(0);
        }
        return cfgType;
    }

    /** Режимы, которые для типа вообще бывают: для входов и выходов предметов только открыто или закрыто. */
    private static IoMode[] modesOf(TransferType t) {
        if (t == TransferType.ITEMS) {
            return new IoMode[]{IoMode.NONE, IoMode.INPUT};
        }
        if (t.isOutputChannel()) {
            return new IoMode[]{IoMode.NONE, IoMode.OUTPUT};
        }
        return new IoMode[]{IoMode.NONE, IoMode.INPUT, IoMode.OUTPUT, IoMode.ALL};
    }

    private static int cellColor(IoMode mode) {
        return 0xFF000000 | switch (mode) {
            case NONE -> 0x2A2F3B;
            case INPUT -> MachinePortRenderer.INPUT;
            case OUTPUT -> MachinePortRenderer.OUTPUT;
            case ALL -> MachinePortRenderer.BOTH;
        };
    }

    private static int withAlpha(int rgb) {
        return 0xFF000000 | rgb;
    }

    private int netX(int i) {
        return NET_X + NET_POS[i][0] * NET_STEP;
    }

    private int netY(int i) {
        return NET_Y + NET_POS[i][1] * NET_STEP;
    }

    private void drawConfig(GuiGraphics g, int x, int y, int mx, int my) {
        GuiUtil.gauge(g, x + CFG_X, y + CFG_Y, CFG_W, CFG_H);
        SideConfig cfg = menu.sides();
        TransferType sel = selectedType();
        // кнопки типов
        List<TransferType> rows = configRows();
        for (int i = 0; i < rows.size(); i++) {
            TransferType t = rows.get(i);
            int bx = x + TB_X + i * TB_STEP;
            boolean on = t == sel;
            drawButton(g, bx, y + TB_Y, TB_W, TB_H, on ? 0xFF4F6A9A : 0xFF353B4A, !on && inRect(mx, my, bx, y + TB_Y, TB_W, TB_H));
            TabIcons.draw(g, bx, y + TB_Y, TB_W, TB_H, t, on);
        }
        // развёртка куба; лицевая сторона стоит в центре тёмной клеткой, чтобы форма читалась
        drawCell(g, x + NET_X + NET_STEP, y + NET_Y + NET_STEP, 0xFF171A21, false, "");
        for (int i = 0; i < NET_SIDES.length; i++) {
            RelativeSide side = NET_SIDES[i];
            boolean port = menu.kind.hasPort(side);
            int cx = x + netX(i);
            int cy = y + netY(i);
            String letter = Component.translatable("gui.kontur.letter." + side.key).getString();
            drawCell(g, cx, cy, port ? cellColor(cfg.get(sel, side)) : 0xFF171A21, port && inRect(mx, my, cx, cy, CELL, CELL),
                    port ? letter : "");
        }
        // справа: что означают цвета для этого типа
        g.drawString(font, fit(Component.translatable("gui.kontur.row." + sel.key).getString(), CFG_X + CFG_W - LG_X - 4),
                x + LG_X, y + 36, 0xFFF5C542, false);
        IoMode[] modes = modesOf(sel);
        for (int i = 0; i < modes.length; i++) {
            int ly = y + 48 + i * 10;
            g.fill(x + LG_X, ly, x + LG_X + 8, ly + 8, 0xFF10131A);
            g.fill(x + LG_X + 1, ly + 1, x + LG_X + 7, ly + 7, cellColor(modes[i]));
            g.drawString(font, fit(Component.translatable("gui.kontur.mode." + modes[i].key).getString(), 54),
                    x + LG_X + 12, ly, 0xFFC4CCDA, false);
        }
        // авто-вывод
        boolean eject = cfg.ejectItems || cfg.ejectFluids;
        drawButton(g, x + EJ_X, y + EJ_Y, EJ_W, EJ_H, eject ? 0xFF3C7A56 : 0xFF3A404E, inRect(mx, my, x + EJ_X, y + EJ_Y, EJ_W, EJ_H));
        String label = fit(Component.translatable("gui.kontur.eject_short").getString(), EJ_W - 4);
        g.drawString(font, label, x + EJ_X + (EJ_W - font.width(label)) / 2, y + EJ_Y + 1, eject ? 0xFFD8F5E4 : 0xFF9AA4B8, false);
    }

    /** Клетка развёртки: контур, цвет режима, фаска (верх и лево светлее, низ и право темнее) и буква грани. */
    private void drawCell(GuiGraphics g, int x, int y, int color, boolean hover, String letter) {
        int light = withAlpha(MachinePortRenderer.shade(color & 0xFFFFFF, 1.18f));
        int dark = withAlpha(MachinePortRenderer.shade(color & 0xFFFFFF, 0.78f));
        g.fill(x, y, x + CELL, y + CELL, 0xFF10131A);
        g.fill(x + 1, y + 1, x + CELL - 1, y + CELL - 1, color);
        g.fill(x + 1, y + 1, x + CELL - 1, y + 2, light);
        g.fill(x + 1, y + 1, x + 2, y + CELL - 1, light);
        g.fill(x + 1, y + CELL - 2, x + CELL - 1, y + CELL - 1, dark);
        g.fill(x + CELL - 2, y + 1, x + CELL - 1, y + CELL - 1, dark);
        if (hover) {
            g.fill(x + 1, y + 1, x + CELL - 1, y + CELL - 1, 0x38FFFFFF);
        }
        if (!letter.isEmpty()) {
            boolean closed = (color & 0xFFFFFF) == 0x2A2F3B;
            g.drawString(font, letter, x + (CELL - font.width(letter)) / 2, y + 5, closed ? 0xFF7C879C : 0xFF1A1E28, false);
        }
    }

    private static void drawButton(GuiGraphics g, int x, int y, int w, int h, int color, boolean hover) {
        int light = withAlpha(MachinePortRenderer.shade(color & 0xFFFFFF, 1.2f));
        int dark = withAlpha(MachinePortRenderer.shade(color & 0xFFFFFF, 0.75f));
        g.fill(x, y, x + w, y + h, 0xFF10131A);
        g.fill(x + 1, y + 1, x + w - 1, y + h - 1, color);
        g.fill(x + 1, y + 1, x + w - 1, y + 2, light);
        g.fill(x + 1, y + h - 2, x + w - 1, y + h - 1, dark);
        if (hover) {
            g.fill(x + 1, y + 1, x + w - 1, y + h - 1, 0x30FFFFFF);
        }
    }

    private void renderConfigTooltips(GuiGraphics g, int x, int y, int mx, int my) {
        if (inRect(mx, my, x + EJ_X, y + EJ_Y, EJ_W, EJ_H)) {
            g.renderComponentTooltip(font, List.of(Component.translatable("gui.kontur.eject"),
                    Component.translatable("gui.kontur.eject_hint").withStyle(ChatFormatting.GRAY)), mx, my);
            return;
        }
        List<TransferType> rows = configRows();
        for (int i = 0; i < rows.size(); i++) {
            if (inRect(mx, my, x + TB_X + i * TB_STEP, y + TB_Y, TB_W, TB_H)) {
                g.renderTooltip(font, Component.translatable("gui.kontur.row." + rows.get(i).key), mx, my);
                return;
            }
        }
        SideConfig cfg = menu.sides();
        TransferType sel = selectedType();
        for (int i = 0; i < NET_SIDES.length; i++) {
            if (!inRect(mx, my, x + netX(i), y + netY(i), CELL, CELL)) {
                continue;
            }
            RelativeSide side = NET_SIDES[i];
            if (!menu.kind.hasPort(side)) {
                g.renderTooltip(font, Component.translatable("gui.kontur.no_port"), mx, my);
                return;
            }
            g.renderComponentTooltip(font, List.of(
                    Component.translatable("gui.kontur.cell_title", Component.translatable("gui.kontur.side." + side.key),
                            Component.translatable("gui.kontur.row." + sel.key)),
                    Component.translatable("gui.kontur.mode." + cfg.get(sel, side).key).withStyle(ChatFormatting.GOLD),
                    Component.translatable("gui.kontur.cell_hint").withStyle(ChatFormatting.GRAY)), mx, my);
            return;
        }
    }

    private void sendButton(int id) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.gameMode != null) {
            mc.gameMode.handleInventoryButtonClick(menu.containerId, id);
        }
        click();
    }

    private static void click() {
        Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1.0f));
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        int x = leftPos;
        int y = topPos;
        int mx = (int) Math.floor(mouseX);
        int my = (int) Math.floor(mouseY);
        if (hasConfigTab() && button == 0 && inRect(mx, my, x + HOLDER_X + 4, y + configTabY() + 4, 20, 18)) {
            menu.setConfigOpen(!menu.configOpen());
            click();
            return true;
        }
        if (menu.configOpen()) {
            if (button == 0 && inRect(mx, my, x + EJ_X, y + EJ_Y, EJ_W, EJ_H)) {
                sendButton(MachineMenu.EJECT_BUTTON);
                return true;
            }
            List<TransferType> rows = configRows();
            for (int i = 0; i < rows.size(); i++) {
                if (button == 0 && inRect(mx, my, x + TB_X + i * TB_STEP, y + TB_Y, TB_W, TB_H)) {
                    cfgType = rows.get(i);
                    click();
                    return true;
                }
            }
            for (int i = 0; i < NET_SIDES.length; i++) {
                if (inRect(mx, my, x + netX(i), y + netY(i), CELL, CELL)) {
                    if ((button == 0 || button == 1) && menu.kind.hasPort(NET_SIDES[i])) {
                        sendButton(MachineMenu.sideButton(selectedType(), NET_SIDES[i], button == 1));
                    }
                    return true;
                }
            }
            if (inRect(mx, my, x + CFG_X, y + CFG_Y, CFG_W, CFG_H)) {
                return true;
            }
        } else if (button == 0 && Screen.hasShiftDown() && menu.getCarried().isEmpty()) {
            for (int i = 0; i < def.tanks.size(); i++) {
                TankDef t = def.tanks.get(i);
                if (inRect(mx, my, x + t.x(), y + t.y(), t.width(), t.height())) {
                    sendButton(MachineMenu.VOID_TANK_BUTTON + i);
                    return true;
                }
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    /** Вкладка: слот модуля, слот радиатора и полоса нагрева (у панелей - только слот покрытия). */
    private int holderHeight() {
        return def.hasCooler() ? 57 : def.hasModule() ? 36 : 26;
    }

    private int heatBarOffset() {
        return def.hasCooler() ? 47 : 25;
    }

    private static boolean inRect(int mx, int my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }
}
