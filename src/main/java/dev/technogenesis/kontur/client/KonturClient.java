package dev.technogenesis.kontur.client;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.registry.KonturFluids;
import dev.technogenesis.kontur.registry.KonturMenus;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.ModelEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;

/** Клиентская часть: экраны, оттенки жидкостей (текстуры воды ванильные) и слои отрисовки. */
@EventBusSubscriber(modid = Kontur.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class KonturClient {
    private static final ResourceLocation WATER_STILL = ResourceLocation.withDefaultNamespace("block/water_still");
    private static final ResourceLocation WATER_FLOW = ResourceLocation.withDefaultNamespace("block/water_flow");
    private static final ResourceLocation WATER_OVERLAY = ResourceLocation.withDefaultNamespace("block/water_overlay");

    private KonturClient() {
    }

    @SubscribeEvent
    public static void registerScreens(RegisterMenuScreensEvent event) {
        event.register(KonturMenus.MACHINE.get(), MachineScreen::new);
    }

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        KonturBlockEntities.MACHINES.values().forEach(type -> event.registerBlockEntityRenderer(type.get(), MachinePortRenderer::new));
        event.registerBlockEntityRenderer(KonturBlockEntities.PIPE.get(), ConduitPortRenderer::new);
    }

    @SubscribeEvent
    public static void registerExtraModels(ModelEvent.RegisterAdditional event) {
        event.register(WindBladesRenderer.BLADES);
    }

    @SubscribeEvent
    public static void registerFluidExtensions(RegisterClientExtensionsEvent event) {
        for (KonturFluids.FluidSet set : KonturFluids.ALL) {
            event.registerFluidType(new IClientFluidTypeExtensions() {
                @Override
                public ResourceLocation getStillTexture() {
                    return WATER_STILL;
                }

                @Override
                public ResourceLocation getFlowingTexture() {
                    return WATER_FLOW;
                }

                @Override
                public ResourceLocation getOverlayTexture() {
                    return WATER_OVERLAY;
                }

                @Override
                public int getTintColor() {
                    return set.tint;
                }
            }, set.type.get());
        }
    }

    @SubscribeEvent
    public static void clientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            for (KonturFluids.FluidSet set : KonturFluids.ALL) {
                ItemBlockRenderTypes.setRenderLayer(set.source.get(), RenderType.translucent());
                ItemBlockRenderTypes.setRenderLayer(set.flowing.get(), RenderType.translucent());
            }
        });
    }
}
