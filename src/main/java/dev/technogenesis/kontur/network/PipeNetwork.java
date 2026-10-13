package dev.technogenesis.kontur.network;

import dev.technogenesis.kontur.blockentity.ConduitBlockEntity;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.registry.KonturFluids;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.capabilities.BlockCapabilityCache;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemHandlerHelper;

/**
 * Связная сеть труб одного вида (предметы, жидкости или газы). Раз в interval тиков забирает из сторон с режимом
 * "забирать" и отдаёт в стороны с режимом "отдавать", но не больше amount за операцию (по самой слабой трубе).
 * Из точки в ту же самую точку ничего не возвращается, всё переносится только целиком и без потерь.
 */
public final class PipeNetwork {
    private static final int REFRESH_INTERVAL = 200;

    private final ServerLevel level;
    final ConduitKind kind;
    final Map<BlockPos, PipeTier> pipes = new HashMap<>();
    private List<Endpoint<IItemHandler>> itemEnds = new ArrayList<>();
    private List<Endpoint<IFluidHandler>> fluidEnds = new ArrayList<>();
    private Map<EndKey, BlockCapabilityCache<IItemHandler, Direction>> itemCaches = new HashMap<>();
    private Map<EndKey, BlockCapabilityCache<IFluidHandler, Direction>> fluidCaches = new HashMap<>();
    /** Распад сети проверяется один раз за тик, а не при каждом удалении трубы (см. менеджер). */
    boolean splitPending;
    private PipeTier weakCache;
    private boolean weakStale = true;
    private boolean dirty = true;
    private long lastRefresh = Long.MIN_VALUE;
    private int rotation;
    private int lastMoved;
    private int idleOps;
    private Fluid lastFluid = Fluids.EMPTY;

    /** machine - по ту сторону машина Контура: её приёмники имеют приоритет над сундуками и баками. */
    private record Endpoint<T>(BlockPos pipe, Direction dir, ConduitMode mode, boolean machine,
                               BlockCapabilityCache<T, Direction> cache) {
        /** Соседний чанк выгружен - способность не запрашивается, чтобы не загрузить его принудительно. */
        T handler(ServerLevel level) {
            return level.isLoaded(pipe.relative(dir)) ? cache.getCapability() : null;
        }

        boolean same(Endpoint<?> other) {
            return pipe.equals(other.pipe) && dir == other.dir;
        }
    }

    private record EndKey(BlockPos pipe, Direction dir) {
    }

    /** Для диагностики ключом. */
    public record Info(PipeTier weakest, int pipes, int sources, int sinks, int moved) {
    }

    PipeNetwork(ServerLevel level, ConduitKind kind) {
        this.level = level;
        this.kind = kind;
    }

    void markDirty() {
        dirty = true;
        weakStale = true;
    }

    /** Самая слабая труба сети; считается только после изменения состава сети, а не каждый тик. */
    private PipeTier weakest() {
        if (weakStale) {
            PipeTier min = null;
            for (PipeTier t : pipes.values()) {
                if (min == null || t.perTick() < min.perTick()) {
                    min = t;
                }
            }
            weakCache = min;
            weakStale = false;
        }
        return weakCache;
    }

    public Info info() {
        int src = 0;
        int dst = 0;
        if (kind == ConduitKind.ITEMS) {
            for (Endpoint<IItemHandler> e : itemEnds) {
                src += e.mode.pulls() ? 1 : 0;
                dst += e.mode.pushes() ? 1 : 0;
            }
        } else {
            for (Endpoint<IFluidHandler> e : fluidEnds) {
                src += e.mode.pulls() ? 1 : 0;
                dst += e.mode.pushes() ? 1 : 0;
            }
        }
        return new Info(weakest(), pipes.size(), src, dst, lastMoved);
    }

