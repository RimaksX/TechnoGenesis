package dev.technogenesis.kontur.machine;

import net.minecraft.nbt.CompoundTag;

/** Режимы сторон для предметов, жидкостей и энергии плюс флаги авто-вывода. */
public final class SideConfig {
    private final IoMode[][] modes = new IoMode[TransferType.values().length][RelativeSide.values().length];
    public boolean ejectItems;
    public boolean ejectFluids;

    public SideConfig(IoMode items, IoMode fluids, IoMode energy) {
        fill(TransferType.ITEMS, items);
        fill(TransferType.FLUIDS, fluids);
        fill(TransferType.ENERGY, energy);
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
        IoMode m = get(type, side);
        set(type, side, reverse ? m.prev() : m.next());
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

    /** Энергия - биты 0-11. */
    public int packB() {
        int v = 0;
        for (RelativeSide s : RelativeSide.values()) {
            v |= get(TransferType.ENERGY, s).ordinal() << (s.ordinal() * 2);
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
        for (RelativeSide s : RelativeSide.values()) {
            set(TransferType.ENERGY, s, IoMode.values()[(b >> (s.ordinal() * 2)) & 3]);
        }
    }
}
