package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * Солнечная ферма: многоблочная установка 3 в ширину и 2 в глубину. Все шесть частей - один и тот же блок со своим
 * номером PART (0..5, ряд * 3 + столбец); блок-сущность и тик есть только у части 0, остальные пробрасывают к ней
 * меню и энергию. Сломанная часть убирает всю ферму.
 */
public class SolarFarmBlock extends MachineBlock {
    public static final int PARTS = 6;
    public static final IntegerProperty PART = IntegerProperty.create("part", 0, PARTS - 1);

    public static final MapCodec<SolarFarmBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            propertiesCodec(),
            MachineKind.CODEC.fieldOf("machine").forGetter(b -> b.kind)
    ).apply(i, SolarFarmBlock::new));

    public SolarFarmBlock(Properties properties, MachineKind kind) {
        super(properties, kind);
        registerDefaultState(defaultBlockState().setValue(PART, 0));
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(PART);
    }

    /** Позиции всех шести частей фермы по позиции главной части и направлению. */
    public static List<BlockPos> partPositions(BlockPos master, BlockState state) {
        return partPositions(master, state.getValue(FACING));
    }

    public static List<BlockPos> partPositions(BlockPos master, Direction facing) {
        List<BlockPos> out = new ArrayList<>(PARTS);
        for (int r = 0; r < 2; r++) {
            for (int c = 0; c < 3; c++) {
                out.add(master.relative(facing.getClockWise(), c).relative(facing.getOpposite(), r));
            }
        }
        return out;
    }

    public static BlockPos masterOf(BlockPos pos, BlockState state) {
        int idx = state.getValue(PART);
        Direction facing = state.getValue(FACING);
        return pos.relative(facing.getCounterClockWise(), idx % 3).relative(facing, idx / 3);
    }

    private static VoxelShape stairs(int... tops) {
        VoxelShape shape = Shapes.empty();
        for (int i = 0; i < tops.length; i++) {
            shape = Shapes.or(shape, Block.box(0, 0, i * 4, 16, tops[i], i * 4 + 4));
        }
        return shape;
    }

    /** Форма совпадает с моделью: восемь одинаковых ступеней (шаг и толщина по 2, глубина по 4), шкаф управления на части 1. */
    private static final VoxelShape FRONT_SHAPE = stairs(2, 4, 6, 8);
    private static final VoxelShape BACK_SHAPE = stairs(10, 12, 14, 16);
    private static final VoxelShape CABINET_SHAPE = Shapes.or(FRONT_SHAPE, Block.box(4, 2, 0, 12, 6, 4));

    private static VoxelShape shapeOf(BlockState state) {
        int part = state.getValue(PART);
        return part == 1 ? CABINET_SHAPE : part < 3 ? FRONT_SHAPE : BACK_SHAPE;
    }

    /** Форма части для facing north; для других сторон поворачивается вокруг вертикали. */
    private static VoxelShape rotated(VoxelShape north, Direction facing) {
        int turns = switch (facing) {
            case EAST -> 1;
            case SOUTH -> 2;
            case WEST -> 3;
            default -> 0;
        };
        VoxelShape out = north;
        for (int i = 0; i < turns; i++) {
            VoxelShape[] acc = {Shapes.empty()};
            out.forAllBoxes((x0, y0, z0, x1, y1, z1) ->
                    acc[0] = Shapes.or(acc[0], Shapes.box(1 - z1, y0, x0, 1 - z0, y1, x1)));
            out = acc[0];
        }
        return out;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return rotated(shapeOf(state), state.getValue(FACING));
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return getShape(state, level, pos, context);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return state.getValue(PART) == 0 ? KonturBlockEntities.createMachine(kind, pos, state) : null;
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return state.getValue(PART) == 0 ? super.getTicker(level, state, type) : null;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player,
                                               BlockHitResult hit) {
        BlockPos master = masterOf(pos, state);
        if (!level.isClientSide && level.getBlockEntity(master) instanceof MachineBlockEntity be) {
            player.openMenu(be, buf -> {
                buf.writeEnum(kind);
                buf.writeBlockPos(master);
            });
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        if (!state.is(newState.getBlock())) {
            BlockPos master = masterOf(pos, state);
            for (BlockPos p : partPositions(master, state)) {
                if (!p.equals(pos) && level.getBlockState(p).is(this)) {
                    level.removeBlock(p, false);
                }
            }
        }
        super.onRemove(state, level, pos, newState, moving);
    }
}
