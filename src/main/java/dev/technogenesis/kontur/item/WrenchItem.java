package dev.technogenesis.kontur.item;

import dev.technogenesis.kontur.block.CableBlock;
import dev.technogenesis.kontur.block.ConduitBlock;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.network.CableNetwork;
import dev.technogenesis.kontur.network.CableNetworkManager;
import dev.technogenesis.kontur.network.ConduitMode;
import dev.technogenesis.kontur.network.PipeNetwork;
import dev.technogenesis.kontur.network.PipeNetworkManager;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.blockentity.MinerBlockEntity;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.miner.MinerScan;
import dev.technogenesis.kontur.machine.IoMode;
import dev.technogenesis.kontur.machine.RelativeSide;
import dev.technogenesis.kontur.machine.WrenchMode;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * Ключ для настройки сторон машин. Правый клик по грани переключает режим гнезда (вход, выход, вход и выход, закрыто),
 * с Shift - в обратную сторону; рамка гнезда на модели меняет цвет. Shift + правый клик в воздухе (не глядя на блок) меняет режим ключа:
 * все типы сразу, только предметы, жидкости, энергия или авто-вывод.
 */
public class WrenchItem extends Item {
    private static final String TAG_MODE = "wrench_mode";

    public WrenchItem(Properties properties) {
        super(properties.stacksTo(1));
    }

    public static WrenchMode mode(ItemStack stack) {
        CustomData data = stack.get(DataComponents.CUSTOM_DATA);
        return data == null ? WrenchMode.ALL : WrenchMode.byOrdinal(data.copyTag().getInt(TAG_MODE));
    }

