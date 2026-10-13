package dev.technogenesis.kontur.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.technogenesis.kontur.Kontur;
import dev.technogenesis.kontur.machine.AssemblyShape;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.neoforged.neoforge.client.event.ModelEvent;

/**
 * Готовые модели собираемых машин. Модель каждой машины нарезана на клетки 16x16x16 (как крупные машины) и описана в
 * assets/kontur/assembly/&lt;машина&gt;.json: размеры и список непустых клеток. Контроллер собранной машины рисует все клетки
 * на месте скрытых блоков.
 */
public final class AssemblyModels {
    public record Part(int c, int r, int y, ModelResourceLocation off, ModelResourceLocation on) {
    }

    private static final Map<String, List<Part>> PARTS = new HashMap<>();
    public static final ModelResourceLocation GHOST = standalone("block/assembly_ghost");
    public static final ModelResourceLocation GHOST_WRONG = standalone("block/assembly_ghost_wrong");

    private AssemblyModels() {
    }

    private static ModelResourceLocation standalone(String path) {
        return ModelResourceLocation.standalone(ResourceLocation.fromNamespaceAndPath(Kontur.MODID, path));
    }

    /** Читает описания и просит игру загрузить все модели клеток и призрачные кубы. */
    public static void register(ModelEvent.RegisterAdditional event) {
        event.register(GHOST);
        event.register(GHOST_WRONG);
        PARTS.clear();
        for (AssemblyShape shape : AssemblyShape.ALL) {
            List<Part> parts = new ArrayList<>();
            ResourceLocation index = ResourceLocation.fromNamespaceAndPath(Kontur.MODID, "assembly/" + shape.id + ".json");
            Optional<Resource> res = Minecraft.getInstance().getResourceManager().getResource(index);
            if (res.isPresent()) {
                try (Reader reader = res.get().openAsReader()) {
                    JsonObject root = JsonParser.parseReader(reader).getAsJsonObject();
                    JsonArray arr = root.getAsJsonArray("parts");
                    for (JsonElement e : arr) {
                        JsonObject o = e.getAsJsonObject();
                        int c = o.get("c").getAsInt();
                        int r = o.get("r").getAsInt();
                        int y = o.get("y").getAsInt();
                        String base = "block/" + shape.id + "_f" + o.get("i").getAsInt();
                        ModelResourceLocation off = standalone(base);
                        ModelResourceLocation on = o.get("on").getAsBoolean() ? standalone(base + "_on") : off;
                        event.register(off);
                        if (on != off) {
                            event.register(on);
                        }
                        parts.add(new Part(c, r, y, off, on));
                    }
                } catch (Exception ex) {
                    Kontur.LOGGER.error("Не удалось прочитать описание готовой модели {}", shape.id, ex);
                }
            }
            PARTS.put(shape.id, parts);
        }
    }

    public static List<Part> parts(String id) {
        return PARTS.getOrDefault(id, List.of());
    }
}
