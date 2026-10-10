package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.CableBlock;
import dev.technogenesis.kontur.network.CableNetworkManager;
import dev.technogenesis.kontur.network.CableTier;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Узел кабельной сети: регистрируется в сети при загрузке и покидает её при удалении/выгрузке. */
public class CableBlockEntity extends BlockEntity {
    public CableBlockEntity(BlockPos pos, BlockState state) {
        super(KonturBlockEntities.CABLE.get(), pos, state);
    }

    private CableTier tier() {
        return getBlockState().getBlock() instanceof CableBlock cable ? cable.tier : CableTier.COPPER;
    }

    @Override
    public void onLoad() {
        super.onLoad();
        if (level != null && !level.isClientSide) {
            CableNetworkManager.add(level, worldPosition, tier());
        }
    }

    @Override
    public void setRemoved() {
        super.setRemoved();
        if (level != null && !level.isClientSide) {
            CableNetworkManager.remove(level, worldPosition);
        }
    }

    @Override
    public void onChunkUnloaded() {
        super.onChunkUnloaded();
        if (level != null && !level.isClientSide) {
            CableNetworkManager.remove(level, worldPosition);
        }
    }
}
