package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.block.CableBlock;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.material.Metal;
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

/** Блоки: руды, металлические блоки, строительные материалы, машины и кабель. */
public final class KonturBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Kontur.MODID);

    public static final Map<Mineral, DeferredBlock<Block>> ORE = new EnumMap<>(Mineral.class);
    public static final Map<Mineral, DeferredBlock<Block>> DEEPSLATE_ORE = new EnumMap<>(Mineral.class);
    public static final Map<Mineral, DeferredBlock<Block>> NETHER_ORE = new EnumMap<>(Mineral.class);
    public static final Map<Metal, DeferredBlock<Block>> STORAGE = new EnumMap<>(Metal.class);

    public static final DeferredBlock<Block> ASH_BLOCK = block("ash_block", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GRAY).strength(0.6f).sound(SoundType.GRAVEL)));
    public static final DeferredBlock<Block> AGGREGATE_BLOCK = block("aggregate_block", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(1.5f, 6.0f)
                    .sound(SoundType.STONE).requiresCorrectToolForDrops()));

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

    public static final DeferredBlock<CableBlock> COPPER_WIRE = block("copper_wire", () -> new CableBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).strength(1.0f, 3.0f)
                    .sound(SoundType.METAL).noOcclusion(), dev.technogenesis.kontur.network.CableTier.COPPER));

    static {
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
        for (Metal metal : Metal.values()) {
            if (!metal.vanilla) {
                STORAGE.put(metal, block(metal.id() + "_block", () -> new Block(
                        BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(5.0f, 6.0f)
                                .sound(SoundType.METAL).requiresCorrectToolForDrops())));
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

    private static DeferredBlock<MachineBlock> machine(MachineKind kind) {
        DeferredBlock<MachineBlock> holder = block(kind.id, () -> new MachineBlock(
                BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(3.5f, 6.0f).sound(SoundType.METAL)
                        .requiresCorrectToolForDrops().noOcclusion()
                        .lightLevel(state -> state.hasProperty(MachineBlock.ACTIVE) && state.getValue(MachineBlock.ACTIVE) ? 8 : 0),
                kind));
        MACHINES.put(kind, holder);
        return holder;
    }
}
