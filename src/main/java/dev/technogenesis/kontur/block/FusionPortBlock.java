package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import dev.technogenesis.kontur.blockentity.FusionPortBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/** Порт корпуса термоядерного реактора: стоит в любом месте стенки, подключает трубы и кабели к контроллеру. */
public class FusionPortBlock extends BaseEntityBlock {
    public static final MapCodec<FusionPortBlock> CODEC = simpleCodec(FusionPortBlock::new);

    public FusionPortBlock(Properties properties) {
        super(properties);
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
        return new FusionPortBlockEntity(pos, state);
    }
}
