package dev.technogenesis.kontur.machine;

import java.util.ArrayList;
import java.util.List;

/** Описание машины: слоты, баки, энергия и расположение элементов в интерфейсе. Общее для сервера и клиента. */
public final class MachineDefinition {
    public enum SlotRole { INPUT, OUTPUT, FUEL, MODULE, COATING }

    public enum EnergyKind { CONSUMER, GENERATOR, STORAGE }

    public record SlotDef(int x, int y, SlotRole role) {
    }

    public record TankDef(int x, int y, int width, int height, int capacity, boolean output) {
    }

    public final List<SlotDef> slots;
    public final List<TankDef> tanks;
    public final EnergyKind energyKind;
    public final int energyCapacity;
    public final int maxReceive;
    public final int maxExtract;
    /** Предел потребления/выработки в FE/t, для подсказок. */
    public final int ratePerTick;
    public final int arrowX;
    public final int arrowY;
    public final int flameX;
    public final int flameY;

    private MachineDefinition(Builder b) {
        slots = List.copyOf(b.slots);
        tanks = List.copyOf(b.tanks);
        energyKind = b.energyKind;
        energyCapacity = b.energyCapacity;
        maxReceive = b.maxReceive;
        maxExtract = b.maxExtract;
        ratePerTick = b.rate;
        arrowX = b.arrowX;
        arrowY = b.arrowY;
        flameX = b.flameX;
        flameY = b.flameY;
    }

    /** Есть ли обычные слоты (кроме служебных слотов модуля и покрытия на вкладке). */
    public boolean hasItems() {
        for (SlotDef s : slots) {
            if (s.role() != SlotRole.MODULE && s.role() != SlotRole.COATING) {
                return true;
            }
        }
        return false;
    }

    public boolean hasFluids() {
        return !tanks.isEmpty();
    }

    /** Есть ли слот модуля форсирования. */
    public boolean hasModule() {
        return moduleSlot() >= 0;
    }

    /** Есть ли слот покрытия солнечной панели. */
    public boolean hasCoating() {
        return coatingSlot() >= 0;
    }

    public int coatingSlot() {
        for (int i = 0; i < slots.size(); i++) {
            if (slots.get(i).role() == SlotRole.COATING) {
                return i;
            }
        }
        return -1;
    }

    /** Слот на вкладке слева: модуль форсирования или покрытие. */
    public int tabSlot() {
        return hasModule() ? moduleSlot() : coatingSlot();
    }

    public int moduleSlot() {
        for (int i = 0; i < slots.size(); i++) {
            if (slots.get(i).role() == SlotRole.MODULE) {
                return i;
            }
        }
        return -1;
    }

    public boolean hasArrow() {
        return arrowX >= 0;
    }

    public boolean hasFlame() {
        return flameX >= 0;
    }

    /** Индекс входного слота или -1. */
    public int inputSlot() {
        for (int i = 0; i < slots.size(); i++) {
            if (slots.get(i).role() == SlotRole.INPUT) {
                return i;
            }
        }
        return -1;
    }

    public int[] outputSlots() {
        return java.util.stream.IntStream.range(0, slots.size())
                .filter(i -> slots.get(i).role() == SlotRole.OUTPUT).toArray();
    }

    public int inputTank() {
        for (int i = 0; i < tanks.size(); i++) {
            if (!tanks.get(i).output()) {
                return i;
            }
        }
        return -1;
    }

    public int outputTank() {
        for (int i = 0; i < tanks.size(); i++) {
            if (tanks.get(i).output()) {
                return i;
            }
        }
        return -1;
    }

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {
        private final List<SlotDef> slots = new ArrayList<>();
        private final List<TankDef> tanks = new ArrayList<>();
        private EnergyKind energyKind = EnergyKind.CONSUMER;
        private int energyCapacity;
        private int maxReceive;
        private int maxExtract;
        private int rate;
        private int arrowX = -1;
        private int arrowY = -1;
        private int flameX = -1;
        private int flameY = -1;

        public Builder slot(int x, int y, SlotRole role) {
            slots.add(new SlotDef(x, y, role));
            return this;
        }

        /** Слот модуля: добавляется последним, вне рабочей области (на вкладке слева от окна). */
        public Builder module(int x, int y) {
            slots.add(new SlotDef(x, y, SlotRole.MODULE));
            return this;
        }

        /** Слот покрытия: стоит там же, на вкладке слева. */
        public Builder coating(int x, int y) {
            slots.add(new SlotDef(x, y, SlotRole.COATING));
            return this;
        }

        public Builder tank(int x, int y, int capacity, boolean output) {
            tanks.add(new TankDef(x, y, 18, 52, capacity, output));
            return this;
        }

        public Builder energy(EnergyKind kind, int capacity, int receive, int extract, int rate) {
            this.energyKind = kind;
            this.energyCapacity = capacity;
            this.maxReceive = receive;
            this.maxExtract = extract;
            this.rate = rate;
            return this;
        }

        public Builder arrow(int x, int y) {
            this.arrowX = x;
            this.arrowY = y;
            return this;
        }

        public Builder flame(int x, int y) {
            this.flameX = x;
            this.flameY = y;
            return this;
        }

        public MachineDefinition build() {
            return new MachineDefinition(this);
        }
    }
}
