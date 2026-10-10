package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.CableBlock;
import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.machine.IoMode;
import dev.technogenesis.kontur.machine.KonturEnergyStorage;
import dev.technogenesis.kontur.machine.MachineDefinition;
import dev.technogenesis.kontur.machine.MachineDefinition.EnergyKind;
import dev.technogenesis.kontur.machine.MachineDefinition.SlotRole;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.machine.MachineTank;
import dev.technogenesis.kontur.machine.RelativeSide;
import dev.technogenesis.kontur.machine.SideConfig;
import dev.technogenesis.kontur.machine.TransferType;
import dev.technogenesis.kontur.menu.MachineMenu;
import dev.technogenesis.kontur.registry.KonturBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.Containers;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.energy.IEnergyStorage;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemHandlerHelper;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.jetbrains.annotations.Nullable;

/**
 * Основа всех машин Контура: слоты, баки, буфер FE, настройка сторон, авто-вывод, диагностика состояния.
 * Принцип безопасной остановки: если чего-то не хватает или нет места под выход, машина стоит и ничего не теряет.
 */
public abstract class MachineBlockEntity extends BlockEntity implements MenuProvider {
    protected final MachineKind kind;
    protected final MachineDefinition def;
    public final MachineInventory inventory;
    public final MachineTank[] tanks;
    public final KonturEnergyStorage energy;
    public final SideConfig sides;

    protected MachineStatus status = MachineStatus.IDLE;
    protected int progress;
    protected int totalTime;

    private final IItemHandler[] itemViews = new IItemHandler[7];
    private final IFluidHandler[] fluidViews = new IFluidHandler[7];
    private final IEnergyStorage[] energyViews = new IEnergyStorage[7];

    protected MachineBlockEntity(MachineKind kind, BlockPos pos, BlockState state) {
        super(KonturBlockEntities.MACHINES.get(kind).get(), pos, state);
        this.kind = kind;
        this.def = kind.definition;
        this.inventory = new MachineInventory(def.slots.size());
        this.tanks = new MachineTank[def.tanks.size()];
        for (int i = 0; i < tanks.length; i++) {
            MachineDefinition.TankDef t = def.tanks.get(i);
            this.tanks[i] = new MachineTank(t.capacity(), t.output(),
                    t.output() ? fs -> true : this::acceptsFluid, this::setChanged);
        }
        this.energy = new KonturEnergyStorage(def.energyCapacity, def.maxReceive, def.maxExtract);
        this.sides = kind.defaultSides();
        for (int i = 0; i < 7; i++) {
            Direction d = i < 6 ? Direction.values()[i] : null;
            itemViews[i] = new ItemView(d);
            fluidViews[i] = new FluidView(d);
            energyViews[i] = new EnergyView(d);
        }
    }

    public MachineKind kind() {
        return kind;
    }

    public MachineStatus status() {
        return status;
    }

    protected Direction facing() {
        return getBlockState().getValue(MachineBlock.FACING);
    }

    protected IoMode mode(TransferType type, @Nullable Direction side) {
        return side == null ? IoMode.ALL : sides.get(type, RelativeSide.of(facing(), side));
    }

    // ------------------------------------------------------------------ правила машины (переопределяются)

    /** Можно ли положить предмет в слот извне (трубы, воронки, игрок). */
    public boolean isItemValidForSlot(int slot, ItemStack stack) {
        MachineDefinition.SlotDef s = def.slots.get(slot);
        return s.role() != SlotRole.OUTPUT && acceptsItem(slot, stack);
    }

    protected boolean acceptsItem(int slot, ItemStack stack) {
        return true;
    }

    protected boolean acceptsFluid(FluidStack stack) {
        return true;
    }

    /** Один тик логики машины (на сервере). */
    protected abstract void tickMachine();

    protected void updateBlockState() {
    }

    protected void saveExtra(CompoundTag tag) {
    }

    protected void loadExtra(CompoundTag tag) {
    }

    /** Дополнительные значения для интерфейса: индексы 5..7. */
    protected void extraSync(int[] data) {
    }

    // ------------------------------------------------------------------ цикл

