package dev.technogenesis.kontur.block;

import dev.technogenesis.kontur.machine.MachineKind;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * Направляющая шахтёра: балка в верхней части блока (высота 8..16), которая тянется к соседним направляющим и к ядру.
 * Из направляющих собирается замкнутый прямоугольник на одном уровне; сама головка по ним ездит как модель и блоков не занимает.
 */
public class MinerRailBlock extends Block {
    public static final BooleanProperty NORTH = BlockStateProperties.NORTH;
    public static final BooleanProperty EAST = BlockStateProperties.EAST;
    public static final BooleanProperty SOUTH = BlockStateProperties.SOUTH;
    public static final BooleanProperty WEST = BlockStateProperties.WEST;

    private static final VoxelShape CORE = Block.box(4, 8, 4, 12, 16, 12);
    private static final VoxelShape ARM_N = Block.box(4, 8, 0, 12, 16, 4);
    private static final VoxelShape ARM_S = Block.box(4, 8, 12, 12, 16, 16);
    private static final VoxelShape ARM_W = Block.box(0, 8, 4, 4, 16, 12);
    private static final VoxelShape ARM_E = Block.box(12, 8, 4, 16, 16, 12);

    public MinerRailBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(NORTH, false).setValue(EAST, false)
                .setValue(SOUTH, false).setValue(WEST, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(NORTH, EAST, SOUTH, WEST);
    }

    private static BooleanProperty property(Direction dir) {
        return switch (dir) {
            case NORTH -> NORTH;
            case EAST -> EAST;
            case SOUTH -> SOUTH;
            default -> WEST;
        };
    }

    /** К направляющей и к ядру шахтёра балка тянется, ко всему остальному - нет. */
    private static boolean connects(BlockState neighbour) {
        return neighbour.getBlock() instanceof MinerRailBlock
                || neighbour.getBlock() instanceof MachineBlock machine && machine.kind == MachineKind.MINER;
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = defaultBlockState();
        for (Direction dir : Direction.Plane.HORIZONTAL) {
            state = state.setValue(property(dir), connects(context.getLevel().getBlockState(context.getClickedPos().relative(dir))));
        }
        return state;
    }

    @Override
    protected BlockState updateShape(BlockState state, Direction dir, BlockState neighbour, LevelAccessor level,
                                     BlockPos pos, BlockPos neighbourPos) {
        if (dir.getAxis().isHorizontal()) {
            return state.setValue(property(dir), connects(neighbour));
        }
        return state;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        VoxelShape shape = CORE;
        if (state.getValue(NORTH)) {
            shape = Shapes.or(shape, ARM_N);
        }
        if (state.getValue(SOUTH)) {
            shape = Shapes.or(shape, ARM_S);
        }
        if (state.getValue(WEST)) {
            shape = Shapes.or(shape, ARM_W);
        }
        if (state.getValue(EAST)) {
            shape = Shapes.or(shape, ARM_E);
        }
        return shape;
    }
}
