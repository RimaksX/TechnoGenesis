package dev.technogenesis.kontur.client;

import dev.technogenesis.kontur.machine.TransferType;
import net.minecraft.client.gui.GuiGraphics;

/** Маленькие пиксельные значки типов на кнопках панели настройки сторон: там, где текст не помещается. */
final class TabIcons {
    static final int W = 8;
    static final int H = 7;

    private static final String[] ITEMS_IN = {
            "...##...",
            "...##...",
            ".######.",
            "..####..",
            "...##...",
            "#......#",
            "########"};
    private static final String[] ITEMS_OUT = {
            "...##...",
            "..####..",
            ".######.",
            "...##...",
            "...##...",
            "#......#",
            "########"};
    private static final String[] FLUID = {
            "...##...",
            "..####..",
            "..####..",
            ".######.",
            ".######.",
            ".######.",
            "..####.."};
    private static final String[] ENERGY = {
            "....##..",
            "...##...",
            "..##....",
            ".######.",
            "...##...",
            "..##....",
            ".##....."};
    private static final String[][] DIGITS = {
            {".#.", "##.", ".#.", ".#.", "###"},
            {"##.", "..#", ".#.", "#..", "###"},
            {"##.", "..#", ".#.", "..#", "##."}};

    private TabIcons() {
    }

    private static String[] iconOf(TransferType t) {
        return switch (t) {
            case ITEMS -> ITEMS_IN;
            case FLUIDS -> FLUID;
            case ENERGY -> ENERGY;
            default -> ITEMS_OUT;
        };
    }

    /** Цвет значка типа: предметы светлые, жидкости голубые, энергия янтарная; невыбранные тусклее. */
    private static int colorOf(TransferType t, boolean selected) {
        int c = switch (t) {
            case FLUIDS -> 0x7FB8F0;
            case ENERGY -> 0xF0C050;
            default -> 0xE6ECF8;
        };
        if (!selected) {
            c = ((c >> 16 & 255) * 60 / 100) << 16 | ((c >> 8 & 255) * 60 / 100) << 8 | (c & 255) * 60 / 100;
        }
        return 0xFF000000 | c;
    }

    private static void draw(GuiGraphics g, int x, int y, String[] rows, int argb) {
        for (int r = 0; r < rows.length; r++) {
            for (int c = 0; c < rows[r].length(); c++) {
                if (rows[r].charAt(c) == '#') {
                    g.fill(x + c, y + r, x + c + 1, y + r + 1, argb);
                }
            }
        }
    }

    /** Значок по центру кнопки bw x bh; у выходов справа цифра номера (всё вместе ровно по центру: 8 + 1 + 3 = 12). */
    static void draw(GuiGraphics g, int bx, int by, int bw, int bh, TransferType t, boolean selected) {
        int color = colorOf(t, selected);
        int digit = t.isOutputChannel() ? t.outputIndex() : -1;
        int total = digit >= 0 ? W + 1 + 3 : W;
        int x = bx + (bw - total) / 2;
        draw(g, x, by + (bh - H) / 2, iconOf(t), color);
        if (digit >= 0) {
            draw(g, x + W + 1, by + (bh - 5) / 2, DIGITS[digit], color);
        }
    }
}