    public final void serverTick() {
        Level lvl = level;
        if (lvl == null || lvl.isClientSide) {
            return;
        }
        tickMachine();
        pushEnergy();
        if (lvl.getGameTime() % 8 == 0) {
            ejectItems();
            ejectFluids();
        }
        updateBlockState();
    }

    protected final void setStatus(MachineStatus s) {
        this.status = s;
    }

    private void pushEnergy() {
        if (def.energyKind == EnergyKind.CONSUMER || energy.getEnergyStored() <= 0) {
            return;
        }
        for (Direction d : Direction.values()) {
            if (energy.getEnergyStored() <= 0) {
                return;
            }
            if (!mode(TransferType.ENERGY, d).canOutput()) {
                continue;
            }
            BlockPos np = worldPosition.relative(d);
            if (level.getBlockState(np).getBlock() instanceof CableBlock) {
                continue; // кабельная сеть сама забирает энергию
            }
            IEnergyStorage target = level.getCapability(Capabilities.EnergyStorage.BLOCK, np, d.getOpposite());
            if (target == null || !target.canReceive()) {
                continue;
            }
            int offer = Math.min(def.maxExtract, energy.getEnergyStored());
            energy.consume(target.receiveEnergy(offer, false));
        }
    }

    private void ejectItems() {
        if (!sides.ejectItems || !def.hasItems()) {
            return;
        }
        for (Direction d : Direction.values()) {
            if (!mode(TransferType.ITEMS, d).canOutput()) {
                continue;
            }
            IItemHandler target = level.getCapability(Capabilities.ItemHandler.BLOCK, worldPosition.relative(d),
                    d.getOpposite());
            if (target == null) {
                continue;
            }
            for (int slot : def.outputSlots()) {
                ItemStack present = inventory.getStackInSlot(slot);
                if (present.isEmpty()) {
                    continue;
                }
                ItemStack extracted = inventory.extractItem(slot, present.getCount(), true);
                ItemStack rest = ItemHandlerHelper.insertItem(target, extracted.copy(), true);
                int moved = extracted.getCount() - rest.getCount();
                if (moved > 0) {
                    inventory.extractItem(slot, moved, false);
                    ItemHandlerHelper.insertItem(target, extracted.copyWithCount(moved), false);
                }
            }
        }
    }

    private void ejectFluids() {
        if (!sides.ejectFluids || !def.hasFluids()) {
            return;
        }
        for (Direction d : Direction.values()) {
            if (!mode(TransferType.FLUIDS, d).canOutput()) {
                continue;
            }
            IFluidHandler target = level.getCapability(Capabilities.FluidHandler.BLOCK, worldPosition.relative(d),
                    d.getOpposite());
            if (target == null) {
                continue;
            }
            for (MachineTank tank : tanks) {
                if (!tank.output || tank.isEmpty()) {
                    continue;
                }
                FluidStack offer = tank.drain(Math.min(1000, tank.getFluidAmount()), IFluidHandler.FluidAction.SIMULATE);
                int accepted = target.fill(offer, IFluidHandler.FluidAction.SIMULATE);
                if (accepted > 0) {
                    FluidStack drained = tank.drain(accepted, IFluidHandler.FluidAction.EXECUTE);
                    target.fill(drained, IFluidHandler.FluidAction.EXECUTE);
                }
            }
        }
    }

    // ------------------------------------------------------------------ интерфейс

    @Override
    public Component getDisplayName() {
        return getBlockState().getBlock().getName();
    }

    @Nullable
    @Override
    public AbstractContainerMenu createMenu(int id, Inventory inv, Player player) {
        return new MachineMenu(id, inv, this);
    }

    public void fillSyncData(int[] d) {
        d[0] = energy.getEnergyStored();
        d[1] = energy.getMaxEnergyStored();
        d[2] = progress;
        d[3] = totalTime;
        d[4] = status.ordinal();
        extraSync(d);
        d[8] = sides.packA();
        d[9] = sides.packB();
        for (int i = 0; i < tanks.length; i++) {
            FluidStack f = tanks[i].getFluid();
            d[10 + i * 3] = f.isEmpty() ? 0 : BuiltInRegistries.FLUID.getId(f.getFluid());
            d[11 + i * 3] = f.getAmount();
        }
    }

