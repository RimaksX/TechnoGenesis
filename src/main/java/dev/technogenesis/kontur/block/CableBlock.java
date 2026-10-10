package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.network.CableNetworkManager;
import dev.technogenesis.kontur.network.CableTier;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.PipeBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.capabilities.Capabilities;
import org.jetbrains.annotations.Nullable;

/** Кабель: соединяется с другими кабелями и с любыми блоками, умеющими принимать или отдавать FE. */
public class CableBlock extends BaseEntityBlock {
    public static final MapCodec<CableBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            propertiesCodec(),
            StringRepresentable.fromEnum(CableTier::values).fieldOf("tier").forGetter(b -> b.tier)
    ).apply(i, CableBlock::new));

    private static final VoxelShape CORE = Block.box(5, 5, 5, 11, 11, 11);
    /** Порядок как у Direction.values(): DOWN, UP, NORTH, SOUTH, WEST, EAST. */
    private static final VoxelShape[] ARMS = {
            Block.box(6, 0, 6, 10, 5, 10), Block.box(6, 11, 6, 10, 16, 10),
            Block.box(6, 6, 0, 10, 10, 5), Block.box(6, 6, 11, 10, 10, 16),
            Block.box(0, 6, 6, 5, 10, 10), Block.box(11, 6, 6, 16, 10, 10)};

    public final CableTier tier;

    public CableBlock(Properties properties, CableTier tier) {
        super(properties);
        this.tier = tier;
        BlockState state = stateDefinition.any();
        for (BooleanProperty p : PipeBlock.PROPERTY_BY_DIRECTION.values()) {
            state = state.setValue(p, false);
        }
        registerDefaultState(state);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(PipeBlock.NORTH, PipeBlock.EAST, PipeBlock.SOUTH, PipeBlock.WEST, PipeBlock.UP, PipeBlock.DOWN);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        VoxelShape shape = CORE;
        for (Direction d : Direction.values()) {
            if (state.getValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d))) {
                shape = Shapes.or(shape, ARMS[d.ordinal()]);
            }
        }
        return shape;
    }

    private BlockState withConnections(Level level, BlockPos pos, BlockState state) {
        for (Direction d : Direction.values()) {
            state = state.setValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d), canConnect(level, pos, d));
        }
        return state;
    }

    private static boolean canConnect(Level level, BlockPos pos, Direction dir) {
        BlockPos np = pos.relative(dir);
        if (level.getBlockState(np).getBlock() instanceof CableBlock) {
            return true;
        }
        return level.getCapability(Capabilities.EnergyStorage.BLOCK, np, dir.getOpposite()) != null;
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return withConnections(context.getLevel(), context.getClickedPos(), defaultBlockState());
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block block, BlockPos fromPos,
                                   boolean moving) {
        super.neighborChanged(state, level, pos, block, fromPos, moving);
        if (!level.isClientSide) {
            BlockState updated = withConnections(level, pos, state);
            if (updated != state) {
                level.setBlock(pos, updated, 3);
            }
            CableNetworkManager.markDirty(level, pos);
        }
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return KonturBlockEntities.CABLE.get().create(pos, state);
    }
}
