package dev.technogenesis.kontur.machine;

import net.neoforged.neoforge.energy.EnergyStorage;

/** Буфер FE машины с внутренними операциями без лимитов передачи. */
public class KonturEnergyStorage extends EnergyStorage {
    public KonturEnergyStorage(int capacity, int maxReceive, int maxExtract) {
        super(capacity, maxReceive, maxExtract);
    }

    /** Списывает до amount, возвращает списанное. */
    public int consume(int amount) {
        int taken = Math.min(Math.max(0, amount), energy);
        energy -= taken;
        return taken;
    }

    /** Добавляет до amount с учётом ёмкости, возвращает добавленное. */
    public int produce(int amount) {
        int added = Math.min(Math.max(0, amount), capacity - energy);
        energy += added;
        return added;
    }

    /** Меняет ёмкость и предел приёма (модуль форсирования), лишний заряд отбрасывается. */
    public void setLimits(int newCapacity, int newMaxReceive) {
        this.capacity = newCapacity;
        this.maxReceive = newMaxReceive;
        if (energy > capacity) {
            energy = capacity;
        }
    }

    public int space() {
        return capacity - energy;
    }

    public void setStored(int value) {
        energy = Math.max(0, Math.min(capacity, value));
    }
}
