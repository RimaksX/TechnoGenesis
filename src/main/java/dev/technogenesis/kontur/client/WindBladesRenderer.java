package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.WindRotorBlockEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

/**
 * Лопасти ветрового ротора: отдельная модель, которая каждый кадр поворачивается вокруг оси ступицы. Скорость растёт
 * с мощностью ветра; угол копится по реальному времени, поэтому смена скорости не даёт скачков.
 */
public final class WindBladesRenderer {
    public static final ModelResourceLocation BLADES = ModelResourceLocation.standalone(
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "block/wind_rotor_blades"));
    private static final float DEGREES_PER_TICK_PER_POWER = 0.06f;

    private WindBladesRenderer() {
    }

    public static void render(WindRotorBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                              int light, int overlay) {
        if (be.getLevel() == null) {
            return;
        }
        float now = be.getLevel().getGameTime() + partialTick;
        float dt = now - be.lastRenderTick;
        if (dt < 0 || dt > 20) {
            dt = 0;
        }
        be.lastRenderTick = now;
        be.bladeAngle = (be.bladeAngle + dt * be.spin() * DEGREES_PER_TICK_PER_POWER) % 360f;

        // сам блок не пропускает свет, поэтому берём освещённость над ним
        int lit = net.minecraft.client.renderer.LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().above());
        BakedModel model = Minecraft.getInstance().getModelManager().getModel(BLADES);
        Direction facing = be.getBlockState().getValue(MachineBlock.FACING);
        float yRot = switch (facing) {
            case EAST -> 90f;
            case SOUTH -> 180f;
            case WEST -> 270f;
            default -> 0f;
        };
        stack.pushPose();
        stack.translate(0.5, 0.5, 0.5);
        stack.mulPose(Axis.YP.rotationDegrees(-yRot));
        stack.translate(-0.5, -0.5, -0.5);
        stack.translate(0.5, 0.5, 0.0);
        stack.mulPose(Axis.ZP.rotationDegrees(be.bladeAngle));
        stack.translate(-0.5, -0.5, 0.0);
        Minecraft.getInstance().getBlockRenderer().getModelRenderer().renderModel(stack.last(),
                buffers.getBuffer(RenderType.cutout()), null, model, 1f, 1f, 1f, lit, overlay);
        stack.popPose();
    }
}
