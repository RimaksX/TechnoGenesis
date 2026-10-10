package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.ConduitBlock;
import dev.technogenesis.kontur.blockentity.ConduitBlockEntity;
import dev.technogenesis.kontur.network.ConduitMode;
import net.minecraft.client.renderer.LightTexture;
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

    @Override
    public void render(ConduitBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers,
                       int light, int overlay) {
        boolean wrench = MachinePortRenderer.heldWrenchMode() != null;
        VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        PoseStack.Pose pose = stack.last();
        int lit = LightTexture.pack(Math.max(LightTexture.block(light), 9), LightTexture.sky(light));
        for (Direction dir : Direction.values()) {
            ConduitMode mode = be.mode(dir);
            boolean connected = be.getBlockState().getValue(net.minecraft.world.level.block.PipeBlock.PROPERTY_BY_DIRECTION.get(dir));
            boolean toPipe = be.getLevel() != null
                    && be.getLevel().getBlockState(be.getBlockPos().relative(dir)).getBlock() instanceof ConduitBlock;
            if (toPipe || (!connected && !(wrench && mode == ConduitMode.OFF))) {
                continue;
            }
            MachinePortRenderer.ring(vc, pose, dir, 4f, 12f, 1f, mode.color, lit, -LIFT);
        }
    }
}
