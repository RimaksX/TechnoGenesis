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
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.Rect2i;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import com.mojang.blaze3d.platform.InputConstants;
import dev.technogenesis.kontur.block.MachineBlock;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.FluidStack;

/**
 * Универсальный экран машины в духе Mekanism: светлое окно с чёрной обводкой, утопленные слоты и шкалы, шкала энергии
 * справа, тёмный экран состояния с зелёным текстом, вкладка настройки слева. Настройка сторон открывается окном поверх:
 * вкладки типов (предметы, жидкости, энергия), "развёртка" граней машины шестью цветными кнопками, выброс и сброс.
 * Любой текст перед выводом обрезается по доступной ширине, поэтому надписи не наезжают друг на друга.
 */
public class MachineScreen extends AbstractContainerScreen<MachineMenu> {
    public static final int IMAGE_W = 176;
    public static final int IMAGE_H = 184;

    // шкала энергии (справа)
    static final int ENERGY_X = 160;
    static final int ENERGY_Y = 18;
    // рабочая область (без рамки): x 8..152, y 18..74
    static final int CONTENT_X = 8;
    static final int CONTENT_Y = 18;
    static final int CONTENT_W = 144;
    static final int CONTENT_H = 56;
    // экран состояния
    static final int STATUS_X = 8;
    static final int STATUS_Y = 78;
    static final int STATUS_W = 160;
    static final int STATUS_H = 12;
    static final int TITLE_Y = 6;
    static final int INV_LABEL_Y = 92;

    // вкладка настройки (слева): держатель 26x26 перекрывает край окна на 4 пикселя, кнопка 18x18 внутри
    private static final int HOLDER_X = -22;
    private static final int HOLDER_Y = 6;
    private static final int TAB_X = -18;
    private static final int TAB_Y = 10;
    private static final int TAB_SIZE = 18;

    // окно настройки сторон (в координатах окна)
    private static final int WIN_W = 156;
    private static final int WIN_H = 148;
    private static final int WIN_DX = 10;
    private static final int WIN_DY = 18;
    private static final int TYPE_W = 28;
    private static final int TYPE_H = 20;
    private static final int TYPE_Y = 16;
    private static final int TYPE_GAP = 4;
    private static final int SCREEN_X = 6;
    private static final int SCREEN_Y = 40;
    private static final int SCREEN_W = 94;
    private static final int SCREEN_H = 14;
    private static final int ACTION_SIZE = 18;
    private static final int EJECT_X = 104;
    private static final int CLEAR_X = 126;
    private static final int ACTION_Y = 38;
    private static final int SIDE_BTN = 22;
    private static final int LEGEND_Y = 134;

    private static final int COLOR_NONE = 0x8C8C96;
    private static final int COLOR_INPUT = 0x5C9AFF;
    private static final int COLOR_OUTPUT = 0xFFA533;
    private static final int COLOR_ALL = 0x59D973;

    private boolean configOpen;
    private TransferType cfgType;
    private final MachineDefinition def;

