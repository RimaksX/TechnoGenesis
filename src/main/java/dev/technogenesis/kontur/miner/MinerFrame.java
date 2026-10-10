package dev.technogenesis.kontur.miner;

/** Рамка шахтёра: уровень направляющих и границы по рёбрам (координаты самих направляющих). */
public record MinerFrame(int y, int minX, int maxX, int minZ, int maxZ) {
    public int innerWidth() {
        return maxX - minX - 1;
    }

    public int innerDepth() {
        return maxZ - minZ - 1;
    }

    public int cells() {
        return Math.max(0, innerWidth()) * Math.max(0, innerDepth());
    }

    public boolean containsXZ(int x, int z) {
        return x >= minX && x <= maxX && z >= minZ && z <= maxZ;
    }

    public int[] toArray() {
        return new int[]{y, minX, maxX, minZ, maxZ};
    }

    public static MinerFrame fromArray(int[] a) {
        return a.length >= 5 ? new MinerFrame(a[0], a[1], a[2], a[3], a[4]) : null;
    }
}