    /** Конечные точки пересобираются редко, а кэши способностей берутся прежние: их создание дорого. */
    private void refreshEndpoints() {
        List<Endpoint<IItemHandler>> newItems = new ArrayList<>();
        List<Endpoint<IFluidHandler>> newFluids = new ArrayList<>();
        Map<EndKey, BlockCapabilityCache<IItemHandler, Direction>> newItemCaches = new HashMap<>();
        Map<EndKey, BlockCapabilityCache<IFluidHandler, Direction>> newFluidCaches = new HashMap<>();
        for (BlockPos pos : pipes.keySet()) {
            if (!(level.getBlockEntity(pos) instanceof ConduitBlockEntity be)) {
                continue;
            }
            for (Direction d : Direction.values()) {
                BlockPos np = pos.relative(d);
                if (pipes.containsKey(np) || be.mode(d) == ConduitMode.OFF || !level.isLoaded(np)) {
                    continue;
                }
                boolean machine = level.getBlockState(np).getBlock() instanceof dev.technogenesis.kontur.block.MachineBlock;
                ConduitMode mode = be.mode(d).resolve(machine);
                EndKey key = new EndKey(pos, d);
                if (kind == ConduitKind.ITEMS) {
                    BlockCapabilityCache<IItemHandler, Direction> cache = itemCaches.get(key);
                    if (cache == null) {
                        cache = BlockCapabilityCache.create(Capabilities.ItemHandler.BLOCK, level, np, d.getOpposite());
                    }
                    newItemCaches.put(key, cache);
                    newItems.add(new Endpoint<>(pos, d, mode, machine, cache));
                } else {
                    BlockCapabilityCache<IFluidHandler, Direction> cache = fluidCaches.get(key);
                    if (cache == null) {
                        cache = BlockCapabilityCache.create(Capabilities.FluidHandler.BLOCK, level, np, d.getOpposite());
                    }
                    newFluidCaches.put(key, cache);
                    newFluids.add(new Endpoint<>(pos, d, mode, machine, cache));
                }
            }
        }
        itemEnds = newItems;
        fluidEnds = newFluids;
        itemCaches = newItemCaches;
        fluidCaches = newFluidCaches;
        dirty = false;
        lastRefresh = level.getGameTime();
    }

    void tick() {
        if (pipes.isEmpty()) {
            return;
        }
        PipeTier weak = weakest();
        if (level.getGameTime() % weak.interval != 0) {
            return;
        }
        if (dirty || level.getGameTime() - lastRefresh >= REFRESH_INTERVAL) {
            refreshEndpoints();
        }
        rotation++;
        lastMoved = kind == ConduitKind.ITEMS ? moveItems(weak.amount) : moveFluids(weak.amount);
        if (kind == ConduitKind.FLUIDS) {
            // по прозрачным трубам видно, что течёт: жидкость гаснет, если перенос стоит несколько секунд
            if (lastMoved > 0) {
                idleOps = 0;
                showFluid(lastFluid);
            } else if (++idleOps * weak.interval >= 60) {
                showFluid(Fluids.EMPTY);
            }
        }
    }

    private void showFluid(Fluid fluid) {
        for (BlockPos pos : pipes.keySet()) {
            if (level.getBlockEntity(pos) instanceof ConduitBlockEntity be) {
                be.setDisplayFluid(fluid);
            }
        }
    }

    private int moveItems(int budget) {
        List<Endpoint<IItemHandler>> sources = new ArrayList<>();
        List<Endpoint<IItemHandler>> sinks = new ArrayList<>();
        for (Endpoint<IItemHandler> e : itemEnds) {
            if (e.handler(level) == null) {
                continue;
            }
            if (e.mode.pulls()) {
                sources.add(e);
            }
            if (e.mode.pushes()) {
                sinks.add(e);
            }
        }
        if (sources.isEmpty() || sinks.isEmpty()) {
            return 0;
        }
        int left = budget;
        for (int k = 0; k < sources.size() && left > 0; k++) {
            Endpoint<IItemHandler> src = sources.get((rotation + k) % sources.size());
            IItemHandler from = src.handler(level);
            for (int slot = 0; slot < from.getSlots() && left > 0; slot++) {
                ItemStack probe = from.extractItem(slot, left, true);
                if (probe.isEmpty()) {
                    continue;
                }
                List<Endpoint<IItemHandler>> targets = itemTargets(sinks, probe);
                for (int s = 0; s < targets.size(); s++) {
                    Endpoint<IItemHandler> dst = targets.get((rotation + s) % targets.size());
                    if (dst.same(src)) {
                        continue;
                    }
                    IItemHandler to = dst.handler(level);
                    ItemStack rest = ItemHandlerHelper.insertItem(to, probe.copy(), true);
                    int fits = probe.getCount() - rest.getCount();
                    if (fits <= 0) {
                        continue;
                    }
                    ItemStack taken = from.extractItem(slot, fits, false);
                    if (taken.isEmpty()) {
                        break;
                    }
                    ItemStack notInserted = ItemHandlerHelper.insertItem(to, taken, false);
                    if (!notInserted.isEmpty()) {
                        ItemHandlerHelper.insertItem(from, notInserted, false);
                    }
                    left -= taken.getCount() - notInserted.getCount();
                    break;
                }
            }
        }
        return budget - left;
    }

