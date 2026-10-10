package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;

/** Теги мода. */
public final class KonturTags {
    /** Блоки, которые шахтёр не ломает (кроме бедрока и всего, что в принципе неразрушимо). */
    public static final TagKey<Block> MINER_UNBREAKABLE = TagKey.create(Registries.BLOCK,
            ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "miner_unbreakable"));

    private KonturTags() {
    }
}
