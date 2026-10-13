package dev.technogenesis.kontur.registry;

import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.item.MetalFormItem;
import dev.technogenesis.kontur.item.ModuleItem;
import dev.technogenesis.kontur.item.WrenchItem;
import dev.technogenesis.kontur.machine.ModuleTier;
import dev.technogenesis.kontur.material.Form;
import dev.technogenesis.kontur.material.Metal;
import dev.technogenesis.kontur.material.Mineral;
import java.util.EnumMap;
import java.util.Map;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Предметы: сырьё, слитки, формы переработки по металлам и прочие материалы. */
public final class KonturItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Kontur.MODID);

    public static final Map<Mineral, DeferredItem<Item>> RAW = new EnumMap<>(Mineral.class);
    /** Слитки только новых металлов; железо, медь и золото - ванильные. */
    public static final Map<Metal, DeferredItem<Item>> INGOT = new EnumMap<>(Metal.class);
    public static final Map<Form, Map<Metal, DeferredItem<Item>>> FORMS = new EnumMap<>(Form.class);

    public static final Map<ModuleTier, DeferredItem<Item>> MODULES = new EnumMap<>(ModuleTier.class);
    public static final Map<dev.technogenesis.kontur.machine.RadiatorTier, DeferredItem<Item>> RADIATORS =
            new EnumMap<>(dev.technogenesis.kontur.machine.RadiatorTier.class);
    public static final Map<dev.technogenesis.kontur.machine.CoatingTier, DeferredItem<Item>> COATINGS =
            new EnumMap<>(dev.technogenesis.kontur.machine.CoatingTier.class);
    public static final Map<dev.technogenesis.kontur.machine.DrillTier, DeferredItem<Item>> DRILL_TIPS =
            new EnumMap<>(dev.technogenesis.kontur.machine.DrillTier.class);
    /** Детали для крафта машин в порядке показа: платы, обмотки, приводы, процессоры. */
    public static final java.util.List<DeferredItem<Item>> COMPONENTS = new java.util.ArrayList<>();
    public static final String[] COMPONENT_IDS = {
            "circuit_blank", "circuit_board", "control_circuit", "processor_blank", "processor", "plasma_controller",
            "winding", "magnet", "power_module", "gear_drive", "precision_drive", "valve_block", "heat_plate"
    };
    public static final DeferredItem<Item> WRENCH = ITEMS.register("wrench", () -> new WrenchItem(new Item.Properties()));
    public static final DeferredItem<Item> GANGUE = simple("gangue");
    public static final DeferredItem<Item> ASH = simple("ash");
    public static final DeferredItem<Item> WET_SLUDGE = simple("wet_sludge");
    public static final DeferredItem<Item> MINERAL_FRACTION = simple("mineral_fraction");
    public static final DeferredItem<Item> SALT = simple("salt");
    public static final DeferredItem<Item> SULFUR_POWDER = simple("sulfur_powder");
    public static final DeferredItem<Item> CRUSHED_SPODUMENE = simple("crushed_spodumene");
    public static final DeferredItem<Item> GRAPHITE = simple("graphite");

    static {
        for (String id : COMPONENT_IDS) {
            COMPONENTS.add(ITEMS.register(id, () -> new dev.technogenesis.kontur.item.ComponentItem(new Item.Properties(), id)));
        }
        for (Mineral mineral : Mineral.values()) {
            RAW.put(mineral, simple(mineral.rawId));
        }
        for (Metal metal : Metal.values()) {
            if (!metal.vanilla) {
                INGOT.put(metal, simple(metal.id() + "_ingot"));
            }
        }
        for (dev.technogenesis.kontur.machine.CoatingTier tier : dev.technogenesis.kontur.machine.CoatingTier.values()) {
            COATINGS.put(tier, ITEMS.register(tier.itemId(),
                    () -> new dev.technogenesis.kontur.item.CoatingItem(new Item.Properties(), tier)));
        }
        for (dev.technogenesis.kontur.machine.RadiatorTier tier : dev.technogenesis.kontur.machine.RadiatorTier.values()) {
            RADIATORS.put(tier, ITEMS.register(tier.itemId(),
                    () -> new dev.technogenesis.kontur.item.RadiatorItem(new Item.Properties(), tier)));
        }
        for (dev.technogenesis.kontur.machine.DrillTier tier : dev.technogenesis.kontur.machine.DrillTier.values()) {
            DRILL_TIPS.put(tier, ITEMS.register(tier.itemId(),
                    () -> new dev.technogenesis.kontur.item.DrillTipItem(new Item.Properties(), tier)));
        }
        for (ModuleTier tier : ModuleTier.values()) {
            MODULES.put(tier, ITEMS.register(tier.itemId(), () -> new ModuleItem(new Item.Properties(), tier)));
        }
        for (Form form : Form.values()) {
            Map<Metal, DeferredItem<Item>> byMetal = new EnumMap<>(Metal.class);
            for (Metal metal : Metal.values()) {
                byMetal.put(metal, ITEMS.register(form.itemId(metal),
                        () -> new MetalFormItem(new Item.Properties(), metal, form)));
            }
            FORMS.put(form, byMetal);
        }
    }

    private KonturItems() {
    }

    private static DeferredItem<Item> simple(String id) {
        return ITEMS.registerSimpleItem(id, new Item.Properties());
    }
}
