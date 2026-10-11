package dev.technogenesis.kontur.network;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.EnumMap;
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
import org.jetbrains.annotations.Nullable;

/** Сети труб предметов и жидкостей каждого мира: слияние при установке, разделение при удалении. Только сервер. */
public final class PipeNetworkManager {
    private static final Map<ResourceKey<Level>, Map<ConduitKind, Manager>> MANAGERS = new HashMap<>();

    private PipeNetworkManager() {
    }

    private static Manager of(ServerLevel level, ConduitKind kind) {
        return MANAGERS.computeIfAbsent(level.dimension(), k -> new EnumMap<>(ConduitKind.class))
                .computeIfAbsent(kind, k -> new Manager(level, kind));
    }

    public static void add(Level level, BlockPos pos, PipeTier tier) {
        if (level instanceof ServerLevel sl) {
            of(sl, tier.kind).add(pos, tier);
        }
    }

    public static void remove(Level level, BlockPos pos, ConduitKind kind) {
        if (level instanceof ServerLevel sl) {
            of(sl, kind).remove(pos);
        }
    }

    /** Рядом с трубой что-то изменилось: список точек подключения надо собрать заново. */
    public static void markDirty(Level level, BlockPos pos) {
        if (level instanceof ServerLevel sl) {
            Map<ConduitKind, Manager> byKind = MANAGERS.get(sl.dimension());
            if (byKind != null) {
                for (Manager m : byKind.values()) {
                    PipeNetwork n = m.byPos.get(pos);
                    if (n != null) {
                        n.markDirty();
                    }
                }
            }
        }
    }

    /** Сведения о сети, в которой стоит труба (для ключа). */
    @Nullable
    public static PipeNetwork.Info info(Level level, BlockPos pos) {
        if (level instanceof ServerLevel sl) {
            Map<ConduitKind, Manager> byKind = MANAGERS.get(sl.dimension());
            if (byKind != null) {
                for (Manager m : byKind.values()) {
                    PipeNetwork n = m.byPos.get(pos);
                    if (n != null) {
                        if (n.splitPending) {
                            m.split(n);
                            n = m.byPos.get(pos);
                        }
                        return n.info();
                    }
                }
            }
        }
        return null;
    }

    public static void tick(Level level) {
        if (level instanceof ServerLevel sl) {
            Map<ConduitKind, Manager> byKind = MANAGERS.get(sl.dimension());
            if (byKind != null) {
                for (Manager m : byKind.values()) {
                    m.tick();
                }
            }
        }
    }

    public static void clear() {
        MANAGERS.clear();
    }

    private static final class Manager {
        private final ServerLevel level;
        private final ConduitKind kind;
        final Map<BlockPos, PipeNetwork> byPos = new HashMap<>();
        final Set<PipeNetwork> networks = new LinkedHashSet<>();

        Manager(ServerLevel level, ConduitKind kind) {
            this.level = level;
            this.kind = kind;
        }

        void add(BlockPos pos, PipeTier tier) {
            BlockPos key = pos.immutable();
            PipeNetwork existing = byPos.get(key);
            if (existing != null) {
                existing.pipes.put(key, tier);
                existing.markDirty();
                return;
            }
            // соседние сети сливаются в самую большую: меньшие переносятся в неё, а не наоборот
            PipeNetwork target = null;
            for (Direction d : Direction.values()) {
                PipeNetwork n = byPos.get(key.relative(d));
                if (n != null && (target == null || n.pipes.size() > target.pipes.size())) {
                    target = n;
                }
            }
            if (target == null) {
                target = new PipeNetwork(level, kind);
                networks.add(target);
            } else {
                for (Direction d : Direction.values()) {
                    PipeNetwork n = byPos.get(key.relative(d));
                    if (n != null && n != target && networks.remove(n)) {
                        for (Map.Entry<BlockPos, PipeTier> e : n.pipes.entrySet()) {
                            target.pipes.put(e.getKey(), e.getValue());
                            byPos.put(e.getKey(), target);
                        }
                        target.splitPending |= n.splitPending;
                    }
                }
            }
            target.pipes.put(key, tier);
            byPos.put(key, target);
            target.markDirty();
        }

        /**
         * Удаление трубы (в том числе при выгрузке чанка) - О(1): проверка на распад сети откладывается и выполняется
         * один раз за тик. Иначе выгрузка чанка с большой сетью разбирала бы её по одной трубе с обходом всей сети каждый раз.
         */
        void remove(BlockPos pos) {
            PipeNetwork net = byPos.remove(pos);
            if (net == null) {
                return;
            }
            net.pipes.remove(pos);
            if (net.pipes.isEmpty()) {
                networks.remove(net);
                return;
            }
            net.splitPending = true;
            net.markDirty();
        }

        void tick() {
            for (PipeNetwork n : new ArrayList<>(networks)) {
                if (n.splitPending) {
                    split(n);
                }
                n.tick();
            }
        }

        void split(PipeNetwork net) {
            net.splitPending = false;
            Set<BlockPos> seen = new HashSet<>();
            List<Set<BlockPos>> parts = new ArrayList<>();
            for (BlockPos start : net.pipes.keySet()) {
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
                        if (net.pipes.containsKey(q) && part.add(q)) {
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
            Map<BlockPos, PipeTier> all = new HashMap<>(net.pipes);
            net.pipes.clear();
            for (int i = 0; i < parts.size(); i++) {
                PipeNetwork target = i == 0 ? net : new PipeNetwork(level, kind);
                if (i > 0) {
                    networks.add(target);
                }
                for (BlockPos p : parts.get(i)) {
                    target.pipes.put(p, all.get(p));
                    byPos.put(p, target);
                }
                target.markDirty();
            }
        }
    }
}
