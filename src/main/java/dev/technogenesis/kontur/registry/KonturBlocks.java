package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.CableBlock;
import dev.technogenesis.kontur.block.ConduitBlock;
import dev.technogenesis.kontur.network.CableTier;
import dev.technogenesis.kontur.network.PipeTier;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.block.MultiMachineBlock;
import dev.technogenesis.kontur.block.SolarFarmBlock;
import dev.technogenesis.kontur.item.MultiMachineItem;
import dev.technogenesis.kontur.item.SolarFarmItem;
import net.minecraft.world.item.Item;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.material.Mineral;
import java.util.EnumMap;
import java.util.Map;
import java.util.function.Supplier;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Блоки: руды, строительные материалы, машины и кабель. */
public final class KonturBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Kontur.MODID);

    public static final Map<Mineral, DeferredBlock<Block>> ORE = new EnumMap<>(Mineral.class);
    public static final Map<Mineral, DeferredBlock<Block>> DEEPSLATE_ORE = new EnumMap<>(Mineral.class);
    public static final Map<Mineral, DeferredBlock<Block>> NETHER_ORE = new EnumMap<>(Mineral.class);

    public static final DeferredBlock<Block> ASH_BLOCK = block("ash_block", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GRAY).strength(0.6f).sound(SoundType.GRAVEL)));
    public static final DeferredBlock<Block> AGGREGATE_BLOCK = block("aggregate_block", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(1.5f, 6.0f)
                    .sound(SoundType.STONE).requiresCorrectToolForDrops()));

    /** Пустая рама механизма: каркас без начинки, используется в рецептах машин (прозрачна, как рама на моделях машин). */
    public static final DeferredBlock<Block> MACHINE_FRAME = block("machine_frame", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(3.0f, 6.0f).sound(SoundType.METAL)
                    .requiresCorrectToolForDrops().noOcclusion()));

    /** Корпуса и порты собираемых игроком машин: из них строится коробка по схеме (см. AssemblyShape). */
    public static final DeferredBlock<Block> FUSION_CASING = block("fusion_casing", () -> new dev.technogenesis.kontur.block.AssemblyCasingBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(4.0f, 12.0f).sound(SoundType.METAL)
                    .requiresCorrectToolForDrops()));
    public static final DeferredBlock<Block> TURBINE_CASING = block("turbine_casing", () -> new dev.technogenesis.kontur.block.AssemblyCasingBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(4.0f, 12.0f).sound(SoundType.METAL)
                    .requiresCorrectToolForDrops()));
    public static final DeferredBlock<Block> COOLER_CASING = block("cooler_casing", () -> new dev.technogenesis.kontur.block.AssemblyCasingBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(3.0f, 9.0f).sound(SoundType.STONE)
                    .requiresCorrectToolForDrops()));
    /** Ротор паротурбинного зала: блоки вала с лопатками, которые игрок ставит в тоннель. */
    public static final DeferredBlock<Block> TURBINE_ROTOR = block("turbine_rotor", () -> new dev.technogenesis.kontur.block.AssemblyCasingBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(3.0f, 9.0f).sound(SoundType.METAL)
                    .requiresCorrectToolForDrops().noOcclusion()));
    public static final DeferredBlock<Block> FURNACE_CASING = block("furnace_casing", () -> new dev.technogenesis.kontur.block.AssemblyCasingBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_RED).strength(3.0f, 9.0f).sound(SoundType.STONE)
                    .requiresCorrectToolForDrops()));
    public static final DeferredBlock<dev.technogenesis.kontur.block.AssemblyPortBlock> ASSEMBLY_PORT = block("assembly_port",
            () -> new dev.technogenesis.kontur.block.AssemblyPortBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.METAL).strength(4.0f, 12.0f).sound(SoundType.METAL).requiresCorrectToolForDrops()));

    public static final Map<MachineKind, DeferredBlock<MachineBlock>> MACHINES = new EnumMap<>(MachineKind.class);
    public static final DeferredBlock<MachineBlock> JAW_CRUSHER = machine(MachineKind.JAW_CRUSHER);
    public static final DeferredBlock<MachineBlock> WASHING_DRUM = machine(MachineKind.WASHING_DRUM);
    public static final DeferredBlock<MachineBlock> MAGNETIC_SEPARATOR = machine(MachineKind.MAGNETIC_SEPARATOR);
    public static final DeferredBlock<MachineBlock> SETTLING_TANK = machine(MachineKind.SETTLING_TANK);
    public static final DeferredBlock<MachineBlock> SOLID_FUEL_GENERATOR = machine(MachineKind.SOLID_FUEL_GENERATOR);
    public static final DeferredBlock<MachineBlock> CARBON_CAPACITOR = machine(MachineKind.CARBON_CAPACITOR);
    public static final DeferredBlock<MachineBlock> TAILINGS_MILL = machine(MachineKind.TAILINGS_MILL);
    public static final DeferredBlock<MachineBlock> ACID_PLANT = machine(MachineKind.ACID_PLANT);
    public static final DeferredBlock<MachineBlock> LEACHING_REACTOR = machine(MachineKind.LEACHING_REACTOR);
    public static final DeferredBlock<MachineBlock> FILTER_PRESS = machine(MachineKind.FILTER_PRESS);
    public static final DeferredBlock<MachineBlock> PRECIPITATION_REACTOR = machine(MachineKind.PRECIPITATION_REACTOR);
    public static final DeferredBlock<MachineBlock> ACID_REGENERATION_COLUMN =
            machine(MachineKind.ACID_REGENERATION_COLUMN);
    public static final DeferredBlock<MachineBlock> EXTRACTOR = machine(MachineKind.EXTRACTOR);
    public static final DeferredBlock<MachineBlock> ELECTROLYZER = machine(MachineKind.ELECTROLYZER);
    public static final DeferredBlock<MachineBlock> SOLVENT_REGENERATOR = machine(MachineKind.SOLVENT_REGENERATOR);
    public static final DeferredBlock<MachineBlock> ATTRITOR = machine(MachineKind.ATTRITOR);
    public static final DeferredBlock<MachineBlock> STEAM_GENERATOR = machine(MachineKind.STEAM_GENERATOR);
    public static final DeferredBlock<MachineBlock> AUTOCLAVE = machine(MachineKind.AUTOCLAVE);
    public static final DeferredBlock<MachineBlock> PLASMA_GENERATOR = machine(MachineKind.PLASMA_GENERATOR);
    public static final DeferredBlock<MachineBlock> FUSION_REACTOR = machine(MachineKind.FUSION_REACTOR);
    public static final DeferredBlock<MachineBlock> BLAST_FURNACE = machine(MachineKind.BLAST_FURNACE);
    public static final DeferredBlock<MachineBlock> TURBINE_HALL = machine(MachineKind.TURBINE_HALL);
    public static final DeferredBlock<MachineBlock> COOLING_TOWER = machine(MachineKind.COOLING_TOWER);
    public static final DeferredBlock<MachineBlock> ALLOY_FURNACE = machine(MachineKind.ALLOY_FURNACE);
    public static final DeferredBlock<MachineBlock> WATER_SPLITTER = machine(MachineKind.WATER_SPLITTER);
    public static final DeferredBlock<MachineBlock> HYDROGEN_GENERATOR = machine(MachineKind.HYDROGEN_GENERATOR);
    public static final DeferredBlock<MachineBlock> PLASMA_FURNACE = machine(MachineKind.PLASMA_FURNACE);
    public static final DeferredBlock<MachineBlock> VACUUM_CASTER = machine(MachineKind.VACUUM_CASTER);
    public static final DeferredBlock<MachineBlock> WIND_ROTOR = machine(MachineKind.WIND_ROTOR);
    public static final DeferredBlock<MachineBlock> THERMAL_GENERATOR = machine(MachineKind.THERMAL_GENERATOR);
    public static final DeferredBlock<MachineBlock> STEAM_TURBINE = machine(MachineKind.STEAM_TURBINE);
    public static final DeferredBlock<MachineBlock> WATER_PUMP = machine(MachineKind.WATER_PUMP);
    public static final DeferredBlock<MachineBlock> MINER = machine(MachineKind.MINER);
    public static final DeferredBlock<dev.technogenesis.kontur.block.MinerRailBlock> MINER_RAIL = block("miner_rail",
            () -> new dev.technogenesis.kontur.block.MinerRailBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL)
                    .strength(2.0f, 6.0f).sound(SoundType.METAL).requiresCorrectToolForDrops().noOcclusion()));
    public static final DeferredBlock<MachineBlock> SOLAR_PANEL = machine(MachineKind.SOLAR_PANEL);
    public static final DeferredBlock<MachineBlock> SOLAR_PANEL_ADVANCED = machine(MachineKind.SOLAR_PANEL_ADVANCED);
    public static final DeferredBlock<MachineBlock> SOLAR_FARM = machine(MachineKind.SOLAR_FARM);

    /** Кабели по классам (энергия) и трубы по видам и скоростям (предметы, жидкости). */
    public static final Map<CableTier, DeferredBlock<CableBlock>> CABLES = new EnumMap<>(CableTier.class);
    public static final Map<PipeTier, DeferredBlock<ConduitBlock>> PIPES = new EnumMap<>(PipeTier.class);

    static {
        for (CableTier tier : CableTier.values()) {
            CABLES.put(tier, block(tier.id, () -> new CableBlock(
                    BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(1.0f, 3.0f)
                            .sound(SoundType.WOOL).noOcclusion(), tier)));
        }
        for (PipeTier tier : PipeTier.values()) {
            PIPES.put(tier, block(tier.id, () -> new ConduitBlock(
                    BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(1.5f, 4.0f)
                            .sound(SoundType.METAL).noOcclusion(), tier)));
        }
        for (Mineral mineral : Mineral.values()) {
            float hardness = mineral.hardness;
            UniformInt xp = UniformInt.of(mineral.xpMin, mineral.xpMax);
            ORE.put(mineral, block(mineral.oreId, () -> new DropExperienceBlock(xp,
                    BlockBehaviour.Properties.ofFullCopy(Blocks.IRON_ORE).strength(hardness, 3.0f))));
            DEEPSLATE_ORE.put(mineral, block("deepslate_" + mineral.oreId, () -> new DropExperienceBlock(xp,
                    BlockBehaviour.Properties.ofFullCopy(Blocks.DEEPSLATE_IRON_ORE).strength(hardness + 1.5f, 3.0f))));
            if (mineral.nether) {
                NETHER_ORE.put(mineral, block("nether_" + mineral.oreId, () -> new DropExperienceBlock(xp,
                        BlockBehaviour.Properties.ofFullCopy(Blocks.NETHER_GOLD_ORE).strength(hardness, 3.0f))));
            }
        }
    }

    private KonturBlocks() {
    }

    private static <B extends Block> DeferredBlock<B> block(String id, Supplier<B> factory) {
        DeferredBlock<B> holder = BLOCKS.register(id, factory);
        KonturItems.ITEMS.registerSimpleBlockItem(id, holder);
        return holder;
    }

    /** Источники без огня (солнце, ветер) не светят, остальные работающие машины дают слабый свет. */
    private static boolean glows(MachineKind kind) {
        return switch (kind) {
            case SOLAR_PANEL, SOLAR_PANEL_ADVANCED, SOLAR_FARM, WIND_ROTOR -> false;
            default -> true;
        };
    }

    private static DeferredBlock<MachineBlock> machine(MachineKind kind) {
        boolean glow = glows(kind);
        DeferredBlock<MachineBlock> holder = BLOCKS.register(kind.id, () -> {
            BlockBehaviour.Properties props = BlockBehaviour.Properties.of().mapColor(MapColor.METAL)
                    .strength(3.5f, 6.0f).sound(SoundType.METAL).requiresCorrectToolForDrops().noOcclusion()
                    .lightLevel(state -> glow && state.hasProperty(MachineBlock.ACTIVE)
                            && state.getValue(MachineBlock.ACTIVE) ? 8 : 0);
            if (kind == MachineKind.SOLAR_FARM) {
                return new SolarFarmBlock(props, kind);
            }
            if (kind.shape() != null) {
                return new dev.technogenesis.kontur.block.AssemblyControllerBlock(props, kind);
            }
            return kind.layout() != null ? new MultiMachineBlock(props, kind) : new MachineBlock(props, kind);
        });
        if (kind == MachineKind.SOLAR_FARM) {
            KonturItems.ITEMS.register(kind.id, () -> new SolarFarmItem((SolarFarmBlock) holder.get(), new Item.Properties()));
        } else if (kind.layout() != null) {
            KonturItems.ITEMS.register(kind.id, () -> new MultiMachineItem((MultiMachineBlock) holder.get(), new Item.Properties()));
        } else {
            KonturItems.ITEMS.register(kind.id, () -> new dev.technogenesis.kontur.item.MachineBlockItem(holder.get(), new Item.Properties()));
        }
        MACHINES.put(kind, holder);
        return holder;
    }
}
