package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.FusionStructure;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturFluids;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;

/**
 * Термоядерный реактор: контроллер собранной игроком коробки (см. FusionStructure). Работает, только если коробка цела:
 * схема проверяется раз в секунду. 8000 FE/t за 40 мБ водорода и 20 мБ плазмы в тик. Топливо и плазма подаются
 * по газовым трубам в любой порт корпуса, энергию отдаёт любой порт (и сам контроллер).
 */
public class FusionReactorBlockEntity extends MachineBlockEntity {
    public static final int OUTPUT_PER_TICK = 8000;
    public static final int HYDROGEN_PER_TICK = 40;
    public static final int PLASMA_PER_TICK = 20;

    private boolean formed;
    private MachineStatus structure = MachineStatus.NOT_CHECKED;
    private List<BlockPos> ports = List.of();

    public FusionReactorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.FUSION_REACTOR, pos, state);
    }

    public boolean isFormed() {
        return formed;
    }

    @Override
    protected boolean acceptsFluid(FluidStack stack) {
        return stack.getFluid() == KonturFluids.HYDROGEN.source.get() || stack.getFluid() == KonturFluids.PLASMA.source.get();
    }

    private void revalidate() {
        FusionStructure.Result r = FusionStructure.check(level, worldPosition, facing());
        structure = r.status() == null ? MachineStatus.IDLE : r.status();
        formed = r.formed();
        ports = r.ports();
        for (BlockPos p : ports) {
            if (level.getBlockEntity(p) instanceof FusionPortBlockEntity port) {
                port.setController(worldPosition);
            }
        }
    }

    private int tankWith(net.minecraft.world.level.material.Fluid fluid) {
        for (int i = 0; i < tanks.length; i++) {
            if (tanks[i].getFluid().getFluid() == fluid) {
                return i;
            }
        }
        return -1;
    }

    @Override
    protected void tickMachine() {
        if (structure == MachineStatus.NOT_CHECKED || phaseTick(20)) {
            revalidate();
        }
        if (!formed) {
            setStatus(structure);
            return;
        }
        int h = tankWith(KonturFluids.HYDROGEN.source.get());
        int p = tankWith(KonturFluids.PLASMA.source.get());
        if (h < 0 || p < 0 || tanks[h].getFluidAmount() < HYDROGEN_PER_TICK || tanks[p].getFluidAmount() < PLASMA_PER_TICK) {
            setStatus(MachineStatus.NO_FLUID);
            return;
        }
        if (energy.space() < OUTPUT_PER_TICK) {
            setStatus(MachineStatus.FULL);
            return;
        }
        energy.produce(OUTPUT_PER_TICK);
        tanks[h].drain(HYDROGEN_PER_TICK, FluidAction.EXECUTE);
        tanks[p].drain(PLASMA_PER_TICK, FluidAction.EXECUTE);
        setStatus(MachineStatus.RUNNING);
        setChanged();
    }

    @Override
    protected void extraSync(int[] data) {
        data[7] = status == MachineStatus.RUNNING ? OUTPUT_PER_TICK : 0;
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        if (getBlockState().getValue(MachineBlock.ACTIVE) != active) {
            setActive(active);
        }
    }
}
