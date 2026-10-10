package dev.technogenesis.kontur.miner;

import net.minecraft.world.phys.Vec3;

/**
 * Путь головки: прямые отрезки. Между ячейками слоя головка идёт напрямик, а к складу и обратно сначала поднимается к
 * плоскости рамки, едет по ней и только потом опускается (viaPlane). Одну и ту же математику использует сервер при
 * движении и клиент при отрисовке, поэтому анимация совпадает с настоящим положением.
 */
public final class MinerPath {
    private static final double EPS = 1e-4;

    private MinerPath() {
    }

    /** Точки пути от from до to, без самой from. */
    public static Vec3[] waypoints(Vec3 from, Vec3 to, boolean viaPlane, double planeY) {
        double dx = to.x - from.x;
        double dz = to.z - from.z;
        boolean horizontal = dx * dx + dz * dz > EPS * EPS;
        if (viaPlane && horizontal) {
            if (from.y < planeY - EPS) {
                return new Vec3[]{new Vec3(from.x, planeY, from.z), new Vec3(to.x, planeY, to.z), to};
            }
            return new Vec3[]{new Vec3(to.x, planeY, to.z), to};
        }
        return new Vec3[]{to};
    }

    /** Положение после того, как от from пройдено dist по ломаной. */
    public static Vec3 along(Vec3 from, Vec3[] points, double dist) {
        Vec3 pos = from;
        double left = dist;
        for (Vec3 p : points) {
            double len = pos.distanceTo(p);
            if (len <= EPS) {
                pos = p;
                continue;
            }
            if (left >= len) {
                left -= len;
                pos = p;
            } else {
                return pos.add(p.subtract(pos).scale(left / len));
            }
        }
        return pos;
    }
}
