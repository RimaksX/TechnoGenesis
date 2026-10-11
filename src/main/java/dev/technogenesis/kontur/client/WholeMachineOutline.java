package dev.technogenesis.kontur.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.block.MultiMachineBlock;
import dev.technogenesis.kontur.block.SolarFarmBlock;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RenderHighlightEvent;

/**
 * При наведении на любую часть крупной машины (и солнечной фермы) рисуется одна рамка вокруг всей машины, а не
 * отдельного блока: форма всех частей склеивается, внутренние рёбра между ними пропадают.
 */
@EventBusSubscriber(modid = Kontur.MODID, value = Dist.CLIENT)
public final class WholeMachineOutline {
    private WholeMachineOutline() {
    }

    @SubscribeEvent
    public static void onHighlight(RenderHighlightEvent.Block event) {
        Level level = Minecraft.getInstance().level;
        if (level == null) {
            return;
        }
        BlockPos pos = event.getTarget().getBlockPos();
        BlockState state = level.getBlockState(pos);
        BlockPos master;
        List<BlockPos> cells;
        if (state.getBlock() instanceof MultiMachineBlock multi) {
            master = multi.masterPos(state, pos);
            cells = multi.partPositions(master, state.getValue(MachineBlock.FACING));
        } else if (state.getBlock() instanceof SolarFarmBlock) {
            master = SolarFarmBlock.masterOf(pos, state);
            cells = SolarFarmBlock.partPositions(master, state);
        } else {
            return;
        }
        VoxelShape shape = Shapes.empty();
        for (BlockPos p : cells) {
            BlockState part = level.getBlockState(p);
            if (part.is(state.getBlock())) {
                shape = Shapes.or(shape, part.getShape(level, p)
                        .move(p.getX() - master.getX(), p.getY() - master.getY(), p.getZ() - master.getZ()));
            }
        }
        Vec3 cam = event.getCamera().getPosition();
        double ox = master.getX() - cam.x;
        double oy = master.getY() - cam.y;
        double oz = master.getZ() - cam.z;
        VertexConsumer vc = event.getMultiBufferSource().getBuffer(RenderType.lines());
        PoseStack.Pose pose = event.getPoseStack().last();
        shape.forAllEdges((x0, y0, z0, x1, y1, z1) -> {
            float dx = (float) (x1 - x0);
            float dy = (float) (y1 - y0);
            float dz = (float) (z1 - z0);
            float len = Mth.sqrt(dx * dx + dy * dy + dz * dz);
            dx /= len;
            dy /= len;
            dz /= len;
            vc.addVertex(pose, (float) (x0 + ox), (float) (y0 + oy), (float) (z0 + oz))
                    .setColor(0f, 0f, 0f, 0.4f).setNormal(pose, dx, dy, dz);
            vc.addVertex(pose, (float) (x1 + ox), (float) (y1 + oy), (float) (z1 + oz))
                    .setColor(0f, 0f, 0f, 0.4f).setNormal(pose, dx, dy, dz);
        });
        event.setCanceled(true);
    }
}
