package dev.technogenesis.kontur.machine;

import java.util.ArrayList;
import java.util.List;

/** Описание машины: слоты, баки, энергия и расположение элементов в интерфейсе. Общее для сервера и клиента. */
public final class MachineDefinition {
    public enum SlotRole { INPUT, OUTPUT, FUEL, MODULE, COATING, COOLER }

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
    /** Все выходные слоты делят один канал (буфер шахтёра), а не получают отдельные грани. */
    public final boolean singleOutputChannel;
    private final int[] outputSlotCache;

    private MachineDefinition(Builder b) {
        singleOutputChannel = b.singleOutputChannel;
        slots = List.copyOf(b.slots);
        outputSlotCache = java.util.stream.IntStream.range(0, slots.size())
                .filter(i -> slots.get(i).role() == SlotRole.OUTPUT).toArray();
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
            if (s.role() != SlotRole.MODULE && s.role() != SlotRole.COATING && s.role() != SlotRole.COOLER) {
                return true;
            }
        }
        return false;
    }

    public boolean hasFluids() {
        return !tanks.isEmpty();
    }

    /** Типы передачи, которые у машины вообще есть (общее для сервера и экрана настройки сторон). */
    public boolean supports(TransferType type) {
        return switch (type) {
            case ITEMS -> inputSlot() >= 0 || hasFuelSlot();
            case FLUIDS -> hasFluids();
            case ENERGY -> energyCapacity > 0;
            case OUT1, OUT2, OUT3 -> outputChannels() > type.outputIndex();
        };
    }

    /**
     * Режимы грани, которые для типа вообще имеют смысл. Входы предметов - только вход, каждый выход - только выход;
     * жидкости зависят от баков (насос с одним выходным баком только выпускает), энергия - от вида машины
     * (потребитель только принимает, генератор только отдаёт, накопитель и то и другое).
     */
    public IoMode[] allowedModes(TransferType type) {
        return switch (type) {
            case ITEMS -> new IoMode[]{IoMode.NONE, IoMode.INPUT};
            case OUT1, OUT2, OUT3 -> new IoMode[]{IoMode.NONE, IoMode.OUTPUT};
            case FLUIDS -> {
                boolean in = inputTank() >= 0;
                boolean out = outputTank() >= 0;
                yield in && out ? new IoMode[]{IoMode.NONE, IoMode.INPUT, IoMode.OUTPUT, IoMode.ALL}
                        : in ? new IoMode[]{IoMode.NONE, IoMode.INPUT}
                        : new IoMode[]{IoMode.NONE, IoMode.OUTPUT};
            }
            case ENERGY -> switch (energyKind) {
                case CONSUMER -> new IoMode[]{IoMode.NONE, IoMode.INPUT};
                case GENERATOR -> new IoMode[]{IoMode.NONE, IoMode.OUTPUT};
                case STORAGE -> new IoMode[]{IoMode.NONE, IoMode.INPUT, IoMode.OUTPUT, IoMode.ALL};
            };
        };
    }

    /** Приводит желаемый режим к допустимому для типа: вход остаётся входом, только если вход вообще возможен. */
    public IoMode coerce(TransferType type, IoMode wanted) {
        IoMode[] allowed = allowedModes(type);
        boolean hasIn = false;
        boolean hasOut = false;
        for (IoMode m : allowed) {
            if (m == wanted) {
                return m;
            }
            hasIn |= m == IoMode.INPUT;
            hasOut |= m == IoMode.OUTPUT;
        }
        if (wanted.canInput() && hasIn) {
            return IoMode.INPUT;
        }
        if (wanted.canOutput() && hasOut) {
            return IoMode.OUTPUT;
        }
        return IoMode.NONE;
    }

    /** Режим по умолчанию для жидкостей: по тому, какие баки есть. */
    public IoMode defaultFluidMode() {
        IoMode[] a = allowedModes(TransferType.FLUIDS);
        return a[a.length - 1];
    }

    private boolean hasFuelSlot() {
        for (SlotDef s : slots) {
            if (s.role() == SlotRole.FUEL) {
                return true;
            }
        }
        return false;
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

    /** Есть ли слот радиатора (охлаждение модуля). */
    public boolean hasCooler() {
        return coolerSlot() >= 0;
    }

    public int coolerSlot() {
        for (int i = 0; i < slots.size(); i++) {
            if (slots.get(i).role() == SlotRole.COOLER) {
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

    /** Сколько каналов выхода у машины: по слоту на канал, но не больше трёх, у буфера шахтёра один. */
    public int outputChannels() {
        int n = outputSlotCache.length;
        return singleOutputChannel ? Math.min(1, n) : Math.min(3, n);
    }

    /** Индексы выходных слотов (массив общий, не изменять). */
    public int[] outputSlots() {
        return outputSlotCache;
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
        private boolean singleOutputChannel;

        public Builder slot(int x, int y, SlotRole role) {
            slots.add(new SlotDef(x, y, role));
            return this;
        }

        /** Слот модуля: добавляется последним, вне рабочей области (на вкладке слева от окна). */
        public Builder module(int x, int y) {
            slots.add(new SlotDef(x, y, SlotRole.MODULE));
            return this;
        }

        /** Слот радиатора: на вкладке слева под слотом модуля. */
        public Builder cooler(int x, int y) {
            slots.add(new SlotDef(x, y, SlotRole.COOLER));
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

        /** Все выходные слоты - один канал выхода. */
        public Builder singleOutputChannel() {
            this.singleOutputChannel = true;
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
