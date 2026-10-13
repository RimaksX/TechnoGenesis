package dev.technogenesis.kontur.client;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.machine.MachineDefinition;
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
    public static final ResourceLocation SLOT_IN = sprite("slot_in");
    public static final ResourceLocation SLOT_OUT = sprite("slot_out");
    public static final ResourceLocation SLOT_MODULE = sprite("slot_module");
    public static final ResourceLocation GAUGE = sprite("gauge");
    public static final ResourceLocation TANK_OVERLAY = sprite("tank_overlay");
    public static final ResourceLocation HOLDER = sprite("holder");
    public static final ResourceLocation ARROW_OFF = sprite("arrow_off");
    public static final ResourceLocation ARROW_ON = sprite("arrow_on");
    /** Пламя из ванильного меню печи. */
    public static final ResourceLocation FLAME = ResourceLocation.withDefaultNamespace("container/furnace/lit_progress");

    public static final int ARROW_W = 28;
    public static final int ARROW_H = 8;
    public static final int FLAME_SIZE = 14;
    public static final int POWER_W = 8;
    public static final int POWER_H = 56;

    /** Цвет текста на тёмном экране. */
    public static final int SCREEN_TEXT = 0xFF3CFE9A;
    public static final int TITLE_TEXT = 0xFFD4DEEE;
    public static final int LABEL_TEXT = 0xFF8C98AC;

    private GuiUtil() {
    }

    private static ResourceLocation sprite(String name) {
        return ResourceLocation.fromNamespaceAndPath(Kontur.MODID, name);
    }

    public static void background(GuiGraphics g, int x, int y, int w, int h) {
        g.blitSprite(BACKGROUND, x, y, w, h);
    }

    /** Слот: рамка 18x18 вокруг предмета 16x16, который стоит в точке (x, y). Вход - бирюзовая, выход - янтарная. */
    public static void slot(GuiGraphics g, int x, int y, MachineDefinition.SlotRole role) {
        ResourceLocation sprite = role == null ? SLOT : switch (role) {
            case INPUT, INPUT_B, FUEL -> SLOT_IN;
            case OUTPUT -> SLOT_OUT;
            case MODULE, COATING, COOLER -> SLOT_MODULE;
        };
        g.blitSprite(sprite, x - 1, y - 1, 18, 18);
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
        g.fill(left, bottom - h, left + 6, bottom, 0xFFD98A1E);
        for (int row = 0; row < h; row += 2) {
            g.fill(left, bottom - h + row, left + 6, bottom - h + row + 1, 0xFFF0A832);
        }
        g.fill(left, bottom - h, left + 1, bottom, 0xFFFFE09A);
    }

    /** Стрелка прогресса 28x8: серая основа и зелёная часть слева направо. */
    public static void arrow(GuiGraphics g, int x, int y, int progress, int total) {
        g.blitSprite(ARROW_OFF, x, y, ARROW_W, ARROW_H);
        int w = total <= 0 ? 0 : Math.min(ARROW_W, ARROW_W * progress / total);
        if (w > 0) {
            g.blitSprite(ARROW_ON, ARROW_W, ARROW_H, 0, 0, x, y, w, ARROW_H);
        }
    }

    /** Пламя 14x14 из меню печи: тёмный силуэт, поверх цветное, убывающее сверху вниз. */
    public static void flame(GuiGraphics g, int x, int y, int left, int total) {
        g.setColor(0.22f, 0.25f, 0.31f, 1f);
        g.blitSprite(FLAME, x, y, FLAME_SIZE, FLAME_SIZE);
        g.setColor(1f, 1f, 1f, 1f);
        if (total > 0 && left > 0) {
            int k = Math.max(1, FLAME_SIZE * left / total);
            g.blitSprite(FLAME, FLAME_SIZE, FLAME_SIZE, 0, FLAME_SIZE - k, x, y + FLAME_SIZE - k, FLAME_SIZE, k);
        }
    }

    /** Полоса нагрева модуля 18x6: зелёная, жёлтая, красная. */
    public static void heatBar(GuiGraphics g, int x, int y, int percent) {
        gauge(g, x, y, 18, 6);
        int w = Math.max(0, Math.min(16, 16 * percent / 100));
        if (w > 0) {
            int color = percent < 50 ? 0xFF50DC78 : percent < 80 ? 0xFFF0BE32 : 0xFFEB463C;
            g.fill(x + 1, y + 1, x + 1 + w, y + 5, color);
        }
    }

    /** Держатель вкладки слева от окна шириной 31 (правые 4 пикселя ложатся на край окна). */
    public static void holder(GuiGraphics g, int x, int y, int height) {
        g.blitSprite(HOLDER, x, y, 31, height);
    }
}