    public MachineScreen(MachineMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        this.def = menu.def;
        this.imageWidth = IMAGE_W;
        this.imageHeight = IMAGE_H;
        this.titleLabelY = TITLE_Y;
        this.inventoryLabelY = INV_LABEL_Y;
        List<TransferType> cols = columns();
        this.cfgType = cols.isEmpty() ? TransferType.ENERGY : cols.get(0);
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

    private static int colorOf(IoMode m) {
        return switch (m) {
            case NONE -> COLOR_NONE;
            case INPUT -> COLOR_INPUT;
            case OUTPUT -> COLOR_OUTPUT;
            case ALL -> COLOR_ALL;
        };
    }

    private static ResourceLocation iconOf(TransferType t) {
        return switch (t) {
            case ITEMS -> GuiUtil.ICON_ITEMS;
            case FLUIDS -> GuiUtil.ICON_FLUIDS;
            case ENERGY -> GuiUtil.ICON_ENERGY;
        };
    }

    // ------------------------------------------------------------------ геометрия

    private int tabX() {
        return leftPos + TAB_X;
    }

    private int tabY() {
        return topPos + TAB_Y;
    }

    private int winX() {
        return leftPos + WIN_DX;
    }

    private int winY() {
        return topPos + WIN_DY;
    }

    private boolean inWindow(double mx, double my) {
        return configOpen && inRect((int) mx, (int) my, winX(), winY(), WIN_W, WIN_H);
    }

    private static int sideX(RelativeSide s) {
        return switch (s) {
            case LEFT, BACK -> 44;
            case RIGHT -> 90;
            default -> 67;
        };
    }

    private static int sideY(RelativeSide s) {
        return switch (s) {
            case TOP -> 60;
            case BACK, BOTTOM -> 106;
            default -> 83;
        };
    }

    private static final RelativeSide[] CROSS = {RelativeSide.TOP, RelativeSide.LEFT, RelativeSide.FRONT,
            RelativeSide.RIGHT, RelativeSide.BACK, RelativeSide.BOTTOM};

    private int typeTabX(int i, int n) {
        int total = n * TYPE_W + (n - 1) * TYPE_GAP;
        return winX() + (WIN_W - total) / 2 + i * (TYPE_W + TYPE_GAP);
    }

    private boolean hasEject() {
        return cfgType == TransferType.ITEMS || cfgType == TransferType.FLUIDS;
    }

    /** Области вне основной панели (вкладка и окно настройки): JEI не должен заходить на них своим списком. */
    public List<Rect2i> extraAreas() {
        List<Rect2i> areas = new ArrayList<>();
        areas.add(new Rect2i(leftPos + HOLDER_X, topPos + HOLDER_Y, 26, 26));
        return areas;
    }

    // ------------------------------------------------------------------ отрисовка

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        if (configOpen) {
            g.pose().pushPose();
            g.pose().translate(0, 0, 200);
            drawWindow(g, mouseX, mouseY);
            g.pose().popPose();
        }
        if (!inWindow(mouseX, mouseY)) {
            renderTooltip(g, mouseX, mouseY);
        }
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
        drawTab(g, mouseX, mouseY);
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

    /** Мощность справа в строке состояния: расход при работе, выработка у генератора. */
    private String rateText(MachineStatus st) {
        if (def.energyKind == EnergyKind.GENERATOR && menu.rate() > 0) {
            return "+" + fe(menu.rate()) + " FE/t";
        }
        if (def.energyKind == EnergyKind.CONSUMER && st == MachineStatus.RUNNING && def.ratePerTick > 0) {
            return "-" + fe(def.ratePerTick) + " FE/t";
        }
        return "";
    }

    private boolean inTab(double mx, double my) {
        return inRect((int) mx, (int) my, tabX(), tabY(), TAB_SIZE, TAB_SIZE);
    }

    private void drawTab(GuiGraphics g, int mx, int my) {
        GuiUtil.holder(g, leftPos + HOLDER_X, topPos + HOLDER_Y);
        GuiUtil.button(g, tabX(), tabY(), TAB_SIZE, TAB_SIZE, configOpen ? 0xB8F0C8 : 0xFFFFFF, configOpen,
                !configOpen && inTab(mx, my));
        GuiUtil.icon(g, GuiUtil.ICON_CONFIG, tabX() + 1, tabY() + 1);
    }

    // ------------------------------------------------------------------ окно настройки сторон

    private List<TransferType> columns() {
        List<TransferType> cols = new ArrayList<>();
        if (def.hasItems()) {
            cols.add(TransferType.ITEMS);
        }
        if (def.hasFluids()) {
            cols.add(TransferType.FLUIDS);
        }
        if (def.energyCapacity > 0) {
            cols.add(TransferType.ENERGY);
        }
        return cols;
    }

    /** Блок по соседству с гранью; для передней - сама машина. Пусто, если там воздух. */
    private ItemStack neighbour(RelativeSide side) {
        Level level = Minecraft.getInstance().level;
        if (level == null) {
            return ItemStack.EMPTY;
        }
        BlockState self = level.getBlockState(menu.pos);
        if (!self.hasProperty(MachineBlock.FACING)) {
            return ItemStack.EMPTY;
        }
        if (side == RelativeSide.FRONT) {
            return new ItemStack(self.getBlock());
        }
        Direction facing = self.getValue(MachineBlock.FACING);
        for (Direction d : Direction.values()) {
            if (RelativeSide.of(facing, d) == side) {
                BlockState n = level.getBlockState(menu.pos.relative(d));
                return n.isAir() ? ItemStack.EMPTY : new ItemStack(n.getBlock());
            }
        }
        return ItemStack.EMPTY;
    }

    private RelativeSide hoveredSide(int mx, int my) {
        for (RelativeSide s : CROSS) {
            if (inRect(mx, my, winX() + sideX(s), winY() + sideY(s), SIDE_BTN, SIDE_BTN)) {
                return s;
            }
        }
        return null;
    }

    private void drawWindow(GuiGraphics g, int mx, int my) {
        int wx = winX();
        int wy = winY();
        GuiUtil.background(g, wx, wy, WIN_W, WIN_H);
        String heading = fit(Component.translatable("gui.kontur.config.title").getString(), WIN_W - 16);
        g.drawString(font, heading, wx + (WIN_W - font.width(heading)) / 2, wy + 5, GuiUtil.TITLE_TEXT, false);

        // вкладки типов
        List<TransferType> cols = columns();
        for (int i = 0; i < cols.size(); i++) {
            int tx = typeTabX(i, cols.size());
            boolean sel = cols.get(i) == cfgType;
            GuiUtil.button(g, tx, wy + TYPE_Y, TYPE_W, TYPE_H, sel ? 0xB8F0C8 : 0xFFFFFF, sel,
                    !sel && inRect(mx, my, tx, wy + TYPE_Y, TYPE_W, TYPE_H));
            GuiUtil.icon(g, iconOf(cols.get(i)), tx + (TYPE_W - 16) / 2, wy + TYPE_Y + (TYPE_H - 16) / 2 + (sel ? 1 : 0));
        }

        // экран подсказки
        GuiUtil.gauge(g, wx + SCREEN_X, wy + SCREEN_Y, SCREEN_W, SCREEN_H);
        SideConfig cfg = menu.sides();
        RelativeSide hs = hoveredSide(mx, my);
        String line;
        int lineColor = GuiUtil.SCREEN_TEXT;
        if (hs == null) {
            line = Component.translatable("gui.kontur.type." + cfgType.key).getString();
            line = line + " - " + Component.translatable("gui.kontur.config.hint_short").getString();
            lineColor = 0xFF8FA39A;
        } else if (hs == RelativeSide.FRONT) {
            line = Component.translatable("gui.kontur.config.front").getString();
        } else {
            line = Component.translatable("gui.kontur.config.side_line",
                    Component.translatable("gui.kontur.side." + hs.key),
                    Component.translatable("gui.kontur.mode." + cfg.get(cfgType, hs).key)).getString();
        }
        g.drawString(font, fit(line, SCREEN_W - 8), wx + SCREEN_X + 4, wy + SCREEN_Y + (SCREEN_H - 8) / 2, lineColor, false);

        // выброс и сброс
        if (hasEject()) {
            boolean on = cfgType == TransferType.ITEMS ? cfg.ejectItems : cfg.ejectFluids;
            GuiUtil.button(g, wx + EJECT_X, wy + ACTION_Y, ACTION_SIZE, ACTION_SIZE, on ? 0x59D973 : 0xFFFFFF, on,
                    inRect(mx, my, wx + EJECT_X, wy + ACTION_Y, ACTION_SIZE, ACTION_SIZE));
            GuiUtil.icon(g, GuiUtil.ICON_EJECT, wx + EJECT_X + 1, wy + ACTION_Y + 1 + (on ? 1 : 0));
        }
        GuiUtil.button(g, wx + CLEAR_X, wy + ACTION_Y, ACTION_SIZE, ACTION_SIZE, 0xFFFFFF, false,
                inRect(mx, my, wx + CLEAR_X, wy + ACTION_Y, ACTION_SIZE, ACTION_SIZE));
        GuiUtil.icon(g, GuiUtil.ICON_CLEAR, wx + CLEAR_X + 1, wy + ACTION_Y + 1);

        // развёртка граней
        for (RelativeSide s : CROSS) {
            int bx = wx + sideX(s);
            int by = wy + sideY(s);
            boolean front = s == RelativeSide.FRONT;
            int color = front ? 0xA8A8B0 : colorOf(cfg.get(cfgType, s));
            GuiUtil.button(g, bx, by, SIDE_BTN, SIDE_BTN, color, front, !front && s == hs);
            ItemStack icon = neighbour(s);
            if (!icon.isEmpty()) {
                g.renderItem(icon, bx + 3, by + 3);
            }
        }

        // легенда цветов
        IoMode[] modes = IoMode.values();
        int total = 0;
        String[] names = new String[modes.length];
        for (int i = 0; i < modes.length; i++) {
            names[i] = Component.translatable("gui.kontur.legend." + modes[i].key).getString();
            total += 8 + 3 + font.width(names[i]);
        }
        int gap = Math.max(2, Math.min(8, (WIN_W - 12 - total) / (modes.length - 1)));
        int lx = wx + (WIN_W - (total + gap * (modes.length - 1))) / 2;
        for (int i = 0; i < modes.length; i++) {
            int sy = wy + LEGEND_Y;
            g.fill(lx, sy, lx + 8, sy + 8, 0xFF121317);
            g.fill(lx + 1, sy + 1, lx + 7, sy + 7, 0xFF000000 | colorOf(modes[i]));
            g.drawString(font, names[i], lx + 11, sy, GuiUtil.TITLE_TEXT, false);
            lx += 11 + font.width(names[i]) + gap;
        }
    }

    // ------------------------------------------------------------------ подсказки

    private void renderCustomTooltips(GuiGraphics g, int mx, int my) {
        int x = leftPos;
        int y = topPos;
        if (inWindow(mx, my)) {
            windowTooltip(g, mx, my);
            return;
        }
        if (def.energyCapacity > 0 && inRect(mx, my, x + ENERGY_X, y + ENERGY_Y, GuiUtil.POWER_W, GuiUtil.POWER_H)) {
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable("gui.kontur.energy"));
            lines.add(Component.translatable("gui.kontur.energy_value", fe(menu.energy()), fe(menu.energyCapacity())));
            if (def.energyKind == EnergyKind.CONSUMER) {
                lines.add(Component.translatable("gui.kontur.energy_rate", fe(def.ratePerTick)));
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
        if (inTab(mx, my)) {
            g.renderTooltip(font, Component.translatable("gui.kontur.config"), mx, my);
        }
    }

    private void windowTooltip(GuiGraphics g, int mx, int my) {
        SideConfig cfg = menu.sides();
        List<TransferType> cols = columns();
        for (int i = 0; i < cols.size(); i++) {
            if (inRect(mx, my, typeTabX(i, cols.size()), winY() + TYPE_Y, TYPE_W, TYPE_H)) {
                g.renderTooltip(font, Component.translatable("gui.kontur.type." + cols.get(i).key), mx, my);
                return;
            }
        }
        if (hasEject() && inRect(mx, my, winX() + EJECT_X, winY() + ACTION_Y, ACTION_SIZE, ACTION_SIZE)) {
            boolean on = cfgType == TransferType.ITEMS ? cfg.ejectItems : cfg.ejectFluids;
            Component name = Component.translatable("gui.kontur.eject." + cfgType.key);
            List<Component> lines = new ArrayList<>();
            lines.add(Component.translatable(on ? "gui.kontur.config.eject_on" : "gui.kontur.config.eject_off", name));
            lines.add(Component.translatable("gui.kontur.config.eject_hint").withStyle(ChatFormatting.GRAY));
            g.renderComponentTooltip(font, lines, mx, my);
            return;
        }
        if (inRect(mx, my, winX() + CLEAR_X, winY() + ACTION_Y, ACTION_SIZE, ACTION_SIZE)) {
            g.renderTooltip(font, Component.translatable("gui.kontur.config.clear"), mx, my);
            return;
        }
        RelativeSide s = hoveredSide(mx, my);
        if (s == null) {
            return;
        }
        List<Component> lines = new ArrayList<>();
        lines.add(Component.translatable("gui.kontur.side." + s.key));
        if (s == RelativeSide.FRONT) {
            lines.add(Component.translatable("gui.kontur.config.front").withStyle(ChatFormatting.GRAY));
        } else {
            IoMode m = cfg.get(cfgType, s);
            lines.add(Component.translatable("gui.kontur.type." + cfgType.key).append(": ")
                    .append(Component.translatable("gui.kontur.mode." + m.key))
                    .withStyle(st -> st.withColor(colorOf(m))));
            ItemStack n = neighbour(s);
            if (!n.isEmpty()) {
                lines.add(n.getHoverName().copy().withStyle(ChatFormatting.GRAY));
            }
            lines.add(Component.translatable("gui.kontur.config.hint").withStyle(ChatFormatting.DARK_GRAY));
        }
        g.renderComponentTooltip(font, lines, mx, my);
    }

    private static boolean inRect(int mx, int my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }

    // ------------------------------------------------------------------ ввод

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (inTab(mx, my)) {
            configOpen = !configOpen;
            return true;
        }
        if (inWindow(mx, my)) {
            windowClick((int) mx, (int) my, button);
            return true;
        }
        return super.mouseClicked(mx, my, button);
    }

    private void windowClick(int mx, int my, int button) {
        List<TransferType> cols = columns();
        for (int i = 0; i < cols.size(); i++) {
            if (inRect(mx, my, typeTabX(i, cols.size()), winY() + TYPE_Y, TYPE_W, TYPE_H)) {
                cfgType = cols.get(i);
                return;
            }
        }
        if (hasEject() && inRect(mx, my, winX() + EJECT_X, winY() + ACTION_Y, ACTION_SIZE, ACTION_SIZE)) {
            sendButton(cfgType == TransferType.ITEMS ? 200 : 201);
            return;
        }
        if (inRect(mx, my, winX() + CLEAR_X, winY() + ACTION_Y, ACTION_SIZE, ACTION_SIZE)) {
            sendButton(300 + cfgType.ordinal());
            return;
        }
        RelativeSide s = hoveredSide(mx, my);
        if (s != null && s != RelativeSide.FRONT) {
            sendButton(100 + ((cfgType.ordinal() * 6 + s.ordinal()) * 2 + (button == 1 ? 1 : 0)));
        }
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (configOpen && key == InputConstants.KEY_ESCAPE) {
            configOpen = false;
            return true;
        }
        return super.keyPressed(key, scan, mods);
    }

    private void sendButton(int id) {
        if (minecraft != null && minecraft.gameMode != null) {
            minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
        }
    }
}
