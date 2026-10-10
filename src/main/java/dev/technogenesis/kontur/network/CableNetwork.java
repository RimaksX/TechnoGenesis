package dev.technogenesis.kontur.network;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.neoforge.capabilities.BlockCapabilityCache;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.energy.IEnergyStorage;

/**
 * Связная сеть кабелей. Каждый тик переносит FE от источников к потребителям не быстрее самого слабого кабеля
 * сети. Генераторы - это обработчики, которые отдают, но не принимают; потребители - наоборот; накопители умеют
 * и то и другое: их заряжают излишком и разряжают при нехватке. Энергия не создаётся и не пропадает.
 */
public final class CableNetwork {
    private static final int REFRESH_INTERVAL = 40;

    private final ServerLevel level;
    final Map<BlockPos, CableTier> cables = new HashMap<>();
    private final List<BlockCapabilityCache<IEnergyStorage, Direction>> endpoints = new ArrayList<>();
    private boolean dirty = true;
    private int lastSources;
    private int lastSinks;
    private int lastStorages;
    private int lastMoved;
    private long lastRefresh = Long.MIN_VALUE;

    CableNetwork(ServerLevel level) {
        this.level = level;
    }

    void markDirty() {
        dirty = true;
    }

    /** Для диагностики ключом: слабейший кабель, число кабелей, источников, потребителей, накопителей и перенос за тик. */
    public record Info(CableTier weakest, int cables, int sources, int sinks, int storages, int moved) {
    }

    public Info info() {
        CableTier weakest = null;
        for (CableTier t : cables.values()) {
            if (weakest == null || t.throughput < weakest.throughput) {
                weakest = t;
            }
        }
        return new Info(weakest, cables.size(), lastSources, lastSinks, lastStorages, lastMoved);
    }

    public int throughput() {
        int min = Integer.MAX_VALUE;
        for (CableTier t : cables.values()) {
            min = Math.min(min, t.throughput);
        }
        return min == Integer.MAX_VALUE ? 0 : min;
    }

    private void refreshEndpoints() {
        endpoints.clear();
        for (BlockPos pos : cables.keySet()) {
            for (Direction d : Direction.values()) {
                BlockPos np = pos.relative(d);
                if (cables.containsKey(np) || !level.isLoaded(np)) {
                    continue;
                }
                endpoints.add(BlockCapabilityCache.create(Capabilities.EnergyStorage.BLOCK, level, np, d.getOpposite()));
            }
        }
        dirty = false;
        lastRefresh = level.getGameTime();
    }

    void tick() {
        if (cables.isEmpty()) {
            return;
        }
        if (dirty || level.getGameTime() - lastRefresh >= REFRESH_INTERVAL) {
            refreshEndpoints();
        }
        List<IEnergyStorage> sources = new ArrayList<>();
        List<IEnergyStorage> sinks = new ArrayList<>();
        List<IEnergyStorage> storages = new ArrayList<>();
        for (BlockCapabilityCache<IEnergyStorage, Direction> ep : endpoints) {
            IEnergyStorage h = ep.getCapability();
            if (h == null) {
                continue;
            }
            boolean receive = h.canReceive();
            boolean extract = h.canExtract();
            if (extract && !receive) {
                sources.add(h);
            } else if (receive && !extract) {
                sinks.add(h);
            } else if (receive) {
                storages.add(h);
            }
        }
        int cap = throughput();
        lastSources = sources.size();
        lastSinks = sinks.size();
        lastStorages = storages.size();
        int moved = move(sources, sinks, cap);
        int left = cap - moved;
        if (left > 0 && !storages.isEmpty()) {
            int toStorage = move(sources, storages, left);
            moved += toStorage;
            left -= toStorage;
            if (left > 0) {
                moved += move(storages, sinks, left);
            }
        }
        lastMoved = moved;
    }

    /** Переносит до limit FE; возвращает перенесённое. */
    static int move(List<IEnergyStorage> from, List<IEnergyStorage> to, int limit) {
        if (from.isEmpty() || to.isEmpty() || limit <= 0) {
            return 0;
        }
        int[] offer = new int[from.size()];
        int supply = 0;
        for (int i = 0; i < offer.length; i++) {
            offer[i] = from.get(i).extractEnergy(limit, true);
            supply += offer[i];
        }
        int[] accept = new int[to.size()];
        int demand = 0;
        for (int j = 0; j < accept.length; j++) {
            accept[j] = to.get(j).receiveEnergy(limit, true);
            demand += accept[j];
        }
        int amount = Math.min(limit, Math.min(supply, demand));
        if (amount <= 0) {
            return 0;
        }
        int[] give = allocate(offer, amount);
        int[] take = allocate(accept, amount);
        int extracted = 0;
        for (int i = 0; i < give.length; i++) {
            if (give[i] > 0) {
                extracted += from.get(i).extractEnergy(give[i], false);
            }
        }
        int delivered = 0;
        int budget = extracted;
        for (int j = 0; j < take.length && budget > 0; j++) {
            int part = Math.min(take[j], budget);
            if (part > 0) {
                int got = to.get(j).receiveEnergy(part, false);
                delivered += got;
                budget -= got;
            }
        }
        return delivered;
    }

    /** Справедливое распределение: меньшие потребности удовлетворяются полностью, остаток делится поровну. */
    static int[] allocate(int[] caps, int amount) {
        int n = caps.length;
        Integer[] order = new Integer[n];
        for (int i = 0; i < n; i++) {
            order[i] = i;
        }
        java.util.Arrays.sort(order, (a, b) -> Integer.compare(caps[a], caps[b]));
        int[] out = new int[n];
        int remaining = amount;
        for (int k = 0; k < n; k++) {
            int idx = order[k];
            int left = n - k;
            int share = (remaining + left - 1) / left;
            int v = Math.min(caps[idx], share);
            out[idx] = v;
            remaining -= v;
        }
        return out;
    }
}
