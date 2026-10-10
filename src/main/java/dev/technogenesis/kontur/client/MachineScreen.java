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
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.FluidStack;

/** Универсальный экран машины: слоты, шкала энергии, баки, прогресс, диагностика и панель настройки сторон. */
public class MachineScreen extends AbstractContainerScreen<MachineMenu> {
    private static final ResourceLocation ARROW = ResourceLocation.withDefaultNamespace("container/furnace/burn_progress");
    private static final ResourceLocation FLAME = ResourceLocation.withDefaultNamespace("container/furnace/lit_progress");

    private static final int ENERGY_X = 8;
    private static final int ENERGY_Y = 17;
    private static final int ENERGY_W = 10;
    private static final int ENERGY_H = 62;

    private static final int CELL_W = 22;
    private static final int CELL_H = 15;
    private static final int CFG_W = 112;

    private boolean configOpen;
    private final MachineDefinition def;

    public MachineScreen(MachineMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        this.def = menu.def;
        this.imageWidth = 176;
        this.imageHeight = 166;
        this.inventoryLabelY = 10000; // вместо подписи инвентаря внизу машинной части - строка состояния
    }

    private static String fe(long v) {
        return NumberFormat.getIntegerInstance(Locale.ROOT).format(v).replace(',', ' ');
    }

    public MachineKind kind() {
        return menu.kind;
    }

    /** Области вне основной панели (панель настройки сторон): JEI не должен заходить на них своим списком. */
    public List<Rect2i> extraAreas() {
        return configOpen ? List.of(new Rect2i(cfgX(), topPos, CFG_W + 8, cfgHeight())) : List.of();
    }

    private int cfgHeight() {
        return 32 + 6 * (CELL_H + 1) + 6 + (def.hasItems() ? 14 : 0) + (def.hasFluids() ? 14 : 0) + 8;
    }

