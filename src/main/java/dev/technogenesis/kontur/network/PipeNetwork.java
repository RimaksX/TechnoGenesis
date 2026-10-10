package dev.technogenesis.kontur.network;

import dev.technogenesis.kontur.blockentity.ConduitBlockEntity;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.capabilities.BlockCapabilityCache;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemHandlerHelper;

/**
 * Связная сеть труб одного вида (предметы или жидкости). Раз в interval тиков забирает из сторон с режимом
 * "забирать" и отдаёт в стороны с режимом "отдавать", но не больше amount за операцию (по самой слабой трубе).
 * Из точки в ту же самую точку ничего не возвращается, всё переносится только целиком и без потерь.
 */
public final class PipeNetwork {
    private static final int REFRESH_INTERVAL = 40;

    private final ServerLevel level;
    final ConduitKind kind;
    final Map<BlockPos, PipeTier> pipes = new HashMap<>();
    private final List<Endpoint<IItemHandler>> itemEnds = new ArrayList<>();
    private final List<Endpoint<IFluidHandler>> fluidEnds = new ArrayList<>();
    private boolean dirty = true;
    private long lastRefresh = Long.MIN_VALUE;
    private int rotation;
    private int lastMoved;

    private record Endpoint<T>(BlockPos pipe, Direction dir, ConduitMode mode, BlockCapabilityCache<T, Direction> cache) {
        T handler() {
            return cache.getCapability();
        }

        boolean same(Endpoint<?> other) {
            return pipe.equals(other.pipe) && dir == other.dir;
        }
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
    }

    private PipeTier weakest() {
        PipeTier min = null;
        for (PipeTier t : pipes.values()) {
            if (min == null || t.perTick() < min.perTick()) {
                min = t;
            }
        }
        return min;
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

    private void refreshEndpoints() {
        itemEnds.clear();
        fluidEnds.clear();
        for (BlockPos pos : pipes.keySet()) {
            if (!(level.getBlockEntity(pos) instanceof ConduitBlockEntity be)) {
                continue;
            }
            for (Direction d : Direction.values()) {
                BlockPos np = pos.relative(d);
                ConduitMode mode = be.mode(d);
                if (pipes.containsKey(np) || mode == ConduitMode.OFF || !level.isLoaded(np)) {
                    continue;
                }
                if (kind == ConduitKind.ITEMS) {
                    itemEnds.add(new Endpoint<>(pos, d, mode,
                            BlockCapabilityCache.create(Capabilities.ItemHandler.BLOCK, level, np, d.getOpposite())));
                } else {
                    fluidEnds.add(new Endpoint<>(pos, d, mode,
                            BlockCapabilityCache.create(Capabilities.FluidHandler.BLOCK, level, np, d.getOpposite())));
                }
            }
        }
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
    }

    private int moveItems(int budget) {
        List<Endpoint<IItemHandler>> sources = new ArrayList<>();
        List<Endpoint<IItemHandler>> sinks = new ArrayList<>();
        for (Endpoint<IItemHandler> e : itemEnds) {
            if (e.handler() == null) {
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
            IItemHandler from = src.handler();
            for (int slot = 0; slot < from.getSlots() && left > 0; slot++) {
                ItemStack probe = from.extractItem(slot, left, true);
                if (probe.isEmpty()) {
                    continue;
                }
                for (int s = 0; s < sinks.size(); s++) {
                    Endpoint<IItemHandler> dst = sinks.get((rotation + s) % sinks.size());
                    if (dst.same(src)) {
                        continue;
                    }
                    IItemHandler to = dst.handler();
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

    private int moveFluids(int budget) {
        List<Endpoint<IFluidHandler>> sources = new ArrayList<>();
        List<Endpoint<IFluidHandler>> sinks = new ArrayList<>();
        for (Endpoint<IFluidHandler> e : fluidEnds) {
            if (e.handler() == null) {
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
            IFluidHandler from = src.handler();
            FluidStack probe = from.drain(left, IFluidHandler.FluidAction.SIMULATE);
            if (probe.isEmpty()) {
                continue;
            }
            for (int s = 0; s < sinks.size() && left > 0; s++) {
                Endpoint<IFluidHandler> dst = sinks.get((rotation + s) % sinks.size());
                if (dst.same(src)) {
                    continue;
                }
                IFluidHandler to = dst.handler();
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
                break;
            }
        }
        return budget - left;
    }
}
