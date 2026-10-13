package dev.technogenesis.kontur.block;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;

/**
 * Корпусной блок собираемой машины (корпус, ротор). Пока машина не собрана, виден как обычный кубик; когда игрок
 * щёлкнул ключом по контроллеру и схема цела, блок становится невидимым, а вместо груды кубиков контроллер рисует цельную
 * готовую модель машины.
 */
public class AssemblyCasingBlock extends Block {
    public static final BooleanProperty FORMED = BooleanProperty.create("formed");

    public AssemblyCasingBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FORMED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FORMED);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return state.getValue(FORMED) ? RenderShape.INVISIBLE : RenderShape.MODEL;
    }
}
