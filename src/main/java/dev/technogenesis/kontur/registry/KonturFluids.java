package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.material.Metal;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.common.SoundActions;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import org.jetbrains.annotations.Nullable;

/**
 * Технологические жидкости. Водные текстуры ванильные, цвет задаётся оттенком. Внутренние жидкости
 * (растворы металлов) живут только в машинах и трубах: у них нет блока в мире и ведра.
 */
public final class KonturFluids {
    public static final DeferredRegister<FluidType> FLUID_TYPES =
            DeferredRegister.create(NeoForgeRegistries.Keys.FLUID_TYPES, Kontur.MODID);
    public static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(Registries.FLUID, Kontur.MODID);

    /** Все жидкости мода; заполняется конструкторами, поэтому объявлено первым. */
    public static final List<FluidSet> ALL = new ArrayList<>();

    public static final FluidSet POLLUTED_WATER = new FluidSet("polluted_water", 0xFF7A6A3A, 1100, 1500, true);
    public static final FluidSet TECHNICAL_WATER = new FluidSet("technical_water", 0xFF4FB6C4, 1000, 1000, true);
    public static final FluidSet SULFURIC_ACID = new FluidSet("sulfuric_acid", 0xFFC9D94A, 1830, 2000, true);
    public static final FluidSet SPENT_ACID = new FluidSet("spent_acid", 0xFF7C7A3C, 1300, 1800, true);

    /** Ступень ×5: растворитель (делается в заводе кислоты из угля и кислоты) и отработанный растворитель; внутренние. */
    public static final FluidSet SOLVENT = new FluidSet("solvent", 0xFFD9A441, 900, 1200, false);
    public static final FluidSet SPENT_SOLVENT = new FluidSet("spent_solvent", 0xFF8A6A34, 950, 1400, false);

    /** Ступень ×8: пар из парогенератора; внутренняя жидкость. */
    public static final FluidSet STEAM = new FluidSet("steam", 0xFFE6EEF2, 100, 200, false);

    /** Раствор для каждого металла: жидкости разных металлов никогда не смешиваются. */
    public static final Map<Metal, FluidSet> SOLUTION = new EnumMap<>(Metal.class);

    /** Экстракт металла в растворителе (ступень ×5): у каждого металла свой, разные не смешиваются. */
    public static final Map<Metal, FluidSet> EXTRACT = new EnumMap<>(Metal.class);

    static {
        for (Metal metal : Metal.values()) {
            SOLUTION.put(metal, new FluidSet(metal.id() + "_solution", metal.solutionTint, 1200, 1400, false));
        }
        for (Metal metal : Metal.values()) {
            EXTRACT.put(metal, new FluidSet(metal.id() + "_extract", darker(metal.solutionTint), 1050, 1300, false));
        }
    }

    /** Экстракт темнее раствора того же металла: он растворён в маслянистом растворителе. */
    private static int darker(int argb) {
        int r = (argb >> 16 & 0xFF) * 3 / 4;
        int g = (argb >> 8 & 0xFF) * 3 / 4;
        int b = (argb & 0xFF) * 3 / 4;
        return 0xFF000000 | r << 16 | g << 8 | b;
    }

    private KonturFluids() {
    }

    /** Тип жидкости, источник, поток и (для размещаемых) блок и ведро. */
    public static final class FluidSet {
        public final String name;
        public final int tint;
        public final DeferredHolder<FluidType, FluidType> type;
        public final DeferredHolder<Fluid, BaseFlowingFluid.Source> source;
        public final DeferredHolder<Fluid, BaseFlowingFluid.Flowing> flowing;
        @Nullable
        public final DeferredBlock<LiquidBlock> block;
        @Nullable
        public final DeferredItem<BucketItem> bucket;
        private BaseFlowingFluid.Properties properties;

        private FluidSet(String name, int tint, int density, int viscosity, boolean placeable) {
            this.name = name;
            this.tint = tint;
            this.type = FLUID_TYPES.register(name, () -> new FluidType(FluidType.Properties.create()
                    .density(density).viscosity(viscosity)
                    .sound(SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL)
                    .sound(SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY)));
            this.source = FLUIDS.register(name, () -> new BaseFlowingFluid.Source(props()));
            this.flowing = FLUIDS.register("flowing_" + name, () -> new BaseFlowingFluid.Flowing(props()));
            if (placeable) {
                this.block = KonturBlocks.BLOCKS.register(name, () -> new LiquidBlock(this.source.get(),
                        BlockBehaviour.Properties.ofFullCopy(Blocks.WATER).mapColor(MapColor.COLOR_GRAY)));
                this.bucket = KonturItems.ITEMS.register(name + "_bucket", () -> new BucketItem(this.source.get(),
                        new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));
            } else {
                this.block = null;
                this.bucket = null;
            }
            ALL.add(this);
        }

        private BaseFlowingFluid.Properties props() {
            if (properties == null) {
                properties = new BaseFlowingFluid.Properties(type, source, flowing)
                        .slopeFindDistance(4).levelDecreasePerBlock(1);
                if (block != null) {
                    properties.block(block);
                }
                if (bucket != null) {
                    properties.bucket(bucket);
                }
            }
            return properties;
        }
    }
}
