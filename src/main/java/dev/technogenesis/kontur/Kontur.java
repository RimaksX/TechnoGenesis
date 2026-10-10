package dev.technogenesis.kontur;

import dev.technogenesis.kontur.network.CableNetworkManager;
import dev.technogenesis.kontur.network.PipeNetworkManager;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import dev.technogenesis.kontur.registry.KonturBlocks;
import dev.technogenesis.kontur.registry.KonturCreativeTabs;
import dev.technogenesis.kontur.registry.KonturFluids;
import dev.technogenesis.kontur.registry.KonturItems;
import dev.technogenesis.kontur.registry.KonturMenus;
import dev.technogenesis.kontur.registry.KonturRecipes;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.LevelTickEvent;

/** Контур - промышленная металлургия. Точка входа мода. */
@Mod(Kontur.MODID)
public class Kontur {
    public static final String MODID = "kontur";

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }

    public Kontur(IEventBus modBus) {
        KonturBlocks.BLOCKS.register(modBus);
        KonturItems.ITEMS.register(modBus);
        KonturFluids.FLUID_TYPES.register(modBus);
        KonturFluids.FLUIDS.register(modBus);
        KonturBlockEntities.BLOCK_ENTITIES.register(modBus);
        KonturMenus.MENUS.register(modBus);
        KonturRecipes.TYPES.register(modBus);
        KonturRecipes.SERIALIZERS.register(modBus);
        KonturCreativeTabs.TABS.register(modBus);

        modBus.addListener(KonturBlockEntities::registerCapabilities);
        NeoForge.EVENT_BUS.addListener(this::onLevelTick);
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent e) -> {
            CableNetworkManager.clear();
            PipeNetworkManager.clear();
        });
    }

    private void onLevelTick(LevelTickEvent.Post event) {
        if (!event.getLevel().isClientSide()) {
            CableNetworkManager.tick(event.getLevel());
            PipeNetworkManager.tick(event.getLevel());
        }
    }
}
