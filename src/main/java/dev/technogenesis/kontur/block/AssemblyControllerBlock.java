package dev.technogenesis.kontur.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.machine.AssemblyShape;
import dev.technogenesis.kontur.machine.MachineKind;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/** Контроллер собираемой игроком машины: при клике, если схема нарушена, подсказывает, где первая ошибка, и открывает меню. */
public class AssemblyControllerBlock extends MachineBlock {
    public static final MapCodec<AssemblyControllerBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            propertiesCodec(),
            MachineKind.CODEC.fieldOf("machine").forGetter(b -> b.kind)
    ).apply(i, AssemblyControllerBlock::new));

    public AssemblyControllerBlock(Properties properties, MachineKind kind) {
        super(properties, kind);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player,
                                               BlockHitResult hit) {
        if (!level.isClientSide) {
            AssemblyShape shape = kind.shape();
            AssemblyShape.Result r = shape.check(level, pos, state.getValue(FACING));
            if (!r.formed() && r.first() != null) {
                player.displayClientMessage(Component.translatable("message.kontur.assembly_problem", r.problems(),
                        r.first()[0], r.first()[1], r.first()[2]), true);
            }
        }
        return super.useWithoutItem(state, level, pos, player, hit);
    }
}
