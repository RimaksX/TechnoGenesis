package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.material.Form;
import dev.technogenesis.kontur.material.Metal;
import dev.technogenesis.kontur.material.Mineral;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class KonturCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Kontur.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.kontur"))
                    .icon(() -> new ItemStack(KonturBlocks.JAW_CRUSHER.get()))
                    .displayItems((params, out) -> {
                        for (Mineral m : Mineral.values()) {
                            out.accept(KonturBlocks.ORE.get(m));
                            out.accept(KonturBlocks.DEEPSLATE_ORE.get(m));
                            if (KonturBlocks.NETHER_ORE.containsKey(m)) {
                                out.accept(KonturBlocks.NETHER_ORE.get(m));
                            }
                        }
                        for (Mineral m : Mineral.values()) {
                            out.accept(KonturItems.RAW.get(m));
                        }
                        for (Metal m : Metal.values()) {
                            if (!m.vanilla) {
                                out.accept(KonturItems.INGOT.get(m));
                            }
                        }
                        for (Form form : Form.values()) {
                            for (Metal m : Metal.values()) {
                                out.accept(KonturItems.FORMS.get(form).get(m));
                            }
                        }
                        out.accept(KonturItems.GANGUE);
                        out.accept(KonturItems.MINERAL_FRACTION);
                        out.accept(KonturItems.WET_SLUDGE);
                        out.accept(KonturItems.ASH);
                        out.accept(KonturItems.SALT);
                        out.accept(KonturItems.SULFUR_POWDER);
                        out.accept(KonturItems.CRUSHED_SPODUMENE);
                        out.accept(KonturItems.GRAPHITE);
                        out.accept(KonturBlocks.ASH_BLOCK);
                        out.accept(KonturBlocks.AGGREGATE_BLOCK);
                        out.accept(KonturItems.MACHINE_FRAME);
                        out.accept(KonturItems.WRENCH);
                        for (dev.technogenesis.kontur.machine.ModuleTier tier : dev.technogenesis.kontur.machine.ModuleTier.values()) {
                            out.accept(KonturItems.MODULES.get(tier));
                        }
                        for (dev.technogenesis.kontur.machine.RadiatorTier tier : dev.technogenesis.kontur.machine.RadiatorTier.values()) {
                            out.accept(KonturItems.RADIATORS.get(tier));
                        }
                        out.accept(KonturBlocks.JAW_CRUSHER);
                        out.accept(KonturBlocks.WASHING_DRUM);
                        out.accept(KonturBlocks.MAGNETIC_SEPARATOR);
                        out.accept(KonturBlocks.SETTLING_TANK);
                        out.accept(KonturBlocks.SOLID_FUEL_GENERATOR);
                        out.accept(KonturBlocks.WIND_ROTOR);
                        out.accept(KonturBlocks.THERMAL_GENERATOR);
                        out.accept(KonturBlocks.STEAM_TURBINE);
                        out.accept(KonturBlocks.WATER_PUMP);
                        out.accept(KonturBlocks.MINER);
                        out.accept(KonturBlocks.MINER_RAIL);
                        for (dev.technogenesis.kontur.machine.DrillTier tier : dev.technogenesis.kontur.machine.DrillTier.values()) {
                            out.accept(KonturItems.DRILL_TIPS.get(tier));
                        }
                        out.accept(KonturBlocks.SOLAR_PANEL);
                        out.accept(KonturBlocks.SOLAR_PANEL_ADVANCED);
                        out.accept(KonturBlocks.SOLAR_FARM);
                        for (dev.technogenesis.kontur.machine.CoatingTier tier : dev.technogenesis.kontur.machine.CoatingTier.values()) {
                            out.accept(KonturItems.COATINGS.get(tier));
                        }
                        out.accept(KonturBlocks.CARBON_CAPACITOR);
                        out.accept(KonturBlocks.TAILINGS_MILL);
                        out.accept(KonturBlocks.ACID_PLANT);
                        out.accept(KonturBlocks.LEACHING_REACTOR);
                        out.accept(KonturBlocks.FILTER_PRESS);
                        out.accept(KonturBlocks.PRECIPITATION_REACTOR);
                        out.accept(KonturBlocks.ACID_REGENERATION_COLUMN);
                        for (dev.technogenesis.kontur.network.CableTier tier : dev.technogenesis.kontur.network.CableTier.values()) {
                            out.accept(KonturBlocks.CABLES.get(tier));
                        }
                        for (dev.technogenesis.kontur.network.PipeTier tier : dev.technogenesis.kontur.network.PipeTier.values()) {
                            out.accept(KonturBlocks.PIPES.get(tier));
                        }
                        for (KonturFluids.FluidSet fluid : KonturFluids.ALL) {
                            if (fluid.bucket != null) {
                                out.accept(fluid.bucket);
                            }
                        }
                    })
                    .build());

    private KonturCreativeTabs() {
    }
}
