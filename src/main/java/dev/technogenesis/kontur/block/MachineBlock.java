package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.FluidUtil;
import org.jetbrains.annotations.Nullable;

/** Блок машины Контура: направление, признак работы (для анимации передней грани) и уровень заряда. */
public class MachineBlock extends BaseEntityBlock {
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");
    public static final IntegerProperty CHARGE = IntegerProperty.create("charge", 0, 5);

    public static final MapCodec<MachineBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            propertiesCodec(),
            MachineKind.CODEC.fieldOf("machine").forGetter(b -> b.kind)
    ).apply(i, MachineBlock::new));

    public final MachineKind kind;

    public MachineBlock(Properties properties, MachineKind kind) {
        super(properties);
        this.kind = kind;
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH)
                .setValue(ACTIVE, false).setValue(CHARGE, 0));
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        builder.add(FACING, ACTIVE, CHARGE);
    }

    /** Позиция блока с блок-сущностью: у крупных машин главная часть, у остальных сама позиция. */
    public BlockPos masterPos(BlockState state, BlockPos pos) {
        return pos;
    }

    /** Блок-сущность машины в позиции (для частей крупной машины - главной части) или null. */
    @Nullable
    public static MachineBlockEntity resolve(net.minecraft.world.level.BlockGetter level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (state.getBlock() instanceof MachineBlock block) {
            return level.getBlockEntity(block.masterPos(state, pos)) instanceof MachineBlockEntity be ? be : null;
        }
        return null;
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return KonturBlockEntities.createMachine(kind, pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        if (level.isClientSide) {
            return null;
        }
        return createTickerHelper(type, KonturBlockEntities.MACHINES.get(kind).get(),
                (lvl, pos, st, be) -> be.serverTick());
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                              Player player, InteractionHand hand, BlockHitResult hit) {
        // ключ настраивает стороны (работает WrenchItem.useOn), меню при этом не открывается
        if (stack.getItem() instanceof dev.technogenesis.kontur.item.WrenchItem) {
            return ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;
        }
        // ведро/бак с жидкостью: наполнить или слить машину прямо кликом
        if (kind.definition.hasFluids() && !stack.isEmpty() && stack.getCapability(Capabilities.FluidHandler.ITEM) != null) {
            if (!level.isClientSide) {
                MachineBlockEntity be = resolve(level, pos);
                if (be != null) {
                    FluidUtil.interactWithFluidHandler(player, hand, be.playerFluidHandler());
                }
            }
            return ItemInteractionResult.sidedSuccess(level.isClientSide);
        }
        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player,
                                               BlockHitResult hit) {
        BlockPos master = masterPos(state, pos);
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
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof MachineBlockEntity be) {
            be.dropContents();
        }
        super.onRemove(state, level, pos, newState, moving);
    }
}