    /** Кнопки интерфейса: 100+ - режим стороны (тип, сторона, направление), 200/201 - авто-вывод. */
    public void handleButton(int id) {
        if (id == 200) {
            sides.ejectItems = !sides.ejectItems;
        } else if (id == 201) {
            sides.ejectFluids = !sides.ejectFluids;
        } else if (id >= 100) {
            int v = id - 100;
            boolean reverse = (v & 1) == 1;
            v >>= 1;
            int side = v % 6;
            int type = v / 6;
            if (type < TransferType.values().length) {
                sides.cycle(TransferType.values()[type], RelativeSide.values()[side], reverse);
            }
        } else {
            return;
        }
        setChanged();
        if (level != null) {
            level.invalidateCapabilities(worldPosition);
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
        }
    }

    // ------------------------------------------------------------------ синхронизация сторон с клиентом
    // (разъёмы на моделях подсвечиваются по настройке сторон)

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        CompoundTag tag = new CompoundTag();
        tag.put("sides", sides.save());
        return tag;
    }

    @Override
    public void handleUpdateTag(CompoundTag tag, HolderLookup.Provider registries) {
        sides.load(tag.getCompound("sides"));
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    public void dropContents() {
        if (level == null) {
            return;
        }
        for (int i = 0; i < inventory.getSlots(); i++) {
            Containers.dropItemStack(level, worldPosition.getX() + 0.5, worldPosition.getY() + 0.5,
                    worldPosition.getZ() + 0.5, inventory.getStackInSlot(i));
        }
    }

    // ------------------------------------------------------------------ сохранение

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.put("inv", inventory.serializeNBT(registries));
        for (int i = 0; i < tanks.length; i++) {
            tag.put("tank" + i, tanks[i].writeToNBT(registries, new CompoundTag()));
        }
        tag.put("energy", energy.serializeNBT(registries));
        tag.put("sides", sides.save());
        tag.putInt("progress", progress);
        tag.putInt("total", totalTime);
        saveExtra(tag);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        inventory.deserializeNBT(registries, tag.getCompound("inv"));
        for (int i = 0; i < tanks.length; i++) {
            tanks[i].readFromNBT(registries, tag.getCompound("tank" + i));
        }
        Tag e = tag.get("energy");
        if (e != null) {
            energy.deserializeNBT(registries, e);
        }
        sides.load(tag.getCompound("sides"));
        progress = tag.getInt("progress");
        totalTime = tag.getInt("total");
        loadExtra(tag);
    }

    // ------------------------------------------------------------------ внутренний инвентарь

    public final class MachineInventory extends ItemStackHandler {
        MachineInventory(int size) {
            super(size);
        }

        @Override
        protected void onContentsChanged(int slot) {
            setChanged();
        }

        /** Роли слотов проверяют боковые обёртки; сама машина вставляет выходы напрямую. */
        @Override
        public boolean isItemValid(int slot, ItemStack stack) {
            return true;
        }
    }

    // ------------------------------------------------------------------ боковые представления (capability)

    @Nullable
    public IItemHandler getItemHandler(@Nullable Direction side) {
        if (!def.hasItems() || mode(TransferType.ITEMS, side) == IoMode.NONE) {
            return null;
        }
        return itemViews[side == null ? 6 : side.ordinal()];
    }

    @Nullable
    public IFluidHandler getFluidHandler(@Nullable Direction side) {
        if (!def.hasFluids() || mode(TransferType.FLUIDS, side) == IoMode.NONE) {
            return null;
        }
        return fluidViews[side == null ? 6 : side.ordinal()];
    }

    @Nullable
    public IEnergyStorage getEnergyStorage(@Nullable Direction side) {
        if (def.energyCapacity <= 0 || mode(TransferType.ENERGY, side) == IoMode.NONE) {
            return null;
        }
        return energyViews[side == null ? 6 : side.ordinal()];
    }

    private final class ItemView implements IItemHandler {
        private final Direction side;

        ItemView(Direction side) {
            this.side = side;
        }

        @Override
        public int getSlots() {
            return inventory.getSlots();
        }

        @Override
        public ItemStack getStackInSlot(int slot) {
            return inventory.getStackInSlot(slot);
        }

        @Override
        public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) {
            if (!mode(TransferType.ITEMS, side).canInput() || !isItemValidForSlot(slot, stack)) {
                return stack;
            }
            return inventory.insertItem(slot, stack, simulate);
        }

        @Override
        public ItemStack extractItem(int slot, int amount, boolean simulate) {
            if (!mode(TransferType.ITEMS, side).canOutput() || def.slots.get(slot).role() != SlotRole.OUTPUT) {
                return ItemStack.EMPTY;
            }
            return inventory.extractItem(slot, amount, simulate);
        }

        @Override
        public int getSlotLimit(int slot) {
            return inventory.getSlotLimit(slot);
        }

        @Override
        public boolean isItemValid(int slot, ItemStack stack) {
            return mode(TransferType.ITEMS, side).canInput() && isItemValidForSlot(slot, stack);
        }
    }

    private final class FluidView implements IFluidHandler {
        private final Direction side;

        FluidView(Direction side) {
            this.side = side;
        }

        @Override
        public int getTanks() {
            return tanks.length;
        }

        @Override
        public FluidStack getFluidInTank(int tank) {
            return tanks[tank].getFluid();
        }

        @Override
        public int getTankCapacity(int tank) {
            return tanks[tank].getCapacity();
        }

        @Override
        public boolean isFluidValid(int tank, FluidStack stack) {
            return !tanks[tank].output && mode(TransferType.FLUIDS, side).canInput() && tanks[tank].isFluidValid(stack);
        }

        @Override
        public int fill(FluidStack resource, FluidAction action) {
            if (!mode(TransferType.FLUIDS, side).canInput() || resource.isEmpty()) {
                return 0;
            }
            for (MachineTank tank : tanks) {
                if (!tank.output && tank.isFluidValid(resource)
                        && (tank.isEmpty() || FluidStack.isSameFluidSameComponents(tank.getFluid(), resource))) {
                    return tank.fill(resource, action);
                }
            }
            return 0;
        }

        @Override
        public FluidStack drain(FluidStack resource, FluidAction action) {
            if (!mode(TransferType.FLUIDS, side).canOutput() || resource.isEmpty()) {
                return FluidStack.EMPTY;
            }
            for (MachineTank tank : tanks) {
                if (tank.output && FluidStack.isSameFluidSameComponents(tank.getFluid(), resource)) {
                    return tank.drain(resource, action);
                }
            }
            return FluidStack.EMPTY;
        }

        @Override
        public FluidStack drain(int maxDrain, FluidAction action) {
            if (!mode(TransferType.FLUIDS, side).canOutput()) {
                return FluidStack.EMPTY;
            }
            for (MachineTank tank : tanks) {
                if (tank.output && !tank.isEmpty()) {
                    return tank.drain(maxDrain, action);
                }
            }
            return FluidStack.EMPTY;
        }
    }

    private final class EnergyView implements IEnergyStorage {
        private final Direction side;

        EnergyView(Direction side) {
            this.side = side;
        }

        @Override
        public int receiveEnergy(int toReceive, boolean simulate) {
            if (!canReceive()) {
                return 0;
            }
            return energy.receiveEnergy(toReceive, simulate);
        }

        @Override
        public int extractEnergy(int toExtract, boolean simulate) {
            if (!canExtract()) {
                return 0;
            }
            return energy.extractEnergy(toExtract, simulate);
        }

        @Override
        public int getEnergyStored() {
            return energy.getEnergyStored();
        }

        @Override
        public int getMaxEnergyStored() {
            return energy.getMaxEnergyStored();
        }

        @Override
        public boolean canExtract() {
            return def.maxExtract > 0 && mode(TransferType.ENERGY, side).canOutput();
        }

        @Override
        public boolean canReceive() {
            return def.maxReceive > 0 && mode(TransferType.ENERGY, side).canInput();
        }
    }
}
