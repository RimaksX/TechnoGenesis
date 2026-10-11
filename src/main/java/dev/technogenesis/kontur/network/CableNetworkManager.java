package dev.technogenesis.kontur.network;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;

/** Хранит сети кабелей каждого мира: слияние при установке, разделение при удалении. Только на сервере. */
public final class CableNetworkManager {
    private static final Map<ResourceKey<Level>, Manager> MANAGERS = new HashMap<>();

    private CableNetworkManager() {
    }

    private static Manager of(ServerLevel level) {
        return MANAGERS.computeIfAbsent(level.dimension(), k -> new Manager(level));
    }

    public static void add(Level level, BlockPos pos, CableTier tier) {
        if (level instanceof ServerLevel sl) {
            of(sl).add(pos, tier);
        }
    }

    public static void remove(Level level, BlockPos pos) {
        if (level instanceof ServerLevel sl) {
            of(sl).remove(pos);
        }
    }

    /** Подключаемые устройства рядом с кабелем изменились: обновить список конечных точек. */
    public static void markDirty(Level level, BlockPos pos) {
        if (level instanceof ServerLevel sl) {
            Manager m = MANAGERS.get(sl.dimension());
            if (m != null) {
                CableNetwork n = m.byPos.get(pos);
                if (n != null) {
                    n.markDirty();
                }
            }
        }
    }

    /** Сведения о сети, в которой стоит кабель (для ключа). */
    public static CableNetwork.Info info(Level level, BlockPos pos) {
        if (level instanceof ServerLevel sl) {
            Manager m = MANAGERS.get(sl.dimension());
            if (m != null) {
                CableNetwork n = m.byPos.get(pos);
                if (n != null) {
                    if (n.splitPending) {
                        m.split(n);
                        n = m.byPos.get(pos);
                    }
                    return n.info();
                }
            }
        }
        return null;
    }

    public static void tick(Level level) {
        if (level instanceof ServerLevel sl) {
            Manager m = MANAGERS.get(sl.dimension());
            if (m != null) {
                m.tick();
            }
        }
    }

    public static void clear() {
        MANAGERS.clear();
    }

    private static final class Manager {
        private final ServerLevel level;
        final Map<BlockPos, CableNetwork> byPos = new HashMap<>();
        final Set<CableNetwork> networks = new LinkedHashSet<>();

        Manager(ServerLevel level) {
            this.level = level;
        }

        void add(BlockPos pos, CableTier tier) {
            BlockPos key = pos.immutable();
            CableNetwork existing = byPos.get(key);
            if (existing != null) {
                existing.cables.put(key, tier);
                existing.markDirty();
                return;
            }
            CableNetwork target = null;
            for (Direction d : Direction.values()) {
                CableNetwork n = byPos.get(key.relative(d));
                if (n != null && (target == null || n.cables.size() > target.cables.size())) {
                    target = n;
                }
            }
            if (target == null) {
                target = new CableNetwork(level);
                networks.add(target);
            } else {
                for (Direction d : Direction.values()) {
                    CableNetwork n = byPos.get(key.relative(d));
                    if (n != null && n != target && networks.remove(n)) {
                        for (Map.Entry<BlockPos, CableTier> e : n.cables.entrySet()) {
                            target.cables.put(e.getKey(), e.getValue());
                            byPos.put(e.getKey(), target);
                        }
                        target.splitPending |= n.splitPending;
                    }
                }
            }
            target.cables.put(key, tier);
            byPos.put(key, target);
            target.markDirty();
        }

        /** Удаление - О(1), проверка на распад откладывается до тика (см. PipeNetworkManager). */
        void remove(BlockPos pos) {
            CableNetwork net = byPos.remove(pos);
            if (net == null) {
                return;
            }
            net.cables.remove(pos);
            if (net.cables.isEmpty()) {
                networks.remove(net);
                return;
            }
            net.splitPending = true;
            net.markDirty();
        }

        void tick() {
            for (CableNetwork n : new ArrayList<>(networks)) {
                if (n.splitPending) {
                    split(n);
                }
                n.tick();
            }
        }

        void split(CableNetwork net) {
            net.splitPending = false;
            Set<BlockPos> seen = new HashSet<>();
            List<Set<BlockPos>> parts = new ArrayList<>();
            for (BlockPos start : net.cables.keySet()) {
                if (seen.contains(start)) {
                    continue;
                }
                Set<BlockPos> part = new HashSet<>();
                ArrayDeque<BlockPos> queue = new ArrayDeque<>();
                queue.add(start);
                part.add(start);
                while (!queue.isEmpty()) {
                    BlockPos p = queue.poll();
                    for (Direction d : Direction.values()) {
                        BlockPos q = p.relative(d);
                        if (net.cables.containsKey(q) && part.add(q)) {
                            queue.add(q);
                        }
                    }
                }
                seen.addAll(part);
                parts.add(part);
            }
            net.markDirty();
            if (parts.size() <= 1) {
                return;
            }
            Map<BlockPos, CableTier> all = new HashMap<>(net.cables);
            net.cables.clear();
            for (int i = 0; i < parts.size(); i++) {
                CableNetwork target = i == 0 ? net : new CableNetwork(level);
                if (i > 0) {
                    networks.add(target);
                }
                for (BlockPos p : parts.get(i)) {
                    target.cables.put(p, all.get(p));
                    byPos.put(p, target);
                }
                target.markDirty();
            }
        }
    }
}
