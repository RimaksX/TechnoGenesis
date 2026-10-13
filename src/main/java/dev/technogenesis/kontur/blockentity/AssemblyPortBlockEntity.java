package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.energy.IEnergyStorage;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.items.IItemHandler;
import org.jetbrains.annotations.Nullable;

/** Порт корпуса: пробрасывает предметы, баки и энергию контроллера, если машина собрана. Адрес контроллера запоминает при проверке схемы. */
public class AssemblyPortBlockEntity extends BlockEntity {
    @Nullable
    private BlockPos controller;

    public AssemblyPortBlockEntity(BlockPos pos, BlockState state) {
        super(KonturBlockEntities.ASSEMBLY_PORT.get(), pos, state);
    }

    public void setController(BlockPos pos) {
        if (!pos.equals(controller)) {
            controller = pos;
            setChanged();
        }
    }

    @Nullable
    private MachineBlockEntity machine() {
        if (level == null || controller == null || !level.isLoaded(controller)) {
            return null;
        }
        return level.getBlockEntity(controller) instanceof MachineBlockEntity m
                && m instanceof AssemblyController c && c.isFormed() ? m : null;
    }

    @Nullable
    public IItemHandler itemHandler() {
        MachineBlockEntity m = machine();
        return m == null ? null : m.getItemHandler(null);
    }

    @Nullable
    public IFluidHandler fluidHandler() {
        MachineBlockEntity m = machine();
        return m == null ? null : m.getFluidHandler(null);
    }

    @Nullable
    public IEnergyStorage energyStorage() {
        MachineBlockEntity m = machine();
        return m == null ? null : m.getEnergyStorage(null);
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
