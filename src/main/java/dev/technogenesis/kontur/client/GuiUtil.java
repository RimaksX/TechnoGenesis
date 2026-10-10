package dev.technogenesis.kontur.client;

import dev.technogenesis.kontur.Kontur;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;

/**
 * Рисование интерфейса машин спрайтами из assets/kontur/textures/gui/sprites: окно, слоты, утопленные шкалы и экраны,
 * кнопки, стрелка, пламя, значки. Окно, шкалы, кнопки и держатель вкладки - девятипатчи (граница описана в .mcmeta);
 * кнопки светлые и красятся в нужный цвет при рисовании.
 */
public final class GuiUtil {
    public static final ResourceLocation BACKGROUND = sprite("background");
    public static final ResourceLocation SLOT = sprite("slot");
    public static final ResourceLocation GAUGE = sprite("gauge");
    public static final ResourceLocation TANK_OVERLAY = sprite("tank_overlay");
    public static final ResourceLocation HOLDER = sprite("holder");
    public static final ResourceLocation ARROW_OFF = sprite("arrow_off");
    public static final ResourceLocation ARROW_ON = sprite("arrow_on");
    public static final ResourceLocation FLAME_OFF = sprite("flame_off");
    public static final ResourceLocation FLAME_ON = sprite("flame_on");

    public static final int ARROW_W = 28;
    public static final int ARROW_H = 8;
    public static final int FLAME_SIZE = 13;
    public static final int POWER_W = 8;
    public static final int POWER_H = 56;

    /** Цвет текста на тёмном экране. */
    public static final int SCREEN_TEXT = 0xFF3CFE9A;
    public static final int TITLE_TEXT = 0xFF404040;

    private GuiUtil() {
    }

    private static ResourceLocation sprite(String name) {
        return ResourceLocation.fromNamespaceAndPath(Kontur.MODID, name);
    }

    public static void background(GuiGraphics g, int x, int y, int w, int h) {
        g.blitSprite(BACKGROUND, x, y, w, h);
    }

    /** Слот: рамка 18x18 вокруг предмета 16x16, который стоит в точке (x, y). */
    public static void slot(GuiGraphics g, int x, int y) {
        g.blitSprite(SLOT, x - 1, y - 1, 18, 18);
    }

    /** Утопленная рамка с тёмной серединой: шкалы, баки, экраны. */
    public static void gauge(GuiGraphics g, int x, int y, int w, int h) {
        g.blitSprite(GAUGE, x, y, w, h);
    }

    /** Вертикальная шкала энергии: рамка 8x56 и мятная заливка 6x54 снизу вверх. */
    public static void powerBar(GuiGraphics g, int x, int y, long stored, long capacity) {
        gauge(g, x, y, POWER_W, POWER_H);
        if (capacity <= 0 || stored <= 0) {
            return;
        }
        int h = (int) Math.max(1, Math.min(54, 54 * stored / capacity));
        int left = x + 1;
        int bottom = y + POWER_H - 1;
        g.fill(left, bottom - h, left + 6, bottom, 0xFF2FC577);
        for (int row = 0; row < h; row += 2) {
            g.fill(left, bottom - h + row, left + 6, bottom - h + row + 1, 0xFF3EE88A);
        }
        g.fill(left, bottom - h, left + 1, bottom, 0xFF9CFFC8);
    }

    /** Стрелка прогресса 28x8: серая основа и зелёная часть слева направо. */
    public static void arrow(GuiGraphics g, int x, int y, int progress, int total) {
        g.blitSprite(ARROW_OFF, x, y, ARROW_W, ARROW_H);
        int w = total <= 0 ? 0 : Math.min(ARROW_W, ARROW_W * progress / total);
        if (w > 0) {
            g.blitSprite(ARROW_ON, ARROW_W, ARROW_H, 0, 0, x, y, w, ARROW_H);
        }
    }

    /** Пламя 13x13: серое, поверх цветное, убывающее сверху вниз. */
    public static void flame(GuiGraphics g, int x, int y, int left, int total) {
        g.blitSprite(FLAME_OFF, x, y, FLAME_SIZE, FLAME_SIZE);
        if (total > 0 && left > 0) {
            int k = Math.max(1, FLAME_SIZE * left / total);
            g.blitSprite(FLAME_ON, FLAME_SIZE, FLAME_SIZE, 0, FLAME_SIZE - k, x, y + FLAME_SIZE - k, FLAME_SIZE, k);
        }
    }

    /** Держатель вкладки слева от окна 26x26 (правые 4 пикселя ложатся на край окна). */
    public static void holder(GuiGraphics g, int x, int y) {
        g.blitSprite(HOLDER, x, y, 26, 26);
    }
}
