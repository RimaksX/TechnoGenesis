package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FluidState;

/**
 * Тепловой генератор: лава под блоком и вода сбоку. 120 FE/t за каждую из четырёх боковых граней, касающуюся воды,
 * то есть от 120 до 480 FE/t. Лава остывает: раз в минуту с шансом 1 к 20 лавовый исток под генератором превращается
 * в обсидиан, поэтому в среднем один исток живёт около 20 минут и его надо возобновлять.
 */
public class ThermalGeneratorBlockEntity extends PassiveGeneratorBlockEntity {
    public static final int PER_WATER_SIDE = 120;
    private static final int COOL_INTERVAL = 1200;
    private static final int COOL_CHANCE = 20;

    private int waterSides;
    private boolean lava;

    public ThermalGeneratorBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.THERMAL_GENERATOR, pos, state);
    }

    private void scan() {
        FluidState below = level.getFluidState(worldPosition.below());
        lava = below.is(FluidTags.LAVA);
        int n = 0;
        for (Direction d : Direction.Plane.HORIZONTAL) {
            if (level.getFluidState(worldPosition.relative(d)).is(FluidTags.WATER)) {
                n++;
            }
        }
        waterSides = n;
    }

    @Override
    protected int output() {
        if (level.getGameTime() % 10 == 0) {
            scan();
        }
        if (!lava || waterSides == 0) {
            setStatus(MachineStatus.NO_HEAT);
            return 0;
        }
        if (level.getGameTime() % COOL_INTERVAL == 0 && level.random.nextInt(COOL_CHANCE) == 0) {
            BlockPos under = worldPosition.below();
            if (level.getFluidState(under).isSource()) {
                level.setBlockAndUpdate(under, Blocks.OBSIDIAN.defaultBlockState());
            }
        }
        return PER_WATER_SIDE * waterSides;
    }
}
