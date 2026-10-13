package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.technogenesis.kontur.block.AssemblyCasingBlock;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.item.WrenchItem;
import dev.technogenesis.kontur.machine.AssemblyShape;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Рисует собираемую игроком машину. Пока схема собирается и у игрока в руке ключ, видна призрачная проекция: голубые
 * кубы на пустых местах и красные на местах с чужими блоками. После щелчка ключом блоки схемы невидимы, а контроллер рисует
 * на их месте цельную готовую модель машины (клетки 16x16x16, повёрнутые по направлению контроллера).
 */
public final class AssemblyRenderer {
    private static final int GHOST_REFRESH = 10;

    private record Cache(long time, List<AssemblyShape.Gap> gaps) {
    }

    private static final Map<BlockPos, Cache> GHOSTS = new HashMap<>();

    private AssemblyRenderer() {
    }

    public static void render(MachineBlockEntity be, float partialTick, PoseStack stack, MultiBufferSource buffers) {
        if (be.getLevel() == null) {
            return;
        }
        BlockState state = be.getBlockState();
        AssemblyShape shape = be.kind().shape();
        Direction facing = state.getValue(MachineBlock.FACING);
        if (state.getValue(AssemblyCasingBlock.FORMED)) {
            renderFormed(be, shape, facing, state.getValue(MachineBlock.ACTIVE), stack, buffers);
        } else if (holdsWrench(Minecraft.getInstance().player)) {
            renderGhosts(be, shape, facing, stack, buffers);
        }
    }

    private static boolean holdsWrench(Player player) {
        return player != null && (player.getMainHandItem().getItem() instanceof WrenchItem
                || player.getOffhandItem().getItem() instanceof WrenchItem);
    }

    private static void renderFormed(MachineBlockEntity be, AssemblyShape shape, Direction facing, boolean on,
                                     PoseStack stack, MultiBufferSource buffers) {
        float yRot = switch (facing) {
            case EAST -> 90f;
            case SOUTH -> 180f;
            case WEST -> 270f;
            default -> 0f;
        };
        int lit = LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().relative(facing));
        VertexConsumer vc = buffers.getBuffer(RenderType.translucent());
        var renderer = Minecraft.getInstance().getBlockRenderer().getModelRenderer();
        stack.pushPose();
        stack.translate(0.5, 0.0, 0.5);
        stack.mulPose(com.mojang.math.Axis.YP.rotationDegrees(-yRot));
        stack.translate(-0.5, 0.0, -0.5);
        for (AssemblyModels.Part part : AssemblyModels.parts(shape.id)) {
            BakedModel model = Minecraft.getInstance().getModelManager().getModel(on ? part.on() : part.off());
            stack.pushPose();
            stack.translate(part.c() - shape.halfWidth, part.y() - shape.below, part.r());
            renderer.renderModel(stack.last(), vc, null, model, 1f, 1f, 1f, lit, OverlayTexture.NO_OVERLAY);
            stack.popPose();
        }
        stack.popPose();
    }

    private static void renderGhosts(MachineBlockEntity be, AssemblyShape shape, Direction facing, PoseStack stack,
                                     MultiBufferSource buffers) {
        long now = be.getLevel().getGameTime();
        BlockPos origin = be.getBlockPos();
        Cache cache = GHOSTS.get(origin);
        if (cache == null || now - cache.time() >= GHOST_REFRESH) {
            cache = new Cache(now, shape.gaps(be.getLevel(), origin, facing));
            GHOSTS.put(origin, cache);
        }
        VertexConsumer vc = buffers.getBuffer(RenderType.translucent());
        var renderer = Minecraft.getInstance().getBlockRenderer().getModelRenderer();
        BakedModel missing = Minecraft.getInstance().getModelManager().getModel(AssemblyModels.GHOST);
        BakedModel wrong = Minecraft.getInstance().getModelManager().getModel(AssemblyModels.GHOST_WRONG);
        BakedModel portGhost = Minecraft.getInstance().getModelManager().getModel(AssemblyModels.GHOST_PORT);
        for (AssemblyShape.Gap gap : cache.gaps()) {
            stack.pushPose();
            stack.translate(gap.pos().getX() - origin.getX(), gap.pos().getY() - origin.getY(), gap.pos().getZ() - origin.getZ());
            renderer.renderModel(stack.last(), vc, null, gap.wrong() ? wrong : gap.port() ? portGhost : missing, 1f, 1f, 1f,
                    LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY);
            stack.popPose();
        }
    }
}
