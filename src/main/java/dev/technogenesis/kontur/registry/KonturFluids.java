package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
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

/** Технологические жидкости. Водные текстуры ванильные, цвет задаётся оттенком. */
public final class KonturFluids {
    public static final DeferredRegister<FluidType> FLUID_TYPES =
            DeferredRegister.create(NeoForgeRegistries.Keys.FLUID_TYPES, Kontur.MODID);
    public static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(Registries.FLUID, Kontur.MODID);

    public static final FluidSet POLLUTED_WATER = new FluidSet("polluted_water", 0xFF7A6A3A, 1100, 1500);
    public static final FluidSet TECHNICAL_WATER = new FluidSet("technical_water", 0xFF4FB6C4, 1000, 1000);

    private KonturFluids() {
    }

    /** Тип жидкости, источник, поток, блок и ведро. */
    public static final class FluidSet {
        public final String name;
        public final int tint;
        public final DeferredHolder<FluidType, FluidType> type;
        public final DeferredHolder<Fluid, BaseFlowingFluid.Source> source;
        public final DeferredHolder<Fluid, BaseFlowingFluid.Flowing> flowing;
        public final DeferredBlock<LiquidBlock> block;
        public final DeferredItem<BucketItem> bucket;
        private BaseFlowingFluid.Properties properties;

        private FluidSet(String name, int tint, int density, int viscosity) {
            this.name = name;
            this.tint = tint;
            this.type = FLUID_TYPES.register(name, () -> new FluidType(FluidType.Properties.create()
                    .density(density).viscosity(viscosity)
                    .sound(SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL)
                    .sound(SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY)));
            this.source = FLUIDS.register(name, () -> new BaseFlowingFluid.Source(props()));
            this.flowing = FLUIDS.register("flowing_" + name, () -> new BaseFlowingFluid.Flowing(props()));
            this.block = KonturBlocks.BLOCKS.register(name, () -> new LiquidBlock(this.source.get(),
                    BlockBehaviour.Properties.ofFullCopy(Blocks.WATER).mapColor(MapColor.COLOR_GRAY)));
            this.bucket = KonturItems.ITEMS.register(name + "_bucket", () -> new BucketItem(this.source.get(),
                    new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));
        }

        private BaseFlowingFluid.Properties props() {
            if (properties == null) {
                properties = new BaseFlowingFluid.Properties(type, source, flowing)
                        .block(block).bucket(bucket).slopeFindDistance(3).levelDecreasePerBlock(2);
            }
            return properties;
        }
    }
}
