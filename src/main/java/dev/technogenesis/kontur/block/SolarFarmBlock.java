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
import net.minecraft.world.level.Level;
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
