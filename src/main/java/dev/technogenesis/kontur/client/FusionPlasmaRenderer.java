package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.FusionReactorBlockEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

/**
 * Плазма в камере работающего термоядерного реактора: пульсирующее ядро и шесть сгустков, обращающихся вокруг него.
 * Светится в полную силу независимо от освещения, сама модель - полупрозрачный куб с анимированной текстурой плазмы.
 */
public final class FusionPlasmaRenderer {
    public static final ModelResourceLocation PLASMA = ModelResourceLocation.standalone(
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "block/fusion_plasma"));
    private static final int ORBITERS = 6;

    private FusionPlasmaRenderer() {
    }

    public static void render(FusionReactorBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                              int light, int overlay) {
        if (be.getLevel() == null || !be.getBlockState().getValue(MachineBlock.ACTIVE)) {
            return;
        }
        Direction back = be.getBlockState().getValue(MachineBlock.FACING).getOpposite();
        float t = be.getLevel().getGameTime() + partialTick;
        BakedModel model = Minecraft.getInstance().getModelManager().getModel(PLASMA);
        VertexConsumer vc = buffers.getBuffer(RenderType.translucent());
        float cx = 0.5f + back.getStepX() * 2f;      // середина камеры: две клетки вглубь, на стыке нижнего и верхнего ряда
        float cz = 0.5f + back.getStepZ() * 2f;
        float cy = 1.0f;
        float pulse = 0.85f + 0.12f * (float) Math.sin(t * 0.25f);
        blob(stack, vc, model, cx, cy, cz, pulse, t * 5f);
        for (int i = 0; i < ORBITERS; i++) {
            double angle = t * 0.11 + i * Math.PI * 2 / ORBITERS;
            float ox = (float) (Math.cos(angle) * 1.15);
            float oz = (float) (Math.sin(angle) * 1.15);
            float oy = (float) (Math.sin(t * 0.07 + i * 1.7) * 0.3);
            blob(stack, vc, model, cx + ox, cy + oy, cz + oz, 0.24f, (float) Math.toDegrees(angle) * 2f);
        }
    }

    private static void blob(PoseStack stack, VertexConsumer vc, BakedModel model, float x, float y, float z, float size,
                             float degrees) {
        stack.pushPose();
        stack.translate(x, y, z);
        stack.mulPose(Axis.YP.rotationDegrees(degrees));
        stack.mulPose(Axis.XP.rotationDegrees(degrees * 0.5f));
        stack.scale(size, size, size);
        stack.translate(-0.5, -0.5, -0.5);
        Minecraft.getInstance().getBlockRenderer().getModelRenderer().renderModel(stack.last(), vc, null, model,
                1f, 1f, 1f, LightTexture.FULL_BRIGHT, net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY);
        stack.popPose();
    }
}