    // ------------------------------------------------------------------ отрисовка

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
        renderCustomTooltips(g, mouseX, mouseY);
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        int x = leftPos;
        int y = topPos;
        GuiUtil.panel(g, x, y, imageWidth, imageHeight);
        for (Slot slot : menu.slots) {
            GuiUtil.slot(g, x + slot.x, y + slot.y);
        }
        if (def.energyCapacity > 0) {
            GuiUtil.energyBar(g, x + ENERGY_X, y + ENERGY_Y, ENERGY_W, ENERGY_H, menu.energy(), menu.energyCapacity());
        }
        for (int i = 0; i < def.tanks.size(); i++) {
            drawTank(g, x, y, def.tanks.get(i), menu.fluid(i));
        }
        if (def.hasArrow()) {
            drawArrow(g, x + def.arrowX, y + def.arrowY);
        }
        if (def.hasFlame()) {
            drawFlame(g, x + def.flameX, y + def.flameY);
        }
        drawStatusLine(g, x, y);
        drawConfigToggle(g, mouseX, mouseY);
        if (configOpen) {
            drawConfigPanel(g, mouseX, mouseY);
        }
    }

    private void drawTank(GuiGraphics g, int x, int y, TankDef t, FluidStack fluid) {
        GuiUtil.inset(g, x + t.x(), y + t.y(), t.width(), t.height());
        if (!fluid.isEmpty()) {
            int h = Math.max(1, (int) ((long) (t.height() - 2) * fluid.getAmount() / t.capacity()));
            IClientFluidTypeExtensions ext = IClientFluidTypeExtensions.of(fluid.getFluid());
            TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS)
                    .apply(ext.getStillTexture(fluid));
            int tint = ext.getTintColor(fluid);
            float r = ((tint >> 16) & 255) / 255f;
            float gr = ((tint >> 8) & 255) / 255f;
            float b = (tint & 255) / 255f;
            int left = x + t.x() + 1;
            int bottom = y + t.y() + t.height() - 1;
            g.enableScissor(left, bottom - h, left + t.width() - 2, bottom);
            for (int yy = bottom - 16; yy > bottom - h - 16; yy -= 16) {
                g.blit(left, yy, 0, 16, 16, sprite, r, gr, b, 1.0f);
            }
            g.disableScissor();
        }
        for (int i = 1; i < 8; i++) { // деления бака
            int ty = y + t.y() + t.height() - 1 - i * (t.height() - 2) / 8;
            g.fill(x + t.x() + t.width() - 5, ty, x + t.x() + t.width() - 1, ty + 1, i % 2 == 0 ? 0x99000000 : 0x55000000);
        }
    }

    private void drawArrow(GuiGraphics g, int ax, int ay) {
        g.setColor(0.33f, 0.33f, 0.33f, 1f);
        g.blitSprite(ARROW, 24, 16, 0, 0, ax, ay, 24, 16);
        g.setColor(1f, 1f, 1f, 1f);
        int total = menu.totalTime();
        int w = total <= 0 ? 0 : Math.min(24, 24 * menu.progress() / total);
        if (w > 0) {
            g.blitSprite(ARROW, 24, 16, 0, 0, ax, ay, w, 16);
        }
    }

    private void drawFlame(GuiGraphics g, int fx, int fy) {
        g.setColor(0.28f, 0.28f, 0.28f, 1f);
        g.blitSprite(FLAME, 14, 14, 0, 0, fx, fy, 14, 14);
        g.setColor(1f, 1f, 1f, 1f);
        int total = menu.burnTotal();
        if (total > 0 && menu.burnLeft() > 0) {
            int k = Math.max(1, 13 * menu.burnLeft() / total);
            g.blitSprite(FLAME, 14, 14, 0, 14 - k, fx, fy + 14 - k, 14, k + 1);
        }
    }

    private void drawStatusLine(GuiGraphics g, int x, int y) {
        MachineStatus st = menu.status();
        int color = st.problem ? 0xFFAA2222 : (st == MachineStatus.RUNNING || st == MachineStatus.CHARGING ? 0xFF2E7D32 : 0xFF404040);
        g.drawString(font, st.text(), x + 8, y + 72, color, false);
    }

    private boolean inToggle(double mx, double my) {
        int bx = leftPos + imageWidth - 18;
        int by = topPos + 4;
        return mx >= bx && mx < bx + 12 && my >= by && my < by + 12;
    }

    private void drawConfigToggle(GuiGraphics g, int mx, int my) {
        int bx = leftPos + imageWidth - 18;
        int by = topPos + 4;
        GuiUtil.inset(g, bx, by, 12, 12);
        if (!configOpen) {
            g.fill(bx + 1, by + 1, bx + 11, by + 11, inToggle(mx, my) ? 0xFFB8B8B8 : 0xFFC6C6C6);
            g.fill(bx + 1, by + 1, bx + 10, by + 2, 0xFFFFFFFF);
            g.fill(bx + 1, by + 1, bx + 2, by + 10, 0xFFFFFFFF);
            g.fill(bx + 2, by + 10, bx + 11, by + 11, 0xFF555555);
            g.fill(bx + 10, by + 2, bx + 11, by + 11, 0xFF555555);
        } else {
            g.fill(bx + 1, by + 1, bx + 11, by + 11, 0xFF9A9A9A);
        }
        for (int i = 0; i < 3; i++) {
            g.fill(bx + 3, by + 3 + i * 3, bx + 9, by + 4 + i * 3, 0xFF373737);
        }
    }

    // ------------------------------------------------------------------ панель сторон

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

    private int cfgX() {
        return leftPos + imageWidth + 2;
    }

    private int cfgRowsTop() {
        return topPos + 32;
    }

    private int cfgCellX(int col) {
        return cfgX() + 50 + col * (CELL_W + 2);
    }

    private int cfgCellY(int row) {
        return cfgRowsTop() + row * (CELL_H + 1);
    }

    private int ejectY(int i) {
        return cfgRowsTop() + 6 * (CELL_H + 1) + 6 + i * 14;
    }

    private void drawConfigPanel(GuiGraphics g, int mx, int my) {
        int px = cfgX();
        int py = topPos;
        GuiUtil.panel(g, px, py, CFG_W + 8, cfgHeight());
        g.drawString(font, Component.translatable("gui.kontur.config.title"), px + 8, py + 7, 0xFF404040, false);
        List<TransferType> cols = columns();
        for (int c = 0; c < cols.size(); c++) {
            ItemStack icon = switch (cols.get(c)) {
                case ITEMS -> new ItemStack(Items.HOPPER);
                case FLUIDS -> new ItemStack(Items.WATER_BUCKET);
                case ENERGY -> new ItemStack(Items.REDSTONE);
            };
            g.renderItem(icon, cfgCellX(c) + 3, py + 13);
        }
        SideConfig cfg = menu.sides();
        RelativeSide[] sides = RelativeSide.values();
        for (int r = 0; r < sides.length; r++) {
            g.drawString(font, Component.translatable("gui.kontur.side." + sides[r].key), px + 8, cfgCellY(r) + 4, 0xFF404040, false);
            for (int c = 0; c < cols.size(); c++) {
                drawCell(g, cfgCellX(c), cfgCellY(r), cfg.get(cols.get(c), sides[r]), hoverCell(mx, my, c, r));
            }
        }
        if (def.hasItems()) {
            drawEject(g, px + 8, ejectY(0), "gui.kontur.eject.items", cfg.ejectItems, mx, my);
        }
        if (def.hasFluids()) {
            drawEject(g, px + 8, ejectY(def.hasItems() ? 1 : 0), "gui.kontur.eject.fluids", cfg.ejectFluids, mx, my);
        }
    }

    private boolean hoverCell(int mx, int my, int c, int r) {
        int x = cfgCellX(c);
        int y = cfgCellY(r);
        return mx >= x && mx < x + CELL_W && my >= y && my < y + CELL_H;
    }

    private void drawCell(GuiGraphics g, int x, int y, IoMode mode, boolean hover) {
        int color = switch (mode) {
            case NONE -> 0xFF6B6B6B;
            case INPUT -> 0xFF3F6FD6;
            case OUTPUT -> 0xFFE08A2A;
            case ALL -> 0xFF3FAE4F;
        };
        g.fill(x, y, x + CELL_W, y + CELL_H, 0xFF373737);
        g.fill(x + 1, y + 1, x + CELL_W - 1, y + CELL_H - 1, color);
        g.fill(x + 1, y + 1, x + CELL_W - 1, y + 2, 0x55FFFFFF);
        g.fill(x + 1, y + CELL_H - 2, x + CELL_W - 1, y + CELL_H - 1, 0x55000000);
        if (hover) {
            g.fill(x + 1, y + 1, x + CELL_W - 1, y + CELL_H - 1, 0x33FFFFFF);
        }
        String label = switch (mode) {
            case NONE -> "-";
            case INPUT -> "IN";
            case OUTPUT -> "OUT";
            case ALL -> "I/O";
        };
        g.drawCenteredString(font, label, x + CELL_W / 2, y + 4, 0xFFFFFFFF);
    }

    private void drawEject(GuiGraphics g, int x, int y, String key, boolean on, int mx, int my) {
        GuiUtil.inset(g, x, y, 11, 11);
        if (on) {
            g.fill(x + 2, y + 2, x + 9, y + 9, 0xFF3FAE4F);
            g.fill(x + 2, y + 2, x + 9, y + 3, 0x66FFFFFF);
        }
        g.drawString(font, Component.translatable(key), x + 15, y + 2, 0xFF404040, false);
    }

    // ------------------------------------------------------------------ подсказки

    private void renderCustomTooltips(GuiGraphics g, int mx, int my) {
        int x = leftPos;
        int y = topPos;
        if (def.energyCapacity > 0 && inRect(mx, my, x + ENERGY_X, y + ENERGY_Y, ENERGY_W, ENERGY_H)) {
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
        if (def.hasArrow() && inRect(mx, my, x + def.arrowX, y + def.arrowY, 24, 16) && menu.totalTime() > 0) {
            g.renderTooltip(font, Component.translatable("gui.kontur.progress", 100 * menu.progress() / menu.totalTime()), mx, my);
        }
        if (inToggle(mx, my)) {
            g.renderTooltip(font, Component.translatable("gui.kontur.config"), mx, my);
        }
        if (configOpen) {
            cellTooltip(g, mx, my);
        }
    }

    private void cellTooltip(GuiGraphics g, int mx, int my) {
        List<TransferType> cols = columns();
        RelativeSide[] sides = RelativeSide.values();
        for (int r = 0; r < sides.length; r++) {
            for (int c = 0; c < cols.size(); c++) {
                if (hoverCell(mx, my, c, r)) {
                    IoMode m = menu.sides().get(cols.get(c), sides[r]);
                    List<Component> lines = new ArrayList<>();
                    lines.add(Component.translatable("gui.kontur.side." + sides[r].key)
                            .append(" - ").append(Component.translatable("gui.kontur.type." + cols.get(c).key)));
                    lines.add(Component.translatable("gui.kontur.mode." + m.key));
                    lines.add(Component.translatable("gui.kontur.config.hint"));
                    g.renderComponentTooltip(font, lines, mx, my);
                    return;
                }
            }
        }
    }

    private static boolean inRect(int mx, int my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }

    // ------------------------------------------------------------------ ввод

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (inToggle(mx, my)) {
            configOpen = !configOpen;
            return true;
        }
        if (configOpen) {
            List<TransferType> cols = columns();
            for (int r = 0; r < 6; r++) {
                for (int c = 0; c < cols.size(); c++) {
                    if (hoverCell((int) mx, (int) my, c, r)) {
                        int type = cols.get(c).ordinal();
                        sendButton(100 + ((type * 6 + r) * 2 + (button == 1 ? 1 : 0)));
                        return true;
                    }
                }
            }
            int px = cfgX() + 8;
            if (def.hasItems() && inRect((int) mx, (int) my, px, ejectY(0), 80, 11)) {
                sendButton(200);
                return true;
            }
            if (def.hasFluids() && inRect((int) mx, (int) my, px, ejectY(def.hasItems() ? 1 : 0), 80, 11)) {
                sendButton(201);
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
    }

    private void sendButton(int id) {
        if (minecraft != null && minecraft.gameMode != null) {
            minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
        }
    }
}
