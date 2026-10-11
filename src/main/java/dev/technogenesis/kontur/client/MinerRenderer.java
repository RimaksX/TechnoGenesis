package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.blockentity.MinerBlockEntity;
import dev.technogenesis.kontur.item.WrenchItem;
import dev.technogenesis.kontur.miner.MinerFrame;
import dev.technogenesis.kontur.miner.MinerScan;
import dev.technogenesis.kontur.registry.KonturBlocks;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.ModelBlockRenderer;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Отрисовка шахтёра: балка по рамке, каретка, телескопический вал и головка с вращающимся буром (всё это модели, блоков
 * они не занимают), а также голограммы-подсказки: контур области, недостающие клетки рамки, мешающие блоки и место склада
 * наконечников. Подсказки видны, пока игрок держит ядро, направляющую или ключ.
 */
public final class MinerRenderer {
    private static ModelResourceLocation model(String name) {
        return ModelResourceLocation.standalone(ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "block/" + name));
    }

    public static final ModelResourceLocation BEAM = model("miner_beam");
    public static final ModelResourceLocation TRUCK = model("miner_truck");
    public static final ModelResourceLocation CARRIAGE = model("miner_carriage");
    public static final ModelResourceLocation SHAFT = model("miner_shaft");
    public static final ModelResourceLocation HEAD = model("miner_head");
    public static final ModelResourceLocation[] TIPS = {model("miner_tip_iron"), model("miner_tip_steel"),
            model("miner_tip_carbide")};

    private static final float SPIN_PER_TICK = 28f;
    /** Высота низа балки над полом блока рамки: балка лежит на верхней грани направляющей (12/16 блока). */
    private static final double BEAM_LIFT = 0.75;

    private MinerRenderer() {
    }

    /** Все модели деталей: регистрируются при загрузке ресурсов. */
    public static List<ModelResourceLocation> models() {
        List<ModelResourceLocation> list = new ArrayList<>(List.of(BEAM, TRUCK, CARRIAGE, SHAFT, HEAD));
        list.addAll(List.of(TIPS));
        return list;
    }

    public static void render(MinerBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                              int light, int overlay) {
        Level level = be.getLevel();
        if (level == null) {
            return;
        }
        renderHologram(be, stack, buffers);
        MinerScan scan = be.viewScan();
        if (!be.viewVerified() || scan == null || scan.frame == null || scan.error != MinerScan.Error.NONE) {
            return;                      // каретка рисуется только после проверки ключом
        }
        MinerFrame f = scan.frame;
        BlockPos core = be.getBlockPos();
        Vec3 head = be.viewHead(partialTick);
        ModelBlockRenderer renderer = Minecraft.getInstance().getBlockRenderer().getModelRenderer();
        VertexConsumer vc = buffers.getBuffer(RenderType.cutout());

        double beamY = f.y() + BEAM_LIFT - core.getY();
        double beamZ = head.z - 0.5 - core.getZ();
        for (int x = f.minX(); x <= f.maxX(); x++) {
            part(renderer, vc, stack, level, BEAM, x - core.getX(), beamY, beamZ, core, overlay);
        }
        // тележки: модель нарисована так, что верх рельса приходится на высоту 4 пикселя
        part(renderer, vc, stack, level, TRUCK, f.minX() - core.getX(), beamY - 0.25, beamZ, core, overlay);
        part(renderer, vc, stack, level, TRUCK, f.maxX() - core.getX(), beamY - 0.25, beamZ, core, overlay);

        double headX = head.x - 0.5 - core.getX();
        double headZ = head.z - 0.5 - core.getZ();
        part(renderer, vc, stack, level, CARRIAGE, headX, f.y() + BEAM_LIFT - 1.0 - core.getY(), headZ, core, overlay);

        // вал: целые блоки сверху вниз, последний обрезается по высоте до верха головки
        double top = f.y() + MinerBlockEntity.CARRIAGE_BOTTOM;
        double bottom = head.y + MinerBlockEntity.HEAD_H;
        BakedModel shaft = Minecraft.getInstance().getModelManager().getModel(SHAFT);
        for (double yy = top - 1.0; yy + 1.0 > bottom + 1e-6; yy -= 1.0) {
            double segBottom = Math.max(yy, bottom);
            double frac = yy + 1.0 - segBottom;
            if (frac < 0.01) {
                continue;
            }
            stack.pushPose();
            stack.translate(headX, segBottom - core.getY(), headZ);
            stack.scale(1f, (float) frac, 1f);
            renderer.renderModel(stack.last(), vc, null, shaft, 1f, 1f, 1f, lightAt(level, head.x, segBottom, head.z), overlay);
            stack.popPose();
        }

        // головка и бур; бур вращается, пока идёт ломка
        double headY = head.y - core.getY();
        part(renderer, vc, stack, level, HEAD, headX, headY, headZ, core, overlay);
        int tier = be.viewTip();
        if (tier >= 1 && tier <= TIPS.length) {
            float now = level.getGameTime() + partialTick;
            float dt = now - be.lastRenderTick;
            if (dt < 0 || dt > 20) {
                dt = 0;
            }
            be.lastRenderTick = now;
            if (be.viewMining()) {
                be.drillAngle = (be.drillAngle + dt * SPIN_PER_TICK) % 360f;
            }
            stack.pushPose();
            stack.translate(headX + 0.5, headY, headZ + 0.5);
            stack.mulPose(Axis.YP.rotationDegrees(be.drillAngle));
            stack.translate(-0.5, 0, -0.5);
            renderer.renderModel(stack.last(), vc, null, Minecraft.getInstance().getModelManager().getModel(TIPS[tier - 1]),
                    1f, 1f, 1f, lightAt(level, head.x, head.y, head.z), overlay);
            stack.popPose();
        }
    }

    private static int lightAt(Level level, double x, double y, double z) {
        return LevelRenderer.getLightColor(level, BlockPos.containing(x, y + 0.5, z));
    }

    private static void part(ModelBlockRenderer renderer, VertexConsumer vc, PoseStack stack, Level level,
                             ModelResourceLocation id, double rx, double ry, double rz, BlockPos core, int overlay) {
        stack.pushPose();
        stack.translate(rx, ry, rz);
        BakedModel model = Minecraft.getInstance().getModelManager().getModel(id);
        BlockPos at = BlockPos.containing(core.getX() + rx + 0.5, core.getY() + ry + 0.5, core.getZ() + rz + 0.5);
        renderer.renderModel(stack.last(), vc, null, model, 1f, 1f, 1f, LevelRenderer.getLightColor(level, at), overlay);
        stack.popPose();
    }

    // ------------------------------------------------------------------ голограммы

    private static boolean holdingBuildItem() {
        Player player = Minecraft.getInstance().player;
        if (player == null) {
            return false;
        }
        for (ItemStack held : new ItemStack[]{player.getMainHandItem(), player.getOffhandItem()}) {
            Item item = held.getItem();
            if (item == KonturBlocks.MINER.get().asItem() || item == KonturBlocks.MINER_RAIL.get().asItem()
                    || item instanceof WrenchItem) {
                return true;
            }
        }
        return false;
    }

    private static void box(PoseStack stack, VertexConsumer vc, BlockPos core, double x0, double y0, double z0,
                            double x1, double y1, double z1, float r, float g, float b, float a) {
        LevelRenderer.renderLineBox(stack, vc, x0 - core.getX(), y0 - core.getY(), z0 - core.getZ(),
                x1 - core.getX(), y1 - core.getY(), z1 - core.getZ(), r, g, b, a);
    }

    private static void cell(PoseStack stack, VertexConsumer vc, BlockPos core, BlockPos p, double grow,
                             float r, float g, float b, float a) {
        box(stack, vc, core, p.getX() - grow, p.getY() - grow, p.getZ() - grow,
                p.getX() + 1 + grow, p.getY() + 1 + grow, p.getZ() + 1 + grow, r, g, b, a);
    }

    private static void renderHologram(MinerBlockEntity be, PoseStack stack, MultiBufferSource buffers) {
        if (!holdingBuildItem()) {
            return;
        }
        BlockPos core = be.getBlockPos();
        VertexConsumer vc = buffers.getBuffer(RenderType.lines());
        MinerScan scan = be.viewScan();
        MinerFrame f = scan == null ? null : scan.frame;
        boolean onlyCore = f == null || f.maxX() - f.minX() <= 0 && f.maxZ() - f.minZ() <= 0;
        Direction front = be.getBlockState().getValue(dev.technogenesis.kontur.block.MachineBlock.FACING);

        if (onlyCore) {
            // подсказка: примерный контур 7x7 от ядра назад и вбок; настоящий размер задают сами направляющие
            Direction a = front.getOpposite();
            Direction b = front.getClockWise();
            int x1 = core.getX() + a.getStepX() * 6 + b.getStepX() * 6;
            int z1 = core.getZ() + a.getStepZ() * 6 + b.getStepZ() * 6;
            box(stack, vc, core, Math.min(core.getX(), x1), core.getY(), Math.min(core.getZ(), z1),
                    Math.max(core.getX(), x1) + 1, core.getY() + 1, Math.max(core.getZ(), z1) + 1, 0.4f, 0.75f, 1f, 0.45f);
        } else {
            boolean ok = scan.error == MinerScan.Error.NONE;
            float r = ok ? 0.3f : 1f;
            float g = ok ? 1f : 0.65f;
            float bl = ok ? 0.6f : 0.2f;
            box(stack, vc, core, f.minX(), f.y(), f.minZ(), f.maxX() + 1, f.y() + 1, f.maxZ() + 1, r, g, bl, 0.9f);
            if (f.innerWidth() > 0 && f.innerDepth() > 0) {
                // коридор головки: плоскость рамки и блок над ней
                box(stack, vc, core, f.minX() + 1, f.y(), f.minZ() + 1, f.maxX(), f.y() + 2, f.maxZ(), 0.45f, 0.8f, 1f, 0.4f);
            }
            for (long packed : scan.missing) {
                cell(stack, vc, core, BlockPos.of(packed), -0.08, 0.4f, 0.6f, 1f, 0.9f);
            }
            for (long packed : scan.obstacles) {
                cell(stack, vc, core, BlockPos.of(packed), 0.02, 1f, 0.2f, 0.2f, 1f);
            }
        }
        // склад наконечников: сундук вплотную к лицевой грани ядра
        if (!be.viewDepot()) {
            BlockPos depot = core.relative(front);
            cell(stack, vc, core, depot, -0.02, 1f, 0.75f, 0.2f, 0.95f);
            box(stack, vc, core, depot.getX() + 0.0625, depot.getY(), depot.getZ() + 0.0625,
                    depot.getX() + 0.9375, depot.getY() + 0.875, depot.getZ() + 0.9375, 1f, 0.75f, 0.2f, 0.7f);
            box(stack, vc, core, depot.getX() + 0.0625, depot.getY() + 0.625, depot.getZ() + 0.0625,
                    depot.getX() + 0.9375, depot.getY() + 0.6875, depot.getZ() + 0.9375, 1f, 0.75f, 0.2f, 0.7f);
        }
    }
}
