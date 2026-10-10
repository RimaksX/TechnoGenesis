package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.ConduitBlock;
import dev.technogenesis.kontur.network.ConduitMode;
import dev.technogenesis.kontur.network.PipeNetworkManager;
import dev.technogenesis.kontur.network.PipeTier;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/** Узел сети труб: хранит режим каждой стороны, регистрируется в сети при загрузке и покидает её при удалении. */
public class ConduitBlockEntity extends BlockEntity {
    private final ConduitMode[] modes = new ConduitMode[6];

    public ConduitBlockEntity(BlockPos pos, BlockState state) {
        super(KonturBlockEntities.PIPE.get(), pos, state);
        java.util.Arrays.fill(modes, ConduitMode.PUSH);
    }

    public PipeTier tier() {
        return getBlockState().getBlock() instanceof ConduitBlock pipe ? pipe.tier : PipeTier.ITEM_BASIC;
    }

    public ConduitMode mode(Direction dir) {
        return modes[dir.ordinal()];
    }

    public void setMode(Direction dir, ConduitMode mode) {
        modes[dir.ordinal()] = mode;
        setChanged();
        if (level != null) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
        }
    }

    @Override
    public void onLoad() {
        super.onLoad();
        if (level != null && !level.isClientSide) {
            PipeNetworkManager.add(level, worldPosition, tier());
        }
    }

    @Override
    public void setRemoved() {
        super.setRemoved();
        removeFromNetwork(level);
    }

    @Override
    public void onChunkUnloaded() {
        super.onChunkUnloaded();
        removeFromNetwork(level);
    }

    private void removeFromNetwork(@Nullable Level lvl) {
        if (lvl != null && !lvl.isClientSide) {
            PipeNetworkManager.remove(lvl, worldPosition, tier().kind);
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        int[] packed = new int[6];
        for (int i = 0; i < 6; i++) {
            packed[i] = modes[i].ordinal();
        }
        tag.putIntArray("modes", packed);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        int[] packed = tag.getIntArray("modes");
        for (int i = 0; i < 6; i++) {
            modes[i] = i < packed.length ? ConduitMode.byOrdinal(packed[i]) : ConduitMode.PUSH;
        }
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        return saveWithoutMetadata(registries);
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }
}
