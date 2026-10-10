package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.blockentity.CableBlockEntity;
import dev.technogenesis.kontur.blockentity.CapacitorBlockEntity;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.blockentity.ProcessingMachineBlockEntity;
import dev.technogenesis.kontur.blockentity.SolidFuelGeneratorBlockEntity;
import dev.technogenesis.kontur.machine.MachineKind;
import java.util.EnumMap;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Типы блок-сущностей и привязка capability (предметы, жидкости, энергия) для машин. */
public final class KonturBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, Kontur.MODID);

    public static final Map<MachineKind, DeferredHolder<BlockEntityType<?>, BlockEntityType<MachineBlockEntity>>> MACHINES =
            new EnumMap<>(MachineKind.class);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<CableBlockEntity>> CABLE =
            BLOCK_ENTITIES.register("cable", () -> BlockEntityType.Builder
                    .of(CableBlockEntity::new, KonturBlocks.COPPER_WIRE.get()).build(null));

    static {
        for (MachineKind kind : MachineKind.values()) {
            MACHINES.put(kind, BLOCK_ENTITIES.register(kind.id, () -> BlockEntityType.Builder
                    .<MachineBlockEntity>of((pos, state) -> createMachine(kind, pos, state),
                            KonturBlocks.MACHINES.get(kind).get()).build(null)));
        }
    }

    private KonturBlockEntities() {
    }

    public static MachineBlockEntity createMachine(MachineKind kind, BlockPos pos, BlockState state) {
        return switch (kind) {
            case SOLID_FUEL_GENERATOR -> new SolidFuelGeneratorBlockEntity(pos, state);
            case CARBON_CAPACITOR -> new CapacitorBlockEntity(pos, state);
            default -> new ProcessingMachineBlockEntity(kind, pos, state);
        };
    }

    public static void registerCapabilities(RegisterCapabilitiesEvent event) {
        for (MachineKind kind : MachineKind.values()) {
            BlockEntityType<MachineBlockEntity> type = MACHINES.get(kind).get();
            event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, type, (be, side) -> be.getItemHandler(side));
            event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, type, (be, side) -> be.getFluidHandler(side));
            event.registerBlockEntity(Capabilities.EnergyStorage.BLOCK, type, (be, side) -> be.getEnergyStorage(side));
        }
    }
}
