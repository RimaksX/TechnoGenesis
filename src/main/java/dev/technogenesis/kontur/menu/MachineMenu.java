package dev.technogenesis.kontur.menu;

import dev.technogenesis.kontur.blockentity.MachineBlockEntity;
import dev.technogenesis.kontur.item.ModuleItem;
import dev.technogenesis.kontur.machine.MachineDefinition;
import dev.technogenesis.kontur.machine.MachineDefinition.SlotDef;
import dev.technogenesis.kontur.machine.MachineDefinition.SlotRole;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.registry.KonturBlocks;
import dev.technogenesis.kontur.registry.KonturMenus;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.items.SlotItemHandler;
import org.jetbrains.annotations.Nullable;

/**
 * Универсальное меню машины. Значения для экрана (энергия, прогресс, жидкости, стороны) синхронизируются
 * 32-битными числами через пары 16-битных DataSlot: ванильный пакет передаёт только short.
 */
public class MachineMenu extends AbstractContainerMenu {
    public static final int SYNC_SIZE = 20;
    public static final int PLAYER_INV_Y = 102;

    public final MachineKind kind;
    public final MachineDefinition def;
    public final BlockPos pos;
    @Nullable
    private final MachineBlockEntity be;
    private final ContainerLevelAccess access;
    private final int[] sync = new int[SYNC_SIZE];

    /** Серверный конструктор. */
    public MachineMenu(int id, Inventory inv, MachineBlockEntity be) {
        this(id, inv, be.kind(), be.getBlockPos(), be, be.inventory);
    }

    public static MachineMenu fromNetwork(int id, Inventory inv, FriendlyByteBuf buf) {
        MachineKind kind = buf.readEnum(MachineKind.class);
        BlockPos pos = buf.readBlockPos();
        return new MachineMenu(id, inv, kind, pos, null, new ItemStackHandler(kind.definition.slots.size()));
    }