    private static void setMode(ItemStack stack, WrenchMode mode) {
        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> tag.putInt(TAG_MODE, mode.ordinal()));
    }

    /** Цвет режима ключа: совпадает с цветами типов на моделях (предметы, жидкости, энергия). */
    private static int modeColor(WrenchMode mode) {
        return switch (mode) {
            case ALL -> 0xF5C542;
            case ITEMS -> 0xD2D2D8;
            case OUT1 -> 0xE8C46A;
            case OUT2 -> 0xE09A5A;
            case OUT3 -> 0xD07A6A;
            case FLUIDS -> 0x4696E6;
            case ENERGY -> 0xEB463C;
            case EJECT -> 0x46C864;
        };
    }

    /** Цвет режима стороны: синий - вход, оранжевый - выход, зелёный - оба, серый - закрыто. */
    private static int ioColor(IoMode mode) {
        return switch (mode) {
            case NONE -> 0x9A9AA4;
            case INPUT -> 0x5C9AFF;
            case OUTPUT -> 0xFFA533;
            case ALL -> 0x59D973;
        };
    }

    public static MutableComponent modeName(WrenchMode mode) {
        return Component.translatable("wrench.kontur.mode." + mode.key)
                .withStyle(s -> s.withColor(modeColor(mode)).withBold(true));
    }

    /** Что именно переключено: для общего режима пусто, для отдельных каналов - их название. */
    private static Component modeTitle(WrenchMode mode) {
        return mode.type == null ? Component.empty() : Component.literal("[").append(modeName(mode)).append("] ");
    }

    private static MutableComponent colored(String key, int color, Object... args) {
        return Component.translatable(key, args).withStyle(s -> s.withColor(color));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        // режим меняется только Shift + ПКМ в воздухе: клик рядом с блоком (мимо тонкой трубы или кабеля) или по
        // постороннему блоку режим не трогает
        if (!player.isShiftKeyDown()
                || player.pick(player.blockInteractionRange(), 0f, false).getType() == net.minecraft.world.phys.HitResult.Type.BLOCK) {
            return InteractionResultHolder.pass(stack);
        }
        WrenchMode next = mode(stack).next();
        if (!level.isClientSide) {
            setMode(stack, next);
        }
        player.displayClientMessage(Component.translatable("wrench.kontur.mode_set")
                .withStyle(ChatFormatting.GRAY).append(" ").append(modeName(next)), true);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        Level level = ctx.getLevel();
        Player player = ctx.getPlayer();
        BlockPos pos = ctx.getClickedPos();
        Block block = level.getBlockState(pos).getBlock();
        if (!(block instanceof MachineBlock) && !(block instanceof ConduitBlock) && !(block instanceof CableBlock)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide || player == null) {
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        if (block instanceof CableBlock) {
            describeCableNetwork(level, pos, player);
            return InteractionResult.CONSUME;
        }
        if (block instanceof ConduitBlock pipe) {
            configurePipe(pipe, level, pos, ctx, player);
            return InteractionResult.CONSUME;
        }
        MachineBlockEntity be = MachineBlock.resolve(level, pos);
        if (be == null) {
            return InteractionResult.PASS;
        }
        if (be instanceof dev.technogenesis.kontur.blockentity.AssemblyController assembled) {
            assemble(be, assembled, player);       // у собираемых машин ключ собирает и разбирает, а не настраивает стороны
            return InteractionResult.CONSUME;
        }
        if (be instanceof MinerBlockEntity miner && !miner.isVerified()) {
            reportMinerCheck(miner, player);          // пока постройка не проверена, ключ только проверяет
            return InteractionResult.CONSUME;
        }
        WrenchMode mode = mode(ctx.getItemInHand());
        if (mode == WrenchMode.EJECT) {
            boolean on = be.toggleEject();
            player.displayClientMessage(colored(on ? "wrench.kontur.eject_on" : "wrench.kontur.eject_off",
                    on ? 0x59D973 : 0x9A9AA4), true);
            return InteractionResult.CONSUME;
        }
        RelativeSide side = RelativeSide.of(be.getBlockState().getValue(MachineBlock.FACING), ctx.getClickedFace());
        if (!be.kind().hasPort(side)) {
            player.displayClientMessage(Component.translatable("gui.kontur.no_port").withStyle(ChatFormatting.GRAY), true);
            return InteractionResult.CONSUME;
        }
        IoMode result = be.cycleSide(mode, side, player.isShiftKeyDown());
        if (result == null) {
            player.displayClientMessage(Component.translatable("wrench.kontur.unsupported", modeName(mode))
                    .withStyle(ChatFormatting.RED), true);
        } else {
            player.displayClientMessage(Component.translatable("wrench.kontur.side_set",
                    Component.translatable("gui.kontur.side." + side.key).withStyle(ChatFormatting.GRAY),
                    modeTitle(mode), colored("gui.kontur.mode." + result.key, ioColor(result))), true);
        }
        return InteractionResult.CONSUME;
    }

    /** Ключ по контроллеру: замкнуть собранную схему (машина принимает готовый вид), Shift - разобрать обратно. */
    private static void assemble(MachineBlockEntity be, dev.technogenesis.kontur.blockentity.AssemblyController assembled,
                                 Player player) {
        net.minecraft.world.level.Level level = be.getLevel();
        BlockPos pos = be.getBlockPos();
        net.minecraft.core.Direction facing = be.getBlockState().getValue(MachineBlock.FACING);
        var tracker = assembled.tracker();
        if (tracker.formed()) {
            if (player.isShiftKeyDown()) {
                tracker.setFormed(level, pos, facing, false);
                player.displayClientMessage(Component.translatable("wrench.kontur.assembly_off").withStyle(ChatFormatting.GOLD), true);
            } else {
                player.displayClientMessage(Component.translatable("wrench.kontur.assembly_is").withStyle(ChatFormatting.GRAY), true);
            }
            return;
        }
        if (tracker.tryForm(level, pos, facing)) {
            level.playSound(null, pos, net.minecraft.sounds.SoundEvents.ANVIL_USE, net.minecraft.sounds.SoundSource.BLOCKS, 0.6f, 1.2f);
            player.displayClientMessage(Component.translatable("wrench.kontur.assembly_on").withStyle(ChatFormatting.GREEN), true);
        } else {
            var r = be.kind().shape().check(level, pos, facing);
            if (r.first() != null) {
                player.displayClientMessage(Component.translatable("message.kontur.assembly_problem", r.problems(),
                        r.first()[0], r.first()[1], r.first()[2]).withStyle(ChatFormatting.RED), true);
            }
        }
    }

    private static void reportMinerCheck(MinerBlockEntity miner, Player player) {
        MachineStatus bad = miner.check();
        if (bad == null) {
            player.sendSystemMessage(Component.translatable("wrench.kontur.miner_ok").withStyle(ChatFormatting.GREEN));
            return;
        }
        player.sendSystemMessage(Component.translatable("wrench.kontur.miner_fail", bad.text())
                .withStyle(ChatFormatting.RED));
        MinerScan scan = miner.lastScan();
        if (scan != null && scan.missing.length > 0) {
            player.sendSystemMessage(Component.translatable("wrench.kontur.miner_missing", scan.missing.length)
                    .withStyle(ChatFormatting.AQUA));
        }
        if (scan != null && scan.obstacles.length > 0) {
            player.sendSystemMessage(Component.translatable("wrench.kontur.miner_obstacles", scan.obstacles.length)
                    .withStyle(ChatFormatting.GOLD));
        }
        player.sendSystemMessage(Component.translatable("wrench.kontur.miner_again").withStyle(ChatFormatting.GRAY));
    }

    /** Сторона трубы под курсором: по самой далёкой от центра оси точки клика. */
    private static Direction pipeSide(UseOnContext ctx) {
        Vec3 rel = ctx.getClickLocation().subtract(Vec3.atCenterOf(ctx.getClickedPos()));
        double ax = Math.abs(rel.x);
        double ay = Math.abs(rel.y);
        double az = Math.abs(rel.z);
        if (ax >= ay && ax >= az) {
            return rel.x > 0 ? Direction.EAST : Direction.WEST;
        }
        if (ay >= az) {
            return rel.y > 0 ? Direction.UP : Direction.DOWN;
        }
        return rel.z > 0 ? Direction.SOUTH : Direction.NORTH;
    }

    private void configurePipe(ConduitBlock pipe, Level level, BlockPos pos, UseOnContext ctx, Player player) {
        Direction dir = pipeSide(ctx);
        ConduitMode result = pipe.cycleSide(level, pos, dir, player.isShiftKeyDown());
        if (result == null) {
            PipeNetwork.Info info = PipeNetworkManager.info(level, pos);
            if (info != null) {
                player.sendSystemMessage(Component.translatable("wrench.kontur.pipe_network",
                        info.pipes(), info.weakest() == null ? 0 : info.weakest().amount,
                        info.weakest() == null ? 0 : info.weakest().interval, info.sources(), info.sinks(), info.moved())
                        .withStyle(ChatFormatting.AQUA));
            }
            return;
        }
        player.displayClientMessage(Component.translatable("wrench.kontur.pipe_side",
                Component.translatable("wrench.kontur.dir." + dir.getName()).withStyle(ChatFormatting.GRAY),
                colored("wrench.kontur.pipe." + result.key, result.color)), true);
    }

    private static void describeCableNetwork(Level level, BlockPos pos, Player player) {
        CableNetwork.Info info = CableNetworkManager.info(level, pos);
        if (info == null || info.weakest() == null) {
            return;
        }
        player.sendSystemMessage(Component.translatable("wrench.kontur.cable_network", info.cables(),
                Component.translatable("block.kontur." + info.weakest().id), info.weakest().throughput,
                info.sources(), info.sinks(), info.storages(), info.moved()).withStyle(ChatFormatting.AQUA));
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("wrench.kontur.current", modeName(mode(stack))).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("wrench.kontur.hint_side").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("wrench.kontur.hint_shift").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("wrench.kontur.hint_air").withStyle(ChatFormatting.GRAY));
    }
}
