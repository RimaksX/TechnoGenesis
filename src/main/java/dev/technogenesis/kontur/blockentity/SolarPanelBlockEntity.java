package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.item.CoatingItem;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Солнечная панель (базовая и улучшенная). Работает только при чистом небе над панелью и дневном свете: ночью, в
 * подземелье и в мирах без неба стоит. Пик у ясного полдня, дождь убирает около четверти, гроза около сорока
 * процентов. Улучшенная панель принимает покрытие, которое поднимает выработку до 120, 150 или 200%.
 */
public class SolarPanelBlockEntity extends PassiveGeneratorBlockEntity {
    private boolean skyClear;

    public SolarPanelBlockEntity(MachineKind kind, BlockPos pos, BlockState state) {
        super(kind, pos, state);
    }

    /** Доля солнца 0..1 для места pos: ясный день 1, ночь 0, дождь и гроза меньше. */
    public static float sunFactor(net.minecraft.world.level.Level level, BlockPos above) {
        int sky = level.getBrightness(net.minecraft.world.level.LightLayer.SKY, above);
        return Math.max(0f, Math.min(1f, (sky - level.getSkyDarken() - 4) / 11f));
    }

    /** Эффективность покрытия в процентах (100 без покрытия). */
    protected int coatingPercent() {
        int slot = def.coatingSlot();
        if (slot >= 0) {
            ItemStack stack = inventory.getStackInSlot(slot);
            if (stack.getItem() instanceof CoatingItem c) {
                return c.tier().percent;
            }
        }
        return 100;
    }

    /** Доля плиток с чистым небом 0..1 (у одиночной панели 0 или 1). */
    protected float clearShare() {
        return skyClear ? 1f : 0f;
    }

    protected void refreshSky() {
        skyClear = level.canSeeSky(worldPosition.above());
    }

    @Override
    protected int output() {
        if (!level.dimensionType().hasSkyLight()) {
            setStatus(MachineStatus.NO_SUN);
            return 0;
        }
        if (level.getGameTime() % 20 == 0 || (rate == 0 && level.getGameTime() % 5 == 0)) {
            refreshSky();
        }
        float share = clearShare();
        if (share <= 0f) {
            setStatus(MachineStatus.NO_SKY);
            return 0;
        }
        float sun = sunFactor(level, worldPosition.above());
        if (sun <= 0f) {
            setStatus(MachineStatus.NO_SUN);
            return 0;
        }
        return Math.max(1, Math.round(def.ratePerTick * sun * share * coatingPercent() / 100f));
    }
}
