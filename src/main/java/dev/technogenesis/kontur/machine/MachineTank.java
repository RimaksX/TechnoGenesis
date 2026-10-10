package dev.technogenesis.kontur.machine;

import java.util.function.Predicate;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

/** Бак машины. Выходные баки принимают жидкость только изнутри, наружу доступны лишь для слива. */
public class MachineTank extends FluidTank {
    public final boolean output;
    private final Runnable onChange;

    public MachineTank(int capacity, boolean output, Predicate<FluidStack> filter, Runnable onChange) {
        super(capacity, filter);
        this.output = output;
        this.onChange = onChange;
    }

    @Override
    protected void onContentsChanged() {
        onChange.run();
    }
}
