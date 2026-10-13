package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.machine.IoMode;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.machine.MultiLayout;
import dev.technogenesis.kontur.machine.RelativeSide;
import dev.technogenesis.kontur.item.WrenchItem;
import dev.technogenesis.kontur.machine.TransferType;
import dev.technogenesis.kontur.machine.WrenchMode;
import net.minecraft.client.Minecraft;
import net.minecraft.world.item.ItemStack;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

/**
 * Подсветка разъёмов машины по настройке сторон: рамка гнезда приглушённо-синяя (вход), тёплая (выход) или зеленоватая
 * (и то, и другое). Закрытое гнездо без ключа не видно, а с ключом в руке показывается серой рамкой; с ключом в режиме одного типа цвет рамки показывает только этот тип.
 * Гнёзда лежат на гранях блока (стороны 0/16, центр 5..11), поэтому провода подходят к ним вплотную.
 */
public final class MachinePortRenderer implements BlockEntityRenderer<MachineBlockEntity> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "textures/entity/port.png");
    private static final float LIFT = 0.002f;
    // приглушённые тона на основе цвета керамики: вход - сероватый синий, выход - светлый тёплый, оба - зеленоватый
    public static final int INPUT = 0x949EB3;
    public static final int OUTPUT = 0xCAA37D;
    public static final int BOTH = 0x94B593;
    public static final int CLOSED = 0x96928C;   // закрытое гнездо видно только с ключом в руке

    public MachinePortRenderer(BlockEntityRendererProvider.Context context) {
    }

    /** Шахтёр рисует балку и головку по всей рамке, поэтому область отсечения у него шире блока. */
    @Override
    public net.minecraft.world.phys.AABB getRenderBoundingBox(MachineBlockEntity be) {
        if (be instanceof dev.technogenesis.kontur.blockentity.MinerBlockEntity miner) {
            return miner.renderArea();
        }
        if (be instanceof dev.technogenesis.kontur.blockentity.FusionReactorBlockEntity
                || be instanceof dev.technogenesis.kontur.blockentity.TurbineHallBlockEntity) {
            return new net.minecraft.world.phys.AABB(be.getBlockPos()).inflate(8);      // камера и ротор за пределами блока
        }
        if (be.kind().layout() != null) {
            var cells = be.footprint();
            var far = cells.get(cells.size() - 1);
            return new net.minecraft.world.phys.AABB(be.getBlockPos()).minmax(new net.minecraft.world.phys.AABB(far));
        }
        return new net.minecraft.world.phys.AABB(be.getBlockPos());
    }

    /** Балка и головка шахтёра видны, даже когда сам блок ядра вне кадра (иначе деталь пропадает, стоит отвернуться от ядра). */
    @Override
    public boolean shouldRenderOffScreen(MachineBlockEntity be) {
        return be instanceof dev.technogenesis.kontur.blockentity.MinerBlockEntity;
    }

    @Override
    public boolean shouldRender(MachineBlockEntity be, net.minecraft.world.phys.Vec3 camera) {
        double range = be instanceof dev.technogenesis.kontur.blockentity.MinerBlockEntity ? 160.0 : getViewDistance();
        return net.minecraft.world.phys.Vec3.atCenterOf(be.getBlockPos()).closerThan(camera, range);
    }

    @Override
    public void render(MachineBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                       int light, int overlay) {
        if (be.kind() == dev.technogenesis.kontur.machine.MachineKind.SOLAR_FARM) {
            return;
        }
        if (be instanceof dev.technogenesis.kontur.blockentity.MinerBlockEntity miner) {
            MinerRenderer.render(miner, partialTick, stack, buffers, light, overlay);
        }
        if (be instanceof dev.technogenesis.kontur.blockentity.TurbineHallBlockEntity turbine) {
            TurbineRotorRenderer.render(turbine, partialTick, stack, buffers, light, overlay);
        }
        if (be instanceof dev.technogenesis.kontur.blockentity.FusionReactorBlockEntity fusion) {
            FusionPlasmaRenderer.render(fusion, partialTick, stack, buffers, light, overlay);
        }
        if (be instanceof dev.technogenesis.kontur.blockentity.WindRotorBlockEntity rotor) {
            WindBladesRenderer.render(rotor, partialTick, stack, buffers, light, overlay);
        }
        Direction facing = be.getBlockState().getValue(MachineBlock.FACING);
        VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        int lit = LightTexture.pack(Math.max(LightTexture.block(light), 9), LightTexture.sky(light));
        WrenchMode wrench = heldWrenchMode();
        MultiLayout layout = be.kind().layout();
        for (Direction dir : Direction.values()) {
            RelativeSide rs = RelativeSide.of(facing, dir);
            // у крупной машины гнёзда и индикатор лежат на гранях своих клеток: сдвигаем рисование к нужной
            if (rs == RelativeSide.FRONT) {
                stack.pushPose();
                moveToCell(stack, be, layout, facing, layout == null ? 0 : layout.lightIndex());
                frontLight(vc, stack.last(), dir, be.status(), lit);
                stack.popPose();
            }
            stack.pushPose();
            moveToCell(stack, be, layout, facing, layout == null ? 0 : Math.max(0, layout.portIndex(rs)));
            drawPort(be, vc, stack.last(), dir, rs, wrench, lit);
            stack.popPose();
        }
    }

    private static void moveToCell(PoseStack stack, MachineBlockEntity be, MultiLayout layout, Direction facing, int idx) {
        if (layout != null) {
            var cell = layout.cell(be.getBlockPos(), facing, idx);
            stack.translate(cell.getX() - be.getBlockPos().getX(), cell.getY() - be.getBlockPos().getY(),
                    cell.getZ() - be.getBlockPos().getZ());
        }
    }

    private static void drawPort(MachineBlockEntity be, VertexConsumer vc, PoseStack.Pose pose, Direction dir,
                                 RelativeSide rs, WrenchMode wrench, int lit) {
        if (!be.kind().hasPort(rs)) {
            return;
        }
        boolean in = false;
        boolean out = false;
        for (TransferType t : TransferType.values()) {
            if (!be.supports(t)) {
                continue;
            }
            IoMode m = be.sides.get(t, rs);
            if (wrench != null && wrench.type != null && wrench.type != t) {
                continue;   // цвет рамки только по выбранному на ключе типу
            }
            in |= m.canInput();
            out |= m.canOutput();
        }
        if (!in && !out && wrench == null) {
            return;
        }
        int color = in && out ? BOTH : in ? INPUT : out ? OUTPUT : CLOSED;
        bevelRing(vc, pose, dir, 5f, 11f, color, lit, LIFT);
    }

    /** Световой индикатор состояния на передней грани: зелёный - работает, красный - неполадка, жёлтый - полный или заряжается. */
    private static void frontLight(VertexConsumer vc, PoseStack.Pose pose, Direction dir, MachineStatus status, int light) {
        int color = status == MachineStatus.RUNNING ? 0x46C864 : status.problem ? 0xEB463C
                : status == MachineStatus.IDLE ? 0x4A5060 : 0xF0B432;
        rect(vc, pose, dir, 5f, 14f, 11f, 15f, color, LightTexture.pack(15, 15), LIFT);
    }

    /** Режим ключа, если игрок держит его в любой руке; иначе null. */
    static WrenchMode heldWrenchMode() {
        var player = Minecraft.getInstance().player;
        if (player == null) {
            return null;
        }
        for (ItemStack held : new ItemStack[]{player.getMainHandItem(), player.getOffhandItem()}) {
            if (held.getItem() instanceof WrenchItem) {
                return WrenchItem.mode(held);
            }
        }
        return null;
    }

    /** Рамка в 1 пиксель с фаской: верх и лево светлее, низ и право темнее. */
    static void bevelRing(VertexConsumer vc, PoseStack.Pose pose, Direction dir, float lo, float hi, int color,
                          int light, float lift) {
        int lighter = shade(color, 1.10f);
        int darker = shade(color, 0.84f);
        rect(vc, pose, dir, lo, lo, hi, lo + 1f, darker, light, lift);
        rect(vc, pose, dir, lo, hi - 1f, hi, hi, lighter, light, lift);
        rect(vc, pose, dir, lo, lo + 1f, lo + 1f, hi - 1f, lighter, light, lift);
        rect(vc, pose, dir, hi - 1f, lo + 1f, hi, hi - 1f, darker, light, lift);
    }

    public static int shade(int color, float k) {
        int r = Math.min(255, Math.round(((color >> 16) & 255) * k));
        int g = Math.min(255, Math.round(((color >> 8) & 255) * k));
        int b = Math.min(255, Math.round((color & 255) * k));
        return (r << 16) | (g << 8) | b;
    }

    static void ring(VertexConsumer vc, PoseStack.Pose pose, Direction dir, float lo, float hi, float t,
                             int color, int light, float lift) {
        rect(vc, pose, dir, lo, lo, hi, lo + t, color, light, lift);
        rect(vc, pose, dir, lo, hi - t, hi, hi, color, light, lift);
        rect(vc, pose, dir, lo, lo + t, lo + t, hi - t, color, light, lift);
        rect(vc, pose, dir, hi - t, lo + t, hi, hi - t, color, light, lift);
    }

    /** Прямоугольник на грани блока; a/b - координаты вдоль касательных осей грани в единицах 1/16. */
    static void rect(VertexConsumer vc, PoseStack.Pose pose, Direction dir, float a0, float b0, float a1,
                             float b1, int color, int light, float lift) {
        float[][] p = new float[4][3];
        float[] ua = {a0, a1, a1, a0};
        float[] vb = {b0, b0, b1, b1};
        for (int i = 0; i < 4; i++) {
            float a = ua[i] / 16f;
            float b = vb[i] / 16f;
            switch (dir) {
                case EAST -> p[i] = new float[]{1f + lift, b, a};
                case WEST -> p[i] = new float[]{-lift, b, a};
                case SOUTH -> p[i] = new float[]{a, b, 1f + lift};
                case NORTH -> p[i] = new float[]{a, b, -lift};
                case UP -> p[i] = new float[]{a, 1f + lift, b};
                default -> p[i] = new float[]{a, -lift, b};
            }
        }
        int r = (color >> 16) & 255;
        int g = (color >> 8) & 255;
        int bl = color & 255;
        float nx = dir.getStepX();
        float ny = dir.getStepY();
        float nz = dir.getStepZ();
        for (int i = 0; i < 4; i++) {
            vc.addVertex(pose, p[i][0], p[i][1], p[i][2]).setColor(r, g, bl, 255).setUv(0.5f, 0.5f)
                    .setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(pose, nx, ny, nz);
        }
    }
}
