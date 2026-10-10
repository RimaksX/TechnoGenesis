package dev.technogenesis.kontur.miner;

import dev.technogenesis.kontur.block.MinerRailBlock;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Проверка постройки шахтёра: рамка из направляющих должна быть замкнутым прямоугольником на одном уровне, ядро стоит в
 * её углу лицом наружу, а внутри на уровне направляющих и на блок выше нет препятствий для головки.
 * Для голограммы запоминаются недостающие клетки рамки и первые мешающие блоки.
 */
public final class MinerScan {
    public enum Error { NONE, NOT_CLOSED, EXTRA, SIZE, CORNER, FRONT, BLOCKED }

    public static final int MIN_OUTER = 5;
    private static final int MAX_LISTED = 48;

    public final Error error;
    public final MinerFrame frame;
    public final long[] missing;
    public final long[] obstacles;
    /** Часть области лежит в незагруженных чанках: проверить нельзя, работать тоже. */
    public final boolean unloaded;

    public MinerScan(Error error, MinerFrame frame, long[] missing, long[] obstacles, boolean unloaded) {
        this.error = error;
        this.frame = frame;
        this.missing = missing;
        this.obstacles = obstacles;
        this.unloaded = unloaded;
    }

    public boolean ok() {
        return error == Error.NONE && !unloaded;
    }

    public boolean sameAs(MinerScan other) {
        return other != null && error == other.error && unloaded == other.unloaded
                && java.util.Objects.equals(frame, other.frame)
                && java.util.Arrays.equals(missing, other.missing) && java.util.Arrays.equals(obstacles, other.obstacles);
    }

    /** Можно ли головке и балке проходить через эту клетку: нет столкновений и нет жидкости. */
    public static boolean passable(Level level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        return state.getCollisionShape(level, pos).isEmpty() && state.getFluidState().isEmpty();
    }

    public static MinerScan scan(Level level, BlockPos core, Direction front, int maxOuter) {
        int y = core.getY();
        Set<BlockPos> rails = new HashSet<>();
        ArrayDeque<BlockPos> queue = new ArrayDeque<>();
        rails.add(core);
        queue.add(core);
        int limit = 4 * maxOuter + 8;
        while (!queue.isEmpty()) {
            BlockPos p = queue.poll();
            for (Direction d : Direction.Plane.HORIZONTAL) {
                BlockPos n = p.relative(d);
                if (!rails.contains(n) && level.isLoaded(n) && level.getBlockState(n).getBlock() instanceof MinerRailBlock) {
                    if (rails.size() >= limit) {
                        return new MinerScan(Error.SIZE, null, new long[0], new long[0], false);
                    }
                    rails.add(n);
                    queue.add(n);
                }
            }
        }
        int minX = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE;
        int minZ = Integer.MAX_VALUE;
        int maxZ = Integer.MIN_VALUE;
        for (BlockPos p : rails) {
            minX = Math.min(minX, p.getX());
            maxX = Math.max(maxX, p.getX());
            minZ = Math.min(minZ, p.getZ());
            maxZ = Math.max(maxZ, p.getZ());
        }
        MinerFrame frame = new MinerFrame(y, minX, maxX, minZ, maxZ);
        // лишние: направляющие не по периметру ограничивающего прямоугольника
        for (BlockPos p : rails) {
            boolean onEdge = p.getX() == minX || p.getX() == maxX || p.getZ() == minZ || p.getZ() == maxZ;
            if (!onEdge) {
                return new MinerScan(Error.EXTRA, frame, new long[0], new long[]{p.asLong()}, false);
            }
        }
        // недостающие клетки периметра
        List<Long> missing = new ArrayList<>();
        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                boolean onEdge = x == minX || x == maxX || z == minZ || z == maxZ;
                if (onEdge && !rails.contains(new BlockPos(x, y, z)) && missing.size() < 4 * maxOuter) {
                    missing.add(new BlockPos(x, y, z).asLong());
                }
            }
        }
        if (!missing.isEmpty()) {
            return new MinerScan(Error.NOT_CLOSED, frame, toArray(missing), new long[0], false);
        }
        int w = maxX - minX + 1;
        int d = maxZ - minZ + 1;
        if (w < MIN_OUTER || d < MIN_OUTER || w > maxOuter || d > maxOuter) {
            return new MinerScan(Error.SIZE, frame, new long[0], new long[0], false);
        }
        boolean corner = (core.getX() == minX || core.getX() == maxX) && (core.getZ() == minZ || core.getZ() == maxZ);
        if (!corner) {
            return new MinerScan(Error.CORNER, frame, new long[0], new long[0], false);
        }
        BlockPos frontPos = core.relative(front);
        if (front.getAxis().isVertical() || frame.containsXZ(frontPos.getX(), frontPos.getZ())) {
            return new MinerScan(Error.FRONT, frame, new long[0], new long[0], false);
        }
        // область: внутри рамки на уровне направляющих и на блок выше
        List<Long> obstacles = new ArrayList<>();
        boolean unloaded = false;
        for (int x = minX + 1; x < maxX; x++) {
            for (int z = minZ + 1; z < maxZ; z++) {
                BlockPos p = new BlockPos(x, y, z);
                if (!level.isLoaded(p)) {
                    unloaded = true;
                    continue;
                }
                for (int dy = 0; dy <= 1; dy++) {
                    BlockPos q = p.above(dy);
                    if (!level.isOutsideBuildHeight(q) && !passable(level, q) && obstacles.size() < MAX_LISTED) {
                        obstacles.add(q.asLong());
                    }
                }
            }
        }
        if (!obstacles.isEmpty()) {
            return new MinerScan(Error.BLOCKED, frame, new long[0], toArray(obstacles), unloaded);
        }
        return new MinerScan(Error.NONE, frame, new long[0], new long[0], unloaded);
    }

    private static long[] toArray(List<Long> list) {
        long[] a = new long[list.size()];
        for (int i = 0; i < a.length; i++) {
            a[i] = list.get(i);
        }
        return a;
    }
}
