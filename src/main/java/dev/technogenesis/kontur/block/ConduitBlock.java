package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.blockentity.ConduitBlockEntity;
import dev.technogenesis.kontur.network.ConduitKind;
import dev.technogenesis.kontur.network.ConduitMode;
import dev.technogenesis.kontur.network.PipeNetworkManager;
import dev.technogenesis.kontur.network.PipeTier;
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

/**
 * Труба предметов или жидкостей. Соединяется с трубами того же вида и с блоками, у которых есть соответствующий
 * инвентарь или бак на этой грани. Режим каждой стороны (отдавать, забирать, оба, выключено) хранит блок-сущность и
 * меняется ключом.
 */
public class ConduitBlock extends BaseEntityBlock {
    public static final MapCodec<ConduitBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            propertiesCodec(),
            StringRepresentable.fromEnum(PipeTier::values).fieldOf("tier").forGetter(b -> b.tier)
    ).apply(i, ConduitBlock::new));

    private static final VoxelShape CORE = Block.box(4, 4, 4, 12, 12, 12);
    /** Порядок как у Direction.values(): DOWN, UP, NORTH, SOUTH, WEST, EAST. */
    private static final VoxelShape[] ARMS = {
            Block.box(5, 0, 5, 11, 4, 11), Block.box(5, 12, 5, 11, 16, 11),
            Block.box(5, 5, 0, 11, 11, 4), Block.box(5, 5, 12, 11, 11, 16),
            Block.box(0, 5, 5, 4, 11, 11), Block.box(12, 5, 5, 16, 11, 11)};

    public final PipeTier tier;

    public ConduitBlock(Properties properties, PipeTier tier) {
        super(properties);
        this.tier = tier;
        BlockState state = stateDefinition.any();
        for (BooleanProperty p : PipeBlock.PROPERTY_BY_DIRECTION.values()) {
            state = state.setValue(p, false);
        }
        registerDefaultState(state);
    }

    public ConduitKind kind() {
        return tier.kind;
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

    /** Есть ли на грани то, с чем труба умеет работать (инвентарь или бак). */
    private boolean hasHandler(Level level, BlockPos neighbour, Direction dir) {
        return switch (tier.kind) {
            case ITEMS -> level.getCapability(Capabilities.ItemHandler.BLOCK, neighbour, dir.getOpposite()) != null;
            case FLUIDS -> level.getCapability(Capabilities.FluidHandler.BLOCK, neighbour, dir.getOpposite()) != null;
        };
    }

    private boolean canConnect(Level level, BlockPos pos, Direction dir) {
        BlockPos np = pos.relative(dir);
        if (level.getBlockState(np).getBlock() instanceof ConduitBlock other) {
            return other.tier.kind == tier.kind;
        }
        ConduitMode mode = level.getBlockEntity(pos) instanceof ConduitBlockEntity be ? be.mode(dir) : ConduitMode.AUTO;
        return mode != ConduitMode.OFF && hasHandler(level, np, dir);
    }

    /** Пересчитывает соединения по соседям и режимам сторон. */
    public BlockState withConnections(Level level, BlockPos pos, BlockState state) {
        for (Direction d : Direction.values()) {
            state = state.setValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d), canConnect(level, pos, d));
        }
        return state;
    }

    /** Ключ: следующий (или предыдущий) режим стороны. Возвращает новый режим или null, если там не к чему подключаться. */
    @Nullable
    public ConduitMode cycleSide(Level level, BlockPos pos, Direction dir, boolean reverse) {
        if (!(level.getBlockEntity(pos) instanceof ConduitBlockEntity be)
                || level.getBlockState(pos.relative(dir)).getBlock() instanceof ConduitBlock) {
            return null;
        }
        ConduitMode current = be.mode(dir);
        if (current != ConduitMode.OFF || hasHandler(level, pos.relative(dir), dir)) {
            be.setMode(dir, reverse ? current.prev() : current.next());
        } else {
            return null;
        }
        BlockState state = level.getBlockState(pos);
        BlockState updated = withConnections(level, pos, state);
        if (updated != state) {
            level.setBlock(pos, updated, 3);
        }
        PipeNetworkManager.markDirty(level, pos);
        return be.mode(dir);
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
            PipeNetworkManager.markDirty(level, pos);
        }
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return KonturBlockEntities.PIPE.get().create(pos, state);
    }
}
