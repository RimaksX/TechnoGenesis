package dev.technogenesis.kontur.machine;

import net.minecraft.nbt.CompoundTag;

/** Режимы сторон для предметов, жидкостей и энергии плюс флаги авто-вывода. */
public final class SideConfig {
    private final IoMode[][] modes = new IoMode[TransferType.values().length][RelativeSide.values().length];
    public boolean ejectItems;
    public boolean ejectFluids;

    /** items: что разрешено для предметов вообще - вход включает ITEMS, выход включает все каналы выходов. */
    public SideConfig(IoMode items, IoMode fluids, IoMode energy) {
        fill(TransferType.ITEMS, items.canInput() ? IoMode.INPUT : IoMode.NONE);
        for (TransferType t : TransferType.OUTPUTS) {
            fill(t, items.canOutput() ? IoMode.OUTPUT : IoMode.NONE);
        }
        fill(TransferType.FLUIDS, fluids);
        fill(TransferType.ENERGY, energy);
    }

    /** Допустимые режимы типа: входы и выходы предметов - только открыто или закрыто. */
    private static IoMode[] allowed(TransferType type) {
        if (type == TransferType.ITEMS) {
            return new IoMode[]{IoMode.NONE, IoMode.INPUT};
        }
        if (type.isOutputChannel()) {
            return new IoMode[]{IoMode.NONE, IoMode.OUTPUT};
        }
        return IoMode.values();
    }

    /** Приводит режим к допустимому для типа (для режима ключа «все типы»). */
    public static IoMode coerce(TransferType type, IoMode wanted) {
        if (type == TransferType.ITEMS) {
            return wanted.canInput() ? IoMode.INPUT : IoMode.NONE;
        }
        if (type.isOutputChannel()) {
            return wanted.canOutput() ? IoMode.OUTPUT : IoMode.NONE;
        }
        return wanted;
    }

    private void fill(TransferType type, IoMode mode) {
        for (RelativeSide side : RelativeSide.values()) {
            modes[type.ordinal()][side.ordinal()] = side == RelativeSide.FRONT ? IoMode.NONE : mode;
        }
    }

    public IoMode get(TransferType type, RelativeSide side) {
        return modes[type.ordinal()][side.ordinal()];
    }

    /** Передняя грань - лицо машины, разъёмов на ней нет. */
    public void set(TransferType type, RelativeSide side, IoMode mode) {
        modes[type.ordinal()][side.ordinal()] = side == RelativeSide.FRONT ? IoMode.NONE : mode;
    }

    public void cycle(TransferType type, RelativeSide side, boolean reverse) {
        IoMode[] modes = allowed(type);
        int i = 0;
        for (int k = 0; k < modes.length; k++) {
            if (modes[k] == get(type, side)) {
                i = k;
            }
        }
        set(type, side, modes[(i + (reverse ? modes.length - 1 : 1)) % modes.length]);
    }

    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putInt("a", packA());
        tag.putInt("b", packB());
        return tag;
    }

    public void load(CompoundTag tag) {
        unpack(tag.getInt("a"), tag.getInt("b"));
    }

    /** Предметы - биты 0-11, жидкости - 12-23, авто-вывод - 24 и 25. */
    public int packA() {
        int v = 0;
        for (TransferType t : new TransferType[]{TransferType.ITEMS, TransferType.FLUIDS}) {
            for (RelativeSide s : RelativeSide.values()) {
                int shift = t.ordinal() * 12 + s.ordinal() * 2;
                v |= get(t, s).ordinal() << shift;
            }
        }
        if (ejectItems) {
            v |= 1 << 24;
        }
        if (ejectFluids) {
            v |= 1 << 25;
        }
        return v;
    }

    /** Энергия - биты 0-11, каналы выходов предметов - по биту на грань с бита 12, бит 30 - признак нового формата. */
    public int packB() {
        int v = 1 << 30;
        for (RelativeSide s : RelativeSide.values()) {
            v |= get(TransferType.ENERGY, s).ordinal() << (s.ordinal() * 2);
            for (TransferType t : TransferType.OUTPUTS) {
                if (get(t, s).canOutput()) {
                    v |= 1 << (12 + t.outputIndex() * 6 + s.ordinal());
                }
            }
        }
        return v;
    }

    public void unpack(int a, int b) {
        for (TransferType t : new TransferType[]{TransferType.ITEMS, TransferType.FLUIDS}) {
            for (RelativeSide s : RelativeSide.values()) {
                int shift = t.ordinal() * 12 + s.ordinal() * 2;
                set(t, s, IoMode.values()[(a >> shift) & 3]);
            }
        }
        ejectItems = (a & (1 << 24)) != 0;
        ejectFluids = (a & (1 << 25)) != 0;
        boolean modern = (b & (1 << 30)) != 0;
        for (RelativeSide s : RelativeSide.values()) {
            set(TransferType.ENERGY, s, IoMode.values()[(b >> (s.ordinal() * 2)) & 3]);
            IoMode old = get(TransferType.ITEMS, s);       // у старых сохранений предметы были одним режимом
            if (!modern) {
                set(TransferType.ITEMS, s, coerce(TransferType.ITEMS, old));
            }
            for (TransferType t : TransferType.OUTPUTS) {
                boolean on = modern ? (b & (1 << (12 + t.outputIndex() * 6 + s.ordinal()))) != 0 : old.canOutput();
                set(t, s, on ? IoMode.OUTPUT : IoMode.NONE);
            }
        }
    }
}
