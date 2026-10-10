package dev.technogenesis.kontur.client;

import net.minecraft.client.gui.GuiGraphics;

/** Ванильная стилистика интерфейса: серая панель с фасками, утопленные слоты и шкалы. */
public final class GuiUtil {
    public static final int PANEL = 0xFFC6C6C6;
    public static final int LIGHT = 0xFFFFFFFF;
    public static final int SHADOW = 0xFF555555;
    public static final int BLACK = 0xFF000000;
    public static final int INSET = 0xFF8B8B8B;
    public static final int INSET_DARK = 0xFF373737;

    private GuiUtil() {
    }

    public static void panel(GuiGraphics g, int x, int y, int w, int h) {
        g.fill(x, y, x + w, y + h, BLACK);
        g.fill(x + 1, y + 1, x + w - 1, y + h - 1, PANEL);
        g.fill(x + 1, y + 1, x + w - 2, y + 2, LIGHT);
        g.fill(x + 1, y + 1, x + 2, y + h - 2, LIGHT);
        g.fill(x + 2, y + h - 2, x + w - 1, y + h - 1, SHADOW);
        g.fill(x + w - 2, y + 2, x + w - 1, y + h - 1, SHADOW);
    }

    /** Утопленная область: тёмный верх и лево, светлый низ и право. */
    public static void inset(GuiGraphics g, int x, int y, int w, int h) {
        g.fill(x, y, x + w, y + h, INSET);
        g.fill(x, y, x + w - 1, y + 1, INSET_DARK);
        g.fill(x, y, x + 1, y + h - 1, INSET_DARK);
        g.fill(x + 1, y + h - 1, x + w, y + h, LIGHT);
        g.fill(x + w - 1, y + 1, x + w, y + h, LIGHT);
    }

    public static void slot(GuiGraphics g, int x, int y) {
        inset(g, x - 1, y - 1, 18, 18);
    }

    /** Вертикальная шкала энергии: градиент красный - оранжевый, блики по левому краю. */
    public static void energyBar(GuiGraphics g, int x, int y, int w, int h, int stored, int capacity) {
        inset(g, x, y, w, h);
        if (capacity <= 0 || stored <= 0) {
            return;
        }
        int fill = Math.max(1, (int) ((long) (h - 2) * stored / capacity));
        int top = y + h - 1 - fill;
        for (int i = 0; i < fill; i++) {
            float t = (float) i / Math.max(1, h - 2);
            int r = 0xE0 - (int) (t * 0x20);
            int gr = 0x28 + (int) (t * 0x70);
            g.fill(x + 1, y + h - 2 - i, x + w - 1, y + h - 1 - i, 0xFF000000 | (r << 16) | (gr << 8) | 0x20);
        }
        g.fill(x + 1, top, x + 2, y + h - 1, 0x66FFFFFF);
        g.fill(x + w - 2, top, x + w - 1, y + h - 1, 0x33000000);
    }
}
