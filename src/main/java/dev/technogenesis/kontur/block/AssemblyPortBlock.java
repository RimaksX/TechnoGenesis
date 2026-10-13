package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import dev.technogenesis.kontur.blockentity.AssemblyPortBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/** Порт корпуса собираемой машины: стоит в любом месте стенки, подключает трубы и кабели к контроллеру; остаётся видимым и после сборки. */
public class AssemblyPortBlock extends BaseEntityBlock {
    public static final MapCodec<AssemblyPortBlock> CODEC = simpleCodec(AssemblyPortBlock::new);

    public AssemblyPortBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(AssemblyCasingBlock.FORMED, false));
    }

    @Override
    protected void createBlockStateDefinition(net.minecraft.world.level.block.state.StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        builder.add(AssemblyCasingBlock.FORMED);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new AssemblyPortBlockEntity(pos, state);
    }
}