    /**
     * Если предмет вообще годится какой-то машине в сети (пусть сейчас у неё нет места), он идёт только к машинам и
     * ждёт места, а не уходит в сундук. Предмет, который не нужен ни одной машине (например, пустая порода),
     * свободно идёт в остальные приёмники.
     */
    private List<Endpoint<IItemHandler>> itemTargets(List<Endpoint<IItemHandler>> sinks, ItemStack stack) {
        List<Endpoint<IItemHandler>> wanted = new ArrayList<>();
        for (Endpoint<IItemHandler> e : sinks) {
            if (e.machine) {
                IItemHandler h = e.handler(level);
                for (int i = 0; h != null && i < h.getSlots(); i++) {
                    if (h.isItemValid(i, stack)) {
                        wanted.add(e);
                        break;
                    }
                }
            }
        }
        return wanted.isEmpty() ? sinks : wanted;
    }

    private List<Endpoint<IFluidHandler>> fluidTargets(List<Endpoint<IFluidHandler>> sinks, FluidStack stack) {
        List<Endpoint<IFluidHandler>> wanted = new ArrayList<>();
        for (Endpoint<IFluidHandler> e : sinks) {
            if (e.machine) {
                IFluidHandler h = e.handler(level);
                for (int i = 0; h != null && i < h.getTanks(); i++) {
                    if (h.isFluidValid(i, stack)) {
                        wanted.add(e);
                        break;
                    }
                }
            }
        }
        return wanted.isEmpty() ? sinks : wanted;
    }

    /** Газовая сеть возит только газы, сеть жидкостей - всё, кроме газов, которым нужны газовые трубы. */
    private boolean carries(Fluid fluid) {
        return kind == ConduitKind.GASES ? KonturFluids.isGas(fluid) : !KonturFluids.needsGasPipe(fluid);
    }

    private int moveFluids(int budget) {
        List<Endpoint<IFluidHandler>> sources = new ArrayList<>();
        List<Endpoint<IFluidHandler>> sinks = new ArrayList<>();
        for (Endpoint<IFluidHandler> e : fluidEnds) {
            if (e.handler(level) == null) {
                continue;
            }
            if (e.mode.pulls()) {
                sources.add(e);
            }
            if (e.mode.pushes()) {
                sinks.add(e);
            }
        }
        if (sources.isEmpty() || sinks.isEmpty()) {
            return 0;
        }
        int left = budget;
        for (int k = 0; k < sources.size() && left > 0; k++) {
            Endpoint<IFluidHandler> src = sources.get((rotation + k) % sources.size());
            IFluidHandler from = src.handler(level);
            FluidStack probe = from.drain(left, IFluidHandler.FluidAction.SIMULATE);
            if (probe.isEmpty() || !carries(probe.getFluid())) {
                continue;
            }
            List<Endpoint<IFluidHandler>> targets = fluidTargets(sinks, probe);
            for (int s = 0; s < targets.size() && left > 0; s++) {
                Endpoint<IFluidHandler> dst = targets.get((rotation + s) % targets.size());
                if (dst.same(src)) {
                    continue;
                }
                IFluidHandler to = dst.handler(level);
                int fits = to.fill(probe.copyWithAmount(Math.min(probe.getAmount(), left)), IFluidHandler.FluidAction.SIMULATE);
                if (fits <= 0) {
                    continue;
                }
                FluidStack drained = from.drain(probe.copyWithAmount(fits), IFluidHandler.FluidAction.EXECUTE);
                if (drained.isEmpty()) {
                    continue;
                }
                int filled = to.fill(drained, IFluidHandler.FluidAction.EXECUTE);
                if (filled < drained.getAmount()) {
                    from.fill(drained.copyWithAmount(drained.getAmount() - filled), IFluidHandler.FluidAction.EXECUTE);
                }
                left -= filled;
                if (filled > 0) {
                    lastFluid = drained.getFluid();
                }
                break;
            }
        }
        return budget - left;
    }
}
