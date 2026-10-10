package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.machine.IoMode;
import dev.technogenesis.kontur.machine.MachineStatus;
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
 * Подсветка разъёмов машины по настройке сторон: рамка гнезда синяя (вход), оранжевая (выход) или зелёная (и то, и
 * другое); внутри - метки включённых типов (предметы, жидкости, энергия). Закрытое гнездо без ключа не видно, а с
 * ключом в руке показывается серой рамкой; с ключом в режиме одного типа цвет рамки показывает только этот тип.
 * Гнёзда лежат на гранях блока (стороны 0/16, центр 5..11), поэтому провода подходят к ним вплотную.
 */
public final class MachinePortRenderer implements BlockEntityRenderer<MachineBlockEntity> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "textures/entity/port.png");
    private static final float LIFT = 0.002f;
    private static final int INPUT = 0x3C6EE6;
    private static final int OUTPUT = 0xEB8C28;
    private static final int BOTH = 0x46C864;
    private static final int CLOSED = 0x6E6E78;   // закрытое гнездо видно только с ключом в руке
    private static final int[] PIPS = {0xD2D2D8, 0x4696E6, 0xEB463C};   // предметы, жидкости, энергия

    public MachinePortRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(MachineBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                       int light, int overlay) {
        Direction facing = be.getBlockState().getValue(MachineBlock.FACING);
        VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        PoseStack.Pose pose = stack.last();
        int lit = LightTexture.pack(Math.max(LightTexture.block(light), 9), LightTexture.sky(light));
        boolean[] has = {be.kind().definition.hasItems(), be.kind().definition.hasFluids(),
                be.kind().definition.energyCapacity > 0};
        WrenchMode wrench = heldWrenchMode();
        for (Direction dir : Direction.values()) {
            RelativeSide rs = RelativeSide.of(facing, dir);
            if (rs == RelativeSide.FRONT) {
                frontLight(vc, pose, dir, be.status(), lit);
                continue;
            }
            boolean in = false;
            boolean out = false;
            boolean[] on = new boolean[3];
            for (TransferType t : TransferType.values()) {
                if (!has[t.ordinal()]) {
                    continue;
                }
                IoMode m = be.sides.get(t, rs);
                on[t.ordinal()] = m != IoMode.NONE;
                if (wrench != null && wrench.type != null && wrench.type != t) {
                    continue;   // цвет рамки только по выбранному на ключе типу
                }
                in |= m.canInput();
                out |= m.canOutput();
            }
            if (!in && !out && wrench == null) {
                continue;
            }
            int color = in && out ? BOTH : in ? INPUT : out ? OUTPUT : CLOSED;
            // рамка гнезда (1 пиксель = 1 кубик) и метки включённых типов в центре
            ring(vc, pose, dir, 5f, 11f, 1f, color, lit, LIFT);
            int count = 0;
            for (boolean b : on) {
                count += b ? 1 : 0;
            }
            float x = count == 3 ? 6f : 7f;
            for (int i = 0; i < 3; i++) {
                if (on[i]) {
                    rect(vc, pose, dir, x, 7f, x + 1f, 8f, PIPS[i], lit, LIFT * 2);
                    x += 1f;
                }
            }
        }
    }

    /** Световой индикатор состояния на передней грани: зелёный - работает, красный - неполадка, жёлтый - полный или заряжается. */
    private static void frontLight(VertexConsumer vc, PoseStack.Pose pose, Direction dir, MachineStatus status, int light) {
        int color = status == MachineStatus.RUNNING ? 0x46C864 : status.problem ? 0xEB463C
                : status == MachineStatus.IDLE ? 0x4A5060 : 0xF0B432;
        rect(vc, pose, dir, 5f, 13f, 11f, 14f, color, LightTexture.pack(15, 15), LIFT);
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
