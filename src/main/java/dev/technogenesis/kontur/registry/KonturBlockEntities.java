package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.blockentity.CableBlockEntity;
import dev.technogenesis.kontur.blockentity.CapacitorBlockEntity;
import dev.technogenesis.kontur.blockentity.ConduitBlockEntity;
import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.blockentity.ProcessingMachineBlockEntity;
import dev.technogenesis.kontur.blockentity.SolidFuelGeneratorBlockEntity;
import dev.technogenesis.kontur.machine.MachineKind;
import java.util.EnumMap;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Block;
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
                    .of(CableBlockEntity::new, KonturBlocks.CABLES.values().stream()
                            .map(b -> (Block) b.get()).toArray(Block[]::new)).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<ConduitBlockEntity>> PIPE =
            BLOCK_ENTITIES.register("pipe", () -> BlockEntityType.Builder
                    .of(ConduitBlockEntity::new, KonturBlocks.PIPES.values().stream()
                            .map(b -> (Block) b.get()).toArray(Block[]::new)).build(null));

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
            case WIND_ROTOR -> new dev.technogenesis.kontur.blockentity.WindRotorBlockEntity(pos, state);
            case THERMAL_GENERATOR -> new dev.technogenesis.kontur.blockentity.ThermalGeneratorBlockEntity(pos, state);
            case STEAM_TURBINE -> new dev.technogenesis.kontur.blockentity.SteamTurbineBlockEntity(pos, state);
            case SOLAR_PANEL, SOLAR_PANEL_ADVANCED ->
                    new dev.technogenesis.kontur.blockentity.SolarPanelBlockEntity(kind, pos, state);
            case MINER -> new dev.technogenesis.kontur.blockentity.MinerBlockEntity(pos, state);
            case WATER_PUMP -> new dev.technogenesis.kontur.blockentity.WaterPumpBlockEntity(pos, state);
            case SOLAR_FARM -> new dev.technogenesis.kontur.blockentity.SolarFarmBlockEntity(pos, state);
            default -> new ProcessingMachineBlockEntity(kind, pos, state);
        };
    }

    /** Главная часть крупной машины, если сторона side этой клетки - её разъём; иначе null. */
    private static MachineBlockEntity portOwner(net.minecraft.world.level.Level level, BlockPos pos, BlockState state,
                                                @org.jetbrains.annotations.Nullable net.minecraft.core.Direction side) {
        if (side == null || !(state.getBlock() instanceof dev.technogenesis.kontur.block.MultiMachineBlock block)) {
            return null;
        }
        var facing = state.getValue(dev.technogenesis.kontur.block.MachineBlock.FACING);
        var relative = dev.technogenesis.kontur.machine.RelativeSide.of(facing, side);
        int part = state.getValue(dev.technogenesis.kontur.block.MultiMachineBlock.PART);
        if (!block.kind.hasPort(relative) || block.layout.portIndex(relative) != part) {
            return null;
        }
        BlockPos master = block.layout.masterOf(pos, facing, part);
        return level.isLoaded(master) && level.getBlockEntity(master) instanceof MachineBlockEntity be ? be : null;
    }

    public static void registerCapabilities(RegisterCapabilitiesEvent event) {
        for (MachineKind kind : MachineKind.values()) {
            BlockEntityType<MachineBlockEntity> type = MACHINES.get(kind).get();
            if (kind.layout() != null) {
                // крупная машина: способности отдаёт только клетка с разъёмом на нужной стороне, запрос уходит к главной части
                Block block = KonturBlocks.MACHINES.get(kind).get();
                event.registerBlock(Capabilities.ItemHandler.BLOCK, (level, pos, state, be, side) -> {
                    MachineBlockEntity owner = portOwner(level, pos, state, side);
                    return owner == null ? null : owner.getItemHandler(side);
                }, block);
                event.registerBlock(Capabilities.FluidHandler.BLOCK, (level, pos, state, be, side) -> {
                    MachineBlockEntity owner = portOwner(level, pos, state, side);
                    return owner == null ? null : owner.getFluidHandler(side);
                }, block);
                event.registerBlock(Capabilities.EnergyStorage.BLOCK, (level, pos, state, be, side) -> {
                    MachineBlockEntity owner = portOwner(level, pos, state, side);
                    return owner == null ? null : owner.getEnergyStorage(side);
                }, block);
                continue;
            }
            event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, type, (be, side) -> be.getItemHandler(side));
            event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, type, (be, side) -> be.getFluidHandler(side));
            if (kind != MachineKind.SOLAR_FARM) {
                event.registerBlockEntity(Capabilities.EnergyStorage.BLOCK, type, (be, side) -> be.getEnergyStorage(side));
            }
        }
        // ферма отдаёт энергию через разъёмы на боковых гранях задних (высоких) плиток; запрос уходит к главной части
        event.registerBlock(Capabilities.EnergyStorage.BLOCK, (level, pos, state, be, side) -> {
            var facing = state.getValue(dev.technogenesis.kontur.block.SolarFarmBlock.FACING);
            boolean portSide = side == facing.getClockWise() || side == facing.getCounterClockWise();
            if (state.getValue(dev.technogenesis.kontur.block.SolarFarmBlock.PART) < 3 || !portSide) {
                return null;
            }
            BlockPos master = dev.technogenesis.kontur.block.SolarFarmBlock.masterOf(pos, state);
            return level.getBlockEntity(master) instanceof MachineBlockEntity farm ? farm.getEnergyStorage(null) : null;
        }, KonturBlocks.SOLAR_FARM.get());
    }
}
