package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturItems;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Твердотопливный электрогенератор: 128 FE/t. Топливо горит в 8 раз быстрее печи, поэтому 1 уголь = 200 тиков
 * = 25 600 FE. Часть топлива оставляет золу; если её некуда выгрузить, генератор не начинает новое горение.
 * Если буфер полон, топливо не расходуется.
 */
public class SolidFuelGeneratorBlockEntity extends MachineBlockEntity {
    public static final int OUTPUT_PER_TICK = 128;
    public static final int BURN_SPEEDUP = 8;
    public static final float ASH_CHANCE = 0.25f;

    private static final int FUEL_SLOT = 0;
    private static final int ASH_SLOT = 1;

    private int burnLeft;
    private int burnTotal;

    public SolidFuelGeneratorBlockEntity(BlockPos pos, BlockState state) {
        this(MachineKind.SOLID_FUEL_GENERATOR, pos, state);
    }

    protected SolidFuelGeneratorBlockEntity(MachineKind kind, BlockPos pos, BlockState state) {
        super(kind, pos, state);
    }

    /** Выработка за тик при единичной скорости. */
    protected int outputPerTick() {
        return OUTPUT_PER_TICK;
    }

    /** Во сколько раз топливо горит быстрее печи. */
    protected int burnSpeedup() {
        return BURN_SPEEDUP;
    }

    /** Дополнительное условие работы (например, вода); при отказе подкласс сам выставляет статус. */
    protected boolean ready(int speed) {
        return true;
    }

    /** Расход ресурсов на тик работы. */
    protected void consume(int speed) {
    }

    @Override
    protected boolean acceptsItem(int slot, ItemStack stack) {
        return slot == FUEL_SLOT && stack.getBurnTime(RecipeType.SMELTING) > 0;
    }

    @Override
    protected void tickMachine() {
        if (burnLeft <= 0) {
            ItemStack fuel = inventory.getStackInSlot(FUEL_SLOT);
            int burn = fuel.isEmpty() ? 0 : fuel.getBurnTime(RecipeType.SMELTING);
            if (burn <= 0) {
                setStatus(MachineStatus.NO_FUEL);
                return;
            }
            if (energy.space() < outputPerTick() * activeSpeed()) {
                setStatus(MachineStatus.FULL);
                return;
            }
            ItemStack ashStack = new ItemStack(KonturItems.ASH.get());
            // место под золу нужно всегда: безопасная остановка вместо потери побочного продукта
            if (!inventory.insertItem(ASH_SLOT, ashStack, true).isEmpty()) {
                setStatus(MachineStatus.OUTPUT_FULL);
                return;
            }
            boolean ash = burn >= 200 && level.random.nextFloat() < ASH_CHANCE;
            ItemStack remainder = fuel.getCraftingRemainingItem();
            fuel.shrink(1);
            if (fuel.isEmpty()) {
                inventory.setStackInSlot(FUEL_SLOT, ItemStack.EMPTY);
            }
            if (!remainder.isEmpty()) {
                // пустое ведро и подобное уходит в выход, а не залипает в слоте топлива
                ItemStack left = inventory.insertItem(ASH_SLOT, remainder, false);
                if (!left.isEmpty()) {
                    net.minecraft.world.level.block.Block.popResource(level, worldPosition, left);
                }
            }
            if (ash) {
                inventory.insertItem(ASH_SLOT, ashStack, false);
            }
            burnTotal = Math.max(1, burn / burnSpeedup());
            burnLeft = burnTotal;
            setChanged();
        }
        // модуль форсирования: горит и вырабатывает в speed раз быстрее, на единицу топлива энергии столько же
        int speed = Math.max(1, Math.min(activeSpeed(), burnLeft));
        int output = outputPerTick() * speed;
        if (!ready(speed)) {
            return;
        }
        if (energy.space() < output) {
            setStatus(MachineStatus.FULL);
            return;
        }
        energy.produce(output);
        consume(speed);
        burnLeft -= speed;
        setStatus(MachineStatus.RUNNING);
        setChanged();
    }

    @Override
    protected void extraSync(int[] data) {
        data[5] = burnLeft;
        data[6] = burnTotal;
        data[7] = status == MachineStatus.RUNNING ? outputPerTick() * activeSpeed() : 0;
    }

    @Override
    protected void saveExtra(CompoundTag tag) {
        tag.putInt("burnLeft", burnLeft);
        tag.putInt("burnTotal", burnTotal);
    }

    @Override
    protected void loadExtra(CompoundTag tag) {
        burnLeft = tag.getInt("burnLeft");
        burnTotal = tag.getInt("burnTotal");
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        BlockState state = getBlockState();
        if (state.getValue(MachineBlock.ACTIVE) != active) {
            level.setBlock(worldPosition, state.setValue(MachineBlock.ACTIVE, active), 3);
        }
    }
}
