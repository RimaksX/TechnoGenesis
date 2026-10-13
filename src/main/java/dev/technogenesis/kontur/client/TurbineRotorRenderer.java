package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.TurbineHallBlockEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

/** Ротор паротурбинного зала: вал с лопатками вдоль всего тоннеля, вращается, пока зал вырабатывает ток. */
public final class TurbineRotorRenderer {
    public static final ModelResourceLocation ROTOR = ModelResourceLocation.standalone(
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "block/turbine_rotor"));
    private static final int TUNNEL = 5;
    private static final float DEGREES_PER_TICK = 26f;

    private TurbineRotorRenderer() {
    }

    public static void render(TurbineHallBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                              int light, int overlay) {
        if (be.getLevel() == null) {
            return;
        }
        boolean spinning = be.getBlockState().getValue(MachineBlock.ACTIVE);
        Direction back = be.getBlockState().getValue(MachineBlock.FACING).getOpposite();
        float angle = spinning ? (be.getLevel().getGameTime() + partialTick) * DEGREES_PER_TICK : 0f;
        BakedModel model = Minecraft.getInstance().getModelManager().getModel(ROTOR);
        var vc = buffers.getBuffer(RenderType.cutout());
        float yaw = back.getAxis() == Direction.Axis.X ? 90f : 0f;
        for (int b = 1; b <= TUNNEL; b++) {
            stack.pushPose();
            stack.translate(0.5 + back.getStepX() * b, 0.5, 0.5 + back.getStepZ() * b);
            stack.mulPose(Axis.YP.rotationDegrees(yaw));
            stack.mulPose(Axis.ZP.rotationDegrees(angle + b * 9f));
            stack.translate(-0.5, -0.5, -0.5);
            Minecraft.getInstance().getBlockRenderer().getModelRenderer().renderModel(stack.last(), vc, null, model,
                    1f, 1f, 1f, LightTexture.pack(12, 12), OverlayTexture.NO_OVERLAY);
            stack.popPose();
        }
    }
}