    private MachineMenu(int id, Inventory inv, MachineKind kind, BlockPos pos, @Nullable MachineBlockEntity be,
                        IItemHandler handler) {
        super(KonturMenus.MACHINE.get(), id);
        this.kind = kind;
        this.def = kind.definition;
        this.pos = pos;
        this.be = be;
        this.access = be != null && be.getLevel() != null ? ContainerLevelAccess.create(be.getLevel(), pos)
                : ContainerLevelAccess.NULL;

        for (int i = 0; i < def.slots.size(); i++) {
            SlotDef s = def.slots.get(i);
            addSlot(new MachineSlot(handler, i, s.x(), s.y(), s.role()));
        }
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 9; col++) {
                addSlot(new Slot(inv, col + row * 9 + 9, 8 + col * 18, PLAYER_INV_Y + row * 18));
            }
        }
        for (int col = 0; col < 9; col++) {
            addSlot(new Slot(inv, col, 8 + col * 18, PLAYER_INV_Y + 58));
        }
        for (int i = 0; i < SYNC_SIZE; i++) {
            final int idx = i;
            addDataSlot(new DataSlot() {
                @Override
                public int get() {
                    return sync[idx] & 0xFFFF;
                }

                @Override
                public void set(int value) {
                    sync[idx] = (sync[idx] & 0xFFFF0000) | (value & 0xFFFF);
                }
            });
            addDataSlot(new DataSlot() {
                @Override
                public int get() {
                    return sync[idx] >>> 16;
                }

                @Override
                public void set(int value) {
                    sync[idx] = (sync[idx] & 0xFFFF) | ((value & 0xFFFF) << 16);
                }
            });
        }
        if (be != null) {
            be.fillSyncData(sync);
        }
    }

    private final class MachineSlot extends SlotItemHandler {
        private final SlotRole role;

        MachineSlot(IItemHandler handler, int index, int x, int y, SlotRole role) {
            super(handler, index, x, y);
            this.role = role;
        }

        @Override
        public int getMaxStackSize() {
            return role == SlotRole.MODULE || role == SlotRole.COATING || role == SlotRole.COOLER ? 1
                    : super.getMaxStackSize();
        }

        @Override
        public boolean mayPlace(ItemStack stack) {
            if (role == SlotRole.OUTPUT) {
                return false;
            }
            if (role == SlotRole.MODULE) {
                return stack.getItem() instanceof ModuleItem;
            }
            if (role == SlotRole.COATING) {
                return stack.getItem() instanceof dev.technogenesis.kontur.item.CoatingItem;
            }
            if (role == SlotRole.COOLER) {
                return stack.getItem() instanceof dev.technogenesis.kontur.item.RadiatorItem;
            }
            return be == null || be.isItemValidForSlot(getSlotIndex(), stack);
        }
    }

    @Override
    public void broadcastChanges() {
        if (be != null) {
            be.fillSyncData(sync);
        }
        super.broadcastChanges();
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        Slot slot = slots.get(index);
        if (slot == null || !slot.hasItem()) {
            return ItemStack.EMPTY;
        }
        ItemStack stack = slot.getItem();
        ItemStack copy = stack.copy();
        int machineCount = def.slots.size();
        if (index < machineCount) {
            if (!moveItemStackTo(stack, machineCount, slots.size(), true)) {
                return ItemStack.EMPTY;
            }
        } else {
            boolean moved = false;
            for (int i = 0; i < machineCount && !moved; i++) {
                if (def.slots.get(i).role() != SlotRole.OUTPUT) {
                    moved = moveItemStackTo(stack, i, i + 1, false);
                }
            }
            if (!moved) {
                if (index < machineCount + 27) {
                    if (!moveItemStackTo(stack, machineCount + 27, machineCount + 36, false)) {
                        return ItemStack.EMPTY;
                    }
                } else if (!moveItemStackTo(stack, machineCount, machineCount + 27, false)) {
                    return ItemStack.EMPTY;
                }
            }
        }
        if (stack.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        if (stack.getCount() == copy.getCount()) {
            return ItemStack.EMPTY;
        }
        slot.onTake(player, stack);
        return copy;
    }

    @Override
    public boolean stillValid(Player player) {
        return stillValid(access, player, KonturBlocks.MACHINES.get(kind).get());
    }

    // ------------------------------------------------------------------ значения для экрана

    public int energy() {
        return sync[0];
    }

    public int energyCapacity() {
        return sync[1] > 0 ? sync[1] : def.energyCapacity;
    }

    public int progress() {
        return sync[2];
    }

    public int totalTime() {
        return sync[3];
    }

    public MachineStatus status() {
        int o = sync[4];
        return o >= 0 && o < MachineStatus.values().length ? MachineStatus.values()[o] : MachineStatus.IDLE;
    }

    /** Множитель скорости от модуля (1, если модуля нет). */
    public int moduleSpeed() {
        return def.hasModule() ? Math.max(1, sync[8]) : 1;
    }

    public int moduleEnergyPercent() {
        return def.hasModule() && sync[9] > 0 ? sync[9] : 100;
    }

    /** Нагрев модуля в процентах от предела. */
    public int heatPercent() {
        return def.hasModule() ? sync[16] : 0;
    }

    /** Остывание за тик: собственное плюс радиатор плюс вода, лёд или снег рядом. */
    public int cooling() {
        return sync[12];
    }

    public boolean overheated() {
        return def.hasModule() && sync[15] != 0;
    }

    public int burnLeft() {
        return sync[5];
    }

    public int burnTotal() {
        return sync[6];
    }

    public int rate() {
        return sync[7];
    }

    public FluidStack fluid(int tank) {
        int id = sync[10 + tank * 3];
        int amount = sync[11 + tank * 3];
        Fluid f = id == 0 ? Fluids.EMPTY : BuiltInRegistries.FLUID.byId(id);
        return f == Fluids.EMPTY || amount <= 0 ? FluidStack.EMPTY : new FluidStack(f, amount);
    }


}
