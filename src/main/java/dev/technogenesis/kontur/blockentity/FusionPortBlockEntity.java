package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.energy.IEnergyStorage;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import org.jetbrains.annotations.Nullable;

/** Порт корпуса реактора: пробрасывает баки и энергию контроллера, если реактор собран. Адрес контроллера запоминает при проверке схемы. */
public class FusionPortBlockEntity extends BlockEntity {
    @Nullable
    private BlockPos controller;

    public FusionPortBlockEntity(BlockPos pos, BlockState state) {
        super(KonturBlockEntities.FUSION_PORT.get(), pos, state);
    }

    public void setController(BlockPos pos) {
        if (!pos.equals(controller)) {
            controller = pos;
            setChanged();
        }
    }

    @Nullable
    private FusionReactorBlockEntity reactor() {
        if (level == null || controller == null || !level.isLoaded(controller)) {
            return null;
        }
        return level.getBlockEntity(controller) instanceof FusionReactorBlockEntity r && r.isFormed() ? r : null;
    }

    @Nullable
    public IFluidHandler fluidHandler() {
        FusionReactorBlockEntity r = reactor();
        return r == null ? null : r.getFluidHandler(null);
    }

    @Nullable
    public IEnergyStorage energyStorage() {
        FusionReactorBlockEntity r = reactor();
        return r == null ? null : r.getEnergyStorage(null);
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        if (controller != null) {
            tag.putLong("controller", controller.asLong());
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        controller = tag.contains("controller") ? BlockPos.of(tag.getLong("controller")) : null;
    }
}
