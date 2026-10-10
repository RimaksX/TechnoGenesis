package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.ConduitBlock;
import dev.technogenesis.kontur.blockentity.ConduitBlockEntity;
import dev.technogenesis.kontur.network.ConduitMode;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.level.block.PipeBlock;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import dev.technogenesis.kontur.network.ConduitKind;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

/**
 * Рамка на торце трубы там, где она касается инвентаря или бака: синяя - труба отдаёт внутрь, оранжевая - забирает,
 * зелёная - и то и другое. Закрытая сторона видна серой рамкой, только пока в руке ключ. Рамка лежит на грани блока,
 * как рамки разъёмов машин.
 */
public final class ConduitPortRenderer implements BlockEntityRenderer<ConduitBlockEntity> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "textures/entity/port.png");
    private static final float LIFT = 0.002f;

    public ConduitPortRenderer(BlockEntityRendererProvider.Context context) {
    }

    /** Участки жидкости внутри стеклянной трубы: ядро и по проходу на каждую подключённую сторону. */
    private static final float[][] ARMS = {
            {6, 0, 6, 10, 5, 10}, {6, 11, 6, 10, 16, 10}, {6, 6, 0, 10, 10, 5},
            {6, 6, 11, 10, 10, 16}, {0, 6, 6, 5, 10, 10}, {11, 6, 6, 16, 10, 10}};

    private void drawFluid(ConduitBlockEntity be, PoseStack stack, MultiBufferSource buffers, int light) {
        Fluid fluid = be.displayFluid();
        if (fluid == Fluids.EMPTY || be.tier().kind != ConduitKind.FLUIDS) {
            return;
        }
        IClientFluidTypeExtensions ext = IClientFluidTypeExtensions.of(fluid);
        TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS)
                .apply(ext.getStillTexture());
        int tint = ext.getTintColor();
        VertexConsumer vc = buffers.getBuffer(RenderType.entityTranslucent(InventoryMenu.BLOCK_ATLAS));
        PoseStack.Pose pose = stack.last();
        box(vc, pose, sprite, tint, light, 5, 5, 5, 11, 11, 11);
        for (Direction dir : Direction.values()) {
            if (be.getBlockState().getValue(PipeBlock.PROPERTY_BY_DIRECTION.get(dir))) {
                float[] a = ARMS[dir.ordinal()];
                box(vc, pose, sprite, tint, light, a[0], a[1], a[2], a[3], a[4], a[5]);
            }
        }
    }

    /** Параллелепипед, оклеенный спрайтом жидкости; координаты в шестнадцатых долях блока. */
    private static void box(VertexConsumer vc, PoseStack.Pose pose, TextureAtlasSprite sp, int tint, int light,
                            float x0, float y0, float z0, float x1, float y1, float z1) {
        int r = (tint >> 16) & 255;
        int g = (tint >> 8) & 255;
        int b = tint & 255;
        int a = 215;
        // север и юг (x, y), запад и восток (z, y), низ и верх (x, z)
        face(vc, pose, sp, r, g, b, a, light, 0, 0, -1, x0, y0, z0, x1, y0, z0, x1, y1, z0, x0, y1, z0, x0, x1, y0, y1);
        face(vc, pose, sp, r, g, b, a, light, 0, 0, 1, x1, y0, z1, x0, y0, z1, x0, y1, z1, x1, y1, z1, x0, x1, y0, y1);
        face(vc, pose, sp, r, g, b, a, light, -1, 0, 0, x0, y0, z1, x0, y0, z0, x0, y1, z0, x0, y1, z1, z0, z1, y0, y1);
        face(vc, pose, sp, r, g, b, a, light, 1, 0, 0, x1, y0, z0, x1, y0, z1, x1, y1, z1, x1, y1, z0, z0, z1, y0, y1);
        face(vc, pose, sp, r, g, b, a, light, 0, -1, 0, x0, y0, z1, x1, y0, z1, x1, y0, z0, x0, y0, z0, x0, x1, z0, z1);
        face(vc, pose, sp, r, g, b, a, light, 0, 1, 0, x0, y1, z0, x1, y1, z0, x1, y1, z1, x0, y1, z1, x0, x1, z0, z1);
    }

    private static void face(VertexConsumer vc, PoseStack.Pose pose, TextureAtlasSprite sp, int r, int g, int b, int a,
                             int light, float nx, float ny, float nz,
                             float ax, float ay, float az, float bx, float by, float bz,
                             float cx, float cy, float cz, float dx, float dy, float dz,
                             float ua, float ub, float va, float vb) {
        float[] pts = {ax, ay, az, bx, by, bz, cx, cy, cz, dx, dy, dz};
        float[] us = {ua, ub, ub, ua};
        float[] vs = {vb, vb, va, va};
        for (int i = 0; i < 4; i++) {
            float u = sp.getU0() + (sp.getU1() - sp.getU0()) * (us[i] / 16f);
            float v = sp.getV0() + (sp.getV1() - sp.getV0()) * (vs[i] / 16f);
            vc.addVertex(pose, pts[i * 3] / 16f, pts[i * 3 + 1] / 16f, pts[i * 3 + 2] / 16f)
                    .setColor(r, g, b, a).setUv(u, v).setOverlay(OverlayTexture.NO_OVERLAY)
                    .setLight(light).setNormal(pose, nx, ny, nz);
        }
    }

    @Override
    public void render(ConduitBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                       int light, int overlay) {
        drawFluid(be, stack, buffers, light);
        boolean wrench = MachinePortRenderer.heldWrenchMode() != null;
        VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        PoseStack.Pose pose = stack.last();
        int lit = LightTexture.pack(Math.max(LightTexture.block(light), 9), LightTexture.sky(light));
        for (Direction dir : Direction.values()) {
            ConduitMode mode = be.mode(dir);
            boolean connected = be.getBlockState().getValue(PipeBlock.PROPERTY_BY_DIRECTION.get(dir));
            boolean toPipe = be.getLevel() != null
                    && be.getLevel().getBlockState(be.getBlockPos().relative(dir)).getBlock() instanceof ConduitBlock;
            if (toPipe || (!connected && !(wrench && mode == ConduitMode.OFF))) {
                continue;
            }
            MachinePortRenderer.ring(vc, pose, dir, 4f, 12f, 1f, mode.color, lit, -LIFT);
        }
    }
}
