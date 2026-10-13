package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MultiLayout;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import org.jetbrains.annotations.Nullable;

/**
 * Крупная машина из нескольких блоков (до 3x2x2 и колонны в три блока). Все части - один блок со своим номером PART;
 * блок-сущность, тик и меню только у части 0, остальные пробрасывают к ней взаимодействие. Подключение труб и кабелей
 * идёт через одну назначенную клетку на каждой стороне (см. MultiLayout). Сломанная часть убирает всю машину.
 */
public class MultiMachineBlock extends MachineBlock {
    public static final IntegerProperty PART = IntegerProperty.create("part", 0, MultiLayout.MAX_PARTS - 1);

    public static final MapCodec<MultiMachineBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            propertiesCodec(),
            MachineKind.CODEC.fieldOf("machine").forGetter(b -> b.kind)
    ).apply(i, MultiMachineBlock::new));

    public final MultiLayout layout;

    public MultiMachineBlock(Properties properties, MachineKind kind) {
        super(properties, kind);
        this.layout = kind.layout();
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

    @Override
    public BlockPos masterPos(BlockState state, BlockPos pos) {
        return layout.masterOf(pos, state.getValue(FACING), state.getValue(PART));
    }

    public List<BlockPos> partPositions(BlockPos master, Direction facing) {
        return layout.cells(master, facing);
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

    /** Работающее состояние переносится на все части: свет и анимация одинаковы по всей машине. */
    public void setActive(Level level, BlockPos master, boolean active) {
        BlockState masterState = level.getBlockState(master);
        if (!masterState.is(this)) {
            return;
        }
        Direction facing = masterState.getValue(FACING);
        for (BlockPos p : layout.cells(master, facing)) {
            if (!level.isLoaded(p)) {
                continue;
            }
            BlockState st = level.getBlockState(p);
            if (st.is(this) && st.getValue(ACTIVE) != active) {
                level.setBlock(p, st.setValue(ACTIVE, active), 3);
            }
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moving) {
        if (!state.is(newState.getBlock())) {
            BlockPos master = masterPos(state, pos);
            for (BlockPos p : layout.cells(master, state.getValue(FACING))) {
                if (!p.equals(pos) && level.isLoaded(p) && level.getBlockState(p).is(this)) {
                    level.removeBlock(p, false);
                }
            }
        }
        super.onRemove(state, level, pos, newState, moving);
    }
}
