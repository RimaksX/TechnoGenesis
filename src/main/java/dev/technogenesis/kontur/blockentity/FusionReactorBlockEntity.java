package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.AssemblyShape;
import dev.technogenesis.kontur.machine.AssemblyTracker;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.machine.ModuleTier;
import dev.technogenesis.kontur.registry.KonturFluids;
import dev.technogenesis.kontur.registry.KonturItems;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Термоядерный реактор: контроллер собранной игроком коробки 5 x 5 x 4 (см. AssemblyShape). Сам тока не даёт, он греет воду:
 * горение (40 мБ водорода и 20 мБ плазмы в тик, литиевый стержень на 6000 тиков, 600 FE/t на магнитные катушки) выделяет
 * 10 единиц тепла в тик, вода охлаждает стенки и превращается в пар - до 100 мБ/т (мБ воды снимает 0,1 тепла). Пар по
 * газовым трубам идёт в паротурбинный зал, конденсат из него - в градирню, а вода возвращается в реактор. Если воды мало
 * или пару некуда деться (бак пара полон), температура растёт; при 1000 реактор глушится (аварийная остановка, без
 * взрыва) и включается снова, остыв до 400.
 */
public class FusionReactorBlockEntity extends MachineBlockEntity implements AssemblyController {
    public static final int HYDROGEN_PER_TICK = 40;
    public static final int PLASMA_PER_TICK = 20;
    public static final int ENERGY_PER_TICK = 600;
    public static final int ROD_BURN_TICKS = 6000;
    public static final int HEAT_PER_TICK = 10;
    public static final int WATER_PER_TICK = 100;
    /** Сколько мБ воды уносит одну единицу тепла. */
    public static final int WATER_PER_HEAT = 10;
    public static final int IDLE_COOLING = 2;

    private static final int STEAM_TANK = 3;

    private final AssemblyTracker tracker = new AssemblyTracker(AssemblyShape.FUSION);
    private int rodLeft;

    public FusionReactorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.FUSION_REACTOR, pos, state);
    }

    @Override
    public boolean isFormed() {
        return tracker.formed();
    }

    @Override
    protected boolean acceptsItem(int slot, ItemStack stack) {
        return stack.is(KonturItems.LITHIUM_ROD.get());
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        Fluid f = stack.getFluid();
        return f == KonturFluids.HYDROGEN.source.get() || f == KonturFluids.PLASMA.source.get() || isWater(f);
    }

    @Override
    protected boolean interchangeable(FluidStack a, FluidStack b) {
        return isWater(a.getFluid()) && isWater(b.getFluid());
    }

    private static boolean isWater(Fluid f) {
        return f == Fluids.WATER || f == KonturFluids.TECHNICAL_WATER.source.get();
    }

    private int inputWith(java.util.function.Predicate<Fluid> test) {
        for (int i = 0; i < STEAM_TANK; i++) {
            if (!tanks[i].isEmpty() && test.test(tanks[i].getFluid().getFluid())) {
                return i;
            }
        }
        return -1;
    }

    @Override
    protected void tickMachine() {
        if (tracker.needsCheck() || phaseTick(20)) {
            tracker.revalidate(level, worldPosition, facing());
        }
        if (!tracker.formed()) {
            heat = Math.max(0, heat - IDLE_COOLING);
            setStatus(tracker.status());
            return;
        }
        boolean burning = false;
        MachineStatus problem = MachineStatus.RUNNING;
        if (overheated) {
            problem = MachineStatus.SCRAM;                           // аварийная остановка: ждём остывания
        } else if (rodLeft <= 0 && inventory.getStackInSlot(0).isEmpty()) {
            problem = MachineStatus.NO_FUEL;
        } else {
            int h = inputWith(f -> f == KonturFluids.HYDROGEN.source.get());
            int p = inputWith(f -> f == KonturFluids.PLASMA.source.get());
            if (h < 0 || p < 0 || tanks[h].getFluidAmount() < HYDROGEN_PER_TICK || tanks[p].getFluidAmount() < PLASMA_PER_TICK) {
                problem = MachineStatus.NO_FLUID;
            } else if (energy.getEnergyStored() < ENERGY_PER_TICK) {
                problem = MachineStatus.NO_ENERGY;
            } else {
                if (rodLeft <= 0) {
                    ItemStack rod = inventory.getStackInSlot(0);
                    rod.shrink(1);
                    if (rod.isEmpty()) {
                        inventory.setStackInSlot(0, ItemStack.EMPTY);
                    }
                    rodLeft = ROD_BURN_TICKS;
                }
                energy.consume(ENERGY_PER_TICK);
                tanks[h].drain(HYDROGEN_PER_TICK, FluidAction.EXECUTE);
                tanks[p].drain(PLASMA_PER_TICK, FluidAction.EXECUTE);
                rodLeft--;
                heat += HEAT_PER_TICK;
                burning = true;
            }
        }
        // охлаждение: вода уносит тепло и становится паром, пока есть куда девать пар
        int w = inputWith(FusionReactorBlockEntity::isWater);
        if (heat > 0 && w >= 0) {
            int space = tanks[STEAM_TANK].getCapacity() - tanks[STEAM_TANK].getFluidAmount();
            int flow = Math.min(WATER_PER_TICK, Math.min(tanks[w].getFluidAmount(), space));
            int heatNeeded = (heat * WATER_PER_HEAT);
            flow = Math.min(flow, heatNeeded);
            if (flow > 0) {
                tanks[w].drain(flow, FluidAction.EXECUTE);
                tanks[STEAM_TANK].fill(new FluidStack(KonturFluids.STEAM.source.get(), flow), FluidAction.EXECUTE);
                heat -= flow / WATER_PER_HEAT;
            }
        }
        if (!burning) {
            heat = Math.max(0, heat - IDLE_COOLING);
        }
        if (heat >= ModuleTier.HEAT_MAX) {
            heat = ModuleTier.HEAT_MAX;
            overheated = true;
        } else if (overheated && heat <= ModuleTier.HEAT_RESUME) {
            overheated = false;
        }
        boolean dry = w < 0 || tanks[w].isEmpty();
        setStatus(burning ? (dry && heat >= HEAT_PER_TICK ? MachineStatus.NO_WATER : MachineStatus.RUNNING) : problem);
        setChanged();
    }

    @Override
    protected void extraSync(int[] data) {
        data[5] = rodLeft;
        data[6] = ROD_BURN_TICKS;
        data[7] = 0;
    }

    @Override
    protected void saveExtra(CompoundTag tag) {
        tag.putInt("rodLeft", rodLeft);
        tag.putInt("coreHeat", heat);
        tag.putBoolean("scram", overheated);
    }

    @Override
    protected void loadExtra(CompoundTag tag) {
        rodLeft = tag.getInt("rodLeft");
        heat = tag.getInt("coreHeat");
        overheated = tag.getBoolean("scram");
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING || shown == MachineStatus.NO_WATER && heat > 0;
        if (getBlockState().getValue(MachineBlock.ACTIVE) != active) {
            setActive(active);
        }
    }
}
