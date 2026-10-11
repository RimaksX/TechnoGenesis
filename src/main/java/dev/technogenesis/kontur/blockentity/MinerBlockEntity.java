package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.block.MachineBlock;
import dev.technogenesis.kontur.item.DrillTipItem;
import dev.technogenesis.kontur.machine.DrillTier;
import dev.technogenesis.kontur.machine.MachineKind;
import dev.technogenesis.kontur.machine.MachineStatus;
import dev.technogenesis.kontur.miner.MinerFrame;
import dev.technogenesis.kontur.miner.MinerPath;
import dev.technogenesis.kontur.miner.MinerScan;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemHandlerHelper;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.jetbrains.annotations.Nullable;

/**
 * Автоматический шахтёр. Ядро стоит в углу рамки из направляющих лицом наружу; перед ним (лицевая грань) лежит склад
 * наконечников. Головка ездит по рамке, как печатающая головка 3D-принтера, и снимает область слоями сверху вниз змейкой:
 * едет к блоку, ломает, добыча уходит в буфер ядра. Наконечник стирается по твёрдости блоков; сломался - головка едет к
 * ядру, берёт новый из склада и возвращается к тому же блоку. Рамка, склад, бедрок и блоки с инвентарём не ломаются.
 * Работает только в загруженных чанках. Положение головки хранится в сохранении.
 */
public class MinerBlockEntity extends MachineBlockEntity {
    public static final int MAX_OUTER = 50;
    /** Высота головки (наконечник и корпус) и низ каретки над уровнем рамки. */
    public static final double HEAD_H = 0.625;
    public static final double CARRIAGE_BOTTOM = 0.5;
    private static final double MOVE_SPEED = 0.35;
    private static final int ENERGY_MOVE = 60;
    private static final int ENERGY_MINE = 160;
    private static final int SCAN_IDLE = 20;
    private static final int SCAN_BUSY = 100;
    private static final int FETCH_TICKS = 20;

    private enum Phase { SELECT, MOVE, MINE, HOME, FETCH }

    // --- рабочее состояние (сохраняется)
    private Phase phase = Phase.SELECT;
    private int layer;
    private int cell;
    private Vec3 head = Vec3.ZERO;
    private boolean headSet;
    private boolean viaPlane = true;
    private Vec3 target = Vec3.ZERO;
    private BlockPos mining;
    private int mineProgress;
    private int crackStage = -1;
    private int mineTotal;
    private int fetchTimer;
    private int noTipWait;
    private ItemStack tip = ItemStack.EMPTY;
    private MinerFrame workFrame;

    // --- проверка постройки
    private MinerScan scan;
    private long lastScan = Long.MIN_VALUE;
    private boolean depotOk;
    private boolean syncDirty;
    /** Постройка проверена ключом: только после этого появляется каретка и начинается работа. */
    private boolean verified;
    private boolean viewVerified;

    // --- то, что видит клиент
    private MinerScan viewScan;
    private MinerScan clientScan;
    private long clientScanTime;
    private boolean viewDepot;
    private Vec3 syncHead = Vec3.ZERO;
    private Vec3 syncTarget = Vec3.ZERO;
    private boolean syncVia;
    private boolean syncMoving;
    private boolean syncMining;
    private double syncSpeed;
    private long syncTime;
    private int syncTip;
    /** Только клиент: накопленный угол вращения бура и время последней отрисовки. */
    public float drillAngle;
    public float lastRenderTick;

    public MinerBlockEntity(BlockPos pos, BlockState state) {
        super(MachineKind.MINER, pos, state);
    }

    // ------------------------------------------------------------------ геометрия

    private MinerFrame frame() {
        return scan == null ? null : scan.frame;
    }

    private double planeTipY(MinerFrame f) {
        return f.y() + CARRIAGE_BOTTOM - HEAD_H;     // верх головки вплотную к низу каретки
    }

    /** Стоянка: клетка внутри рамки по диагонали от ядра, чтобы каретка не стояла внутри модели самого ядра. */
    private Vec3 home(MinerFrame f) {
        int dx = worldPosition.getX() <= f.minX() ? 1 : -1;
        int dz = worldPosition.getZ() <= f.minZ() ? 1 : -1;
        return new Vec3(worldPosition.getX() + dx + 0.5, planeTipY(f), worldPosition.getZ() + dz + 0.5);
    }

    /** Мировые координаты клетки слоя по номеру: змейка, чётные строки слева направо, нечётные обратно. */
    private BlockPos cellPos(MinerFrame f, int index) {
        int w = f.innerWidth();
        int row = index / w;
        int col = index % w;
        int xi = (row & 1) == 0 ? col : w - 1 - col;
        return new BlockPos(f.minX() + 1 + xi, f.y() - 1 - layer, f.minZ() + 1 + row);
    }

    // ------------------------------------------------------------------ цикл

    @Override
    protected void tickMachine() {
        long now = level.getGameTime();
        boolean busy = phase == Phase.MOVE || phase == Phase.MINE;
        if (scan == null || now - lastScan >= (busy ? SCAN_BUSY : SCAN_IDLE)) {
            rescan(now);
        }
        if (scan.error != MinerScan.Error.NONE) {
            if (verified) {                      // рамку сломали: проверку нужно пройти заново
                verified = false;
                syncDirty = true;
                setChanged();
            }
            clearCracks();
            setStatus(frameStatus(scan.error));
            finishTick(now);
            return;
        }
        if (!verified) {                         // собран, но проверка ключом ещё не пройдена: каретки нет, работы нет
            clearCracks();
            setStatus(MachineStatus.NOT_CHECKED);
            finishTick(now);
            return;
        }
        MinerFrame f = scan.frame;
        if (!f.equals(workFrame)) {              // рамку перестроили: начинаем область сначала
            workFrame = f;
            layer = 0;
            cell = 0;
            phase = Phase.SELECT;
            viaPlane = true;
            head = home(f);
            headSet = true;
            syncDirty = true;
            setChanged();
        }
        if (scan.unloaded) {
            setStatus(MachineStatus.UNLOADED);
            finishTick(now);
            return;
        }
        if (!headSet) {
            head = home(f);
            headSet = true;
        }
        switch (phase) {
            case SELECT -> select(f);
            case MOVE -> move(f);
            case MINE -> mine(f);
            case HOME -> goHome(f);
            case FETCH -> fetch(f);
        }
        finishTick(now);
    }

    private void finishTick(long now) {
        boolean moving = phase == Phase.MOVE || phase == Phase.HOME;
        if (syncDirty || moving && now % 40 == 0) {
            pushSync(now);
        }
    }

    private void rescan(long now) {
        MinerScan fresh = MinerScan.scan(level, worldPosition, facing(), MAX_OUTER);
        boolean changed = !fresh.sameAs(scan);
        scan = fresh;
        lastScan = now;
        boolean depot = depotHandler() != null;
        if (changed || depot != depotOk) {
            depotOk = depot;
            syncDirty = true;
        }
    }

    public boolean isVerified() {
        return verified;
    }

    public boolean viewVerified() {
        return viewVerified;
    }

    /** Последняя проверка постройки (для сообщений ключа). */
    @Nullable
    public MinerScan lastScan() {
        return scan;
    }

    /** Проверка ключом: рамка, область, склад. Возвращает причину отказа или null, если всё собрано. */
    @Nullable
    public MachineStatus check() {
        long now = level.getGameTime();
        MinerScan fresh = MinerScan.scan(level, worldPosition, facing(), MAX_OUTER);
        scan = fresh;
        lastScan = now;
        depotOk = depotHandler() != null;
        MachineStatus bad = null;
        if (fresh.error != MinerScan.Error.NONE) {
            bad = frameStatus(fresh.error);
        } else if (fresh.unloaded) {
            bad = MachineStatus.UNLOADED;
        } else if (!depotOk) {
            bad = MachineStatus.NO_DEPOT;
        }
        verified = bad == null;
        setChanged();
        pushSync(now);
        return bad;
    }

    private static MachineStatus frameStatus(MinerScan.Error error) {
        return switch (error) {
            case NOT_CLOSED -> MachineStatus.FRAME_OPEN;
            case EXTRA -> MachineStatus.FRAME_EXTRA;
            case SIZE -> MachineStatus.FRAME_SIZE;
            case CORNER -> MachineStatus.FRAME_CORNER;
            case FRONT -> MachineStatus.FRAME_FRONT;
            case BLOCKED -> MachineStatus.AREA_BLOCKED;
            default -> MachineStatus.IDLE;
        };
    }

    /** Энергия на тик с учётом модуля; false, если не хватает (статус выставлен). */
    private boolean pay(int base) {
        int cost = base * activeSpeed() * activeEnergyPercent() / 100;
        if (energy.getEnergyStored() < cost) {
            setStatus(MachineStatus.NO_ENERGY);
            return false;
        }
        energy.consume(cost);
        return true;
    }

    // ------------------------------------------------------------------ фазы

    /** Выбирает следующий блок слоя; без наконечника едет за ним. */
    private void select(MinerFrame f) {
        if (tip.isEmpty()) {
            phase = Phase.HOME;
            viaPlane = true;
            syncDirty = true;
            return;
        }
        int total = f.cells();
        int minY = level.getMinBuildHeight();
        int budget = 256;                              // не больше 256 проверок клеток за тик, чтобы пустая шахта не вешала сервер
        while (true) {
            if (f.y() - 1 - layer < minY) {
                clearCracks();
                setStatus(MachineStatus.MINE_DONE);
                return;
            }
            while (cell < total) {
                if (--budget < 0) {
                    setStatus(MachineStatus.RUNNING);
                    return;
                }
                BlockPos pos = cellPos(f, cell);
                if (!level.isLoaded(pos)) {
                    setStatus(MachineStatus.UNLOADED);
                    return;
                }
                BlockState state = level.getBlockState(pos);
                if (!state.getFluidState().isEmpty()) {
                    setStatus(MachineStatus.LIQUID);
                    return;
                }
                if (isMineable(pos, state)) {
                    if (!workAreaLoaded(pos)) {          // рядом выгруженный чанк: не трогаем, чтобы разрушение не подгрузило его
                        setStatus(MachineStatus.UNLOADED);
                        return;
                    }
                    mining = pos;
                    crackStage = -1;
                    target = new Vec3(pos.getX() + 0.5, pos.getY() + 0.8, pos.getZ() + 0.5);
                    phase = Phase.MOVE;
                    syncDirty = true;
                    setChanged();
                    return;
                }
                cell++;
            }
            layer++;
            cell = 0;
            setChanged();
        }
    }

    private boolean isMineable(BlockPos pos, BlockState state) {
        if (state.isAir() || state.getDestroySpeed(level, pos) < 0) {
            return false;
        }
        if (state.is(dev.technogenesis.kontur.registry.KonturTags.MINER_UNBREAKABLE)) {
            return false;
        }
        // блоки с инвентарём (сундуки, печи) не трогаем
        if (level.getBlockEntity(pos) != null
                && level.getCapability(Capabilities.ItemHandler.BLOCK, pos, null) != null) {
            return false;
        }
        return true;
    }

    private void move(MinerFrame f) {
        if (!pay(ENERGY_MOVE)) {
            return;
        }
        setStatus(MachineStatus.RUNNING);
        if (advance(target, viaPlane, f)) {
            if (!workAreaLoaded(mining)) {
                setStatus(MachineStatus.UNLOADED);
                return;
            }
            viaPlane = false;
            phase = Phase.MINE;
            mineProgress = 0;
            BlockState state = level.getBlockState(mining);
            float hardness = Math.max(0f, state.getDestroySpeed(level, mining));
            mineTotal = Math.max(4, (int) (6 + hardness * 10));
            syncDirty = true;
        }
        setChanged();
    }

    private void goHome(MinerFrame f) {
        if (!pay(ENERGY_MOVE)) {
            return;
        }
        setStatus(MachineStatus.RUNNING);
        if (advance(home(f), true, f)) {
            phase = Phase.FETCH;
            fetchTimer = FETCH_TICKS;
            syncDirty = true;
        }
        setChanged();
    }

    /** Двигает головку к to; true, если пришла. */
    private boolean advance(Vec3 to, boolean via, MinerFrame f) {
        Vec3[] way = MinerPath.waypoints(head, to, via, planeTipY(f));
        head = MinerPath.along(head, way, MOVE_SPEED * activeSpeed());
        return head.distanceToSqr(to) < 1e-6;
    }

    private void mine(MinerFrame f) {
        if (!workAreaLoaded(mining)) {                 // чанк выгрузили на ходу: ждём, а не подгружаем его запросом блока
            setStatus(MachineStatus.UNLOADED);
            return;
        }
        BlockState state = level.getBlockState(mining);
        if (state.isAir()) {                       // блок исчез сам
            cell++;
            phase = Phase.SELECT;
            syncDirty = true;
            return;
        }
        if (!state.getFluidState().isEmpty()) {
            setStatus(MachineStatus.LIQUID);
            return;
        }
        if (mineProgress < mineTotal) {
            if (!pay(ENERGY_MINE)) {
                return;
            }
            setStatus(MachineStatus.RUNNING);
            mineProgress = Math.min(mineTotal, mineProgress + activeSpeed());
            crack(Math.min(9, mineProgress * 10 / mineTotal));
            setChanged();
            return;
        }
        breakBlock(state);
    }

    private void breakBlock(BlockState state) {
        if (NeoForge.EVENT_BUS.post(new BlockEvent.BreakEvent(level, mining, state,
                FakePlayerFactory.getMinecraft((net.minecraft.server.level.ServerLevel) level))).isCanceled()) {
            skipCell();                              // защищённый блок (приват и т. п.) не ломаем
            return;
        }
        List<ItemStack> drops = Block.getDrops(state, (net.minecraft.server.level.ServerLevel) level, mining,
                level.getBlockEntity(mining), null, new ItemStack(Items.NETHERITE_PICKAXE));
        if (!fits(drops)) {
            setStatus(MachineStatus.OUTPUT_FULL);    // место в буфере кончилось: ждём, ничего не теряя
            return;
        }
        float hardness = Math.max(0f, state.getDestroySpeed(level, mining));
        crack(-1);
        level.destroyBlock(mining, false);
        for (ItemStack drop : drops) {
            ItemStack left = ItemHandlerHelper.insertItem(inventory, drop, false);
            if (!left.isEmpty()) {
                Block.popResource(level, mining, left);
            }
        }
        // износ наконечника по твёрдости
        tip.setDamageValue(tip.getDamageValue() + Math.max(1, (int) Math.ceil(hardness)));
        boolean broken = tip.getDamageValue() >= tip.getMaxDamage();
        cell++;
        mineProgress = 0;
        if (broken) {
            tip = ItemStack.EMPTY;
            level.playSound(null, worldPosition, SoundEvents.ITEM_BREAK, SoundSource.BLOCKS, 0.8f, 1.0f);
            phase = Phase.HOME;
            viaPlane = true;
        } else {
            phase = Phase.SELECT;
        }
        syncDirty = true;
        setChanged();
    }

    private void skipCell() {
        crack(-1);
        cell++;
        mineProgress = 0;
        phase = Phase.SELECT;
        syncDirty = true;
    }

    /** Поместится ли вся добыча в буфер ядра (проверка на копии буфера). */
    private boolean fits(List<ItemStack> drops) {
        ItemStackHandler copy = new ItemStackHandler(inventory.getSlots());
        for (int i = 0; i < inventory.getSlots(); i++) {
            copy.setStackInSlot(i, inventory.getStackInSlot(i).copy());
        }
        for (ItemStack drop : drops) {
            if (!ItemHandlerHelper.insertItem(copy, drop.copy(), false).isEmpty()) {
                return false;
            }
        }
        return true;
    }

    private void fetch(MinerFrame f) {
        IItemHandler depot = depotHandler();
        if (depot == null) {
            setStatus(MachineStatus.NO_DEPOT);
            return;
        }
        if (noTipWait > 0) {                       // склад пуст: ждём секунду и проверяем снова
            noTipWait--;
            setStatus(MachineStatus.NO_TIPS);
            return;
        }
        if (fetchTimer > 0) {
            if (!pay(ENERGY_MOVE)) {
                return;
            }
            setStatus(MachineStatus.TIP_SWAP);
            fetchTimer--;
            return;
        }
        for (int slot = 0; slot < depot.getSlots(); slot++) {
            ItemStack probe = depot.extractItem(slot, 1, true);
            if (probe.getItem() instanceof DrillTipItem) {
                tip = depot.extractItem(slot, 1, false);
                phase = Phase.SELECT;
                viaPlane = true;
                syncDirty = true;
                setChanged();
                return;
            }
        }
        setStatus(MachineStatus.NO_TIPS);
        noTipWait = FETCH_TICKS;
    }

    /** Склад наконечников: инвентарь вплотную к лицевой грани ядра. */
    @Nullable
    private IItemHandler depotHandler() {
        Direction front = facing();
        BlockPos at = worldPosition.relative(front);
        if (!level.isLoaded(at)) {                      // склад в выгруженном чанке: считаем, что его нет, но не загружаем чанк
            return null;
        }
        return level.getCapability(Capabilities.ItemHandler.BLOCK, at, front.getOpposite());
    }

    private void clearCracks() {
        if (mining != null && crackStage != -1) {
            crack(-1);
        }
    }

    /**
     * Трещины на блоке рассылаются игрокам пакетом; отправляется только смена стадии (и раз в 5 секунд, чтобы клиент не
     * забыл долгую ломку), а не каждый тик.
     */
    private void crack(int stage) {
        if (mining == null) {
            return;
        }
        if (stage != crackStage || stage >= 0 && level.getGameTime() % 100 == 0) {
            level.destroyBlockProgress(-worldPosition.hashCode(), mining, stage);
            crackStage = stage;
        }
    }

    /** Блок и его соседи по горизонтали загружены: разрушение и обновления соседей не вызовут загрузку чанка. */
    private boolean workAreaLoaded(BlockPos pos) {
        return level.hasChunksAt(pos.offset(-1, -1, -1), pos.offset(1, 1, 1));
    }

    // ------------------------------------------------------------------ синхронизация с клиентом

    private void pushSync(long now) {
        syncHead = head;
        syncTarget = switch (phase) {
            case MOVE -> target;
            case HOME -> scan != null && scan.frame != null ? home(scan.frame) : head;
            default -> head;
        };
        syncVia = viaPlane || phase == Phase.HOME;
        syncMoving = phase == Phase.MOVE || phase == Phase.HOME;
        syncMining = phase == Phase.MINE;
        syncSpeed = MOVE_SPEED * activeSpeed();
        syncTime = now;
        syncTip = tip.getItem() instanceof DrillTipItem t ? t.tier().code() : 0;
        viewScan = scan;
        viewDepot = depotOk;
        viewVerified = verified;
        syncDirty = false;
        level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        CompoundTag tag = super.getUpdateTag(registries);
        if (viewScan != null) {
            tag.putInt("scanError", viewScan.error.ordinal());
            tag.putBoolean("scanUnloaded", viewScan.unloaded);
            if (viewScan.frame != null) {
                tag.putIntArray("frame", viewScan.frame.toArray());
            }
            tag.putLongArray("missing", viewScan.missing);
            tag.putLongArray("obstacles", viewScan.obstacles);
        }
        tag.putBoolean("depot", viewDepot);
        tag.putBoolean("verified", viewVerified);
        tag.putDouble("hx", syncHead.x);
        tag.putDouble("hy", syncHead.y);
        tag.putDouble("hz", syncHead.z);
        tag.putDouble("tx", syncTarget.x);
        tag.putDouble("ty", syncTarget.y);
        tag.putDouble("tz", syncTarget.z);
        tag.putBoolean("via", syncVia);
        tag.putBoolean("moving", syncMoving);
        tag.putBoolean("mining", syncMining);
        tag.putDouble("speed", syncSpeed);
        tag.putLong("time", syncTime);
        tag.putInt("tipTier", syncTip);
        return tag;
    }

    @Override
    public void handleUpdateTag(CompoundTag tag, HolderLookup.Provider registries) {
        super.handleUpdateTag(tag, registries);
        if (tag.contains("scanError")) {
            int o = tag.getInt("scanError");
            MinerScan.Error err = o >= 0 && o < MinerScan.Error.values().length ? MinerScan.Error.values()[o] : MinerScan.Error.NONE;
            MinerFrame f = tag.contains("frame") ? MinerFrame.fromArray(tag.getIntArray("frame")) : null;
            viewScan = new MinerScan(err, f, tag.getLongArray("missing"), tag.getLongArray("obstacles"),
                    tag.getBoolean("scanUnloaded"));
        }
        viewDepot = tag.getBoolean("depot");
        viewVerified = tag.getBoolean("verified");
        syncHead = new Vec3(tag.getDouble("hx"), tag.getDouble("hy"), tag.getDouble("hz"));
        syncTarget = new Vec3(tag.getDouble("tx"), tag.getDouble("ty"), tag.getDouble("tz"));
        syncVia = tag.getBoolean("via");
        syncMoving = tag.getBoolean("moving");
        syncMining = tag.getBoolean("mining");
        syncSpeed = tag.getDouble("speed");
        syncTime = tag.getLong("time");
        syncTip = tag.getInt("tipTier");
    }

    // --- для отрисовки на клиенте

    /**
     * Рамка для отрисовки. Если синхронизация ещё не пришла, клиент проверяет рамку сам по своему миру,
     * чтобы балка и головка рисовались независимо от пакетов.
     */
    @Nullable
    public MinerScan viewScan() {
        if (viewScan != null) {
            return viewScan;
        }
        if (level != null && level.isClientSide) {
            long t = level.getGameTime();
            if (clientScan == null || t - clientScanTime >= 40 || t < clientScanTime) {
                clientScan = MinerScan.scan(level, worldPosition, facing(), MAX_OUTER);
                clientScanTime = t;
            }
            return clientScan;
        }
        return null;
    }

    public boolean viewDepot() {
        return viewDepot;
    }

    public int viewTip() {
        return syncTip;
    }

    public boolean viewMining() {
        return syncMining;
    }

    /** Положение головки в данный момент: от последней синхронизации едет по тому же пути, что и на сервере. */
    public Vec3 viewHead(float partialTick) {
        MinerScan sc = viewScan();
        MinerFrame f = sc == null ? null : sc.frame;
        if (f == null) {
            return syncHead;
        }
        if (syncHead.lengthSqr() == 0) {                 // состояние головки ещё не пришло: она стоит над ядром
            return home(f);
        }
        if (!syncMoving || level == null) {
            return syncHead;
        }
        double ticks = Math.max(0.0, level.getGameTime() + partialTick - syncTime);
        Vec3[] way = MinerPath.waypoints(syncHead, syncTarget, syncVia, planeTipY(f));
        return MinerPath.along(syncHead, way, ticks * syncSpeed);
    }

    /** Область отрисовки: вся рамка с запасом по высоте, иначе балку за пределами блока обрежет отсечение по кадру. */
    public AABB renderArea() {
        MinerScan sc = viewScan();
        MinerFrame f = sc == null ? null : sc.frame;
        if (f == null) {
            return new AABB(worldPosition).inflate(8.0);
        }
        return new AABB(f.minX() - 1, level == null ? f.y() - 64 : level.getMinBuildHeight(), f.minZ() - 1,
                f.maxX() + 2, f.y() + 3, f.maxZ() + 2);
    }

    // ------------------------------------------------------------------ сохранение и меню

    @Override
    protected void extraSync(int[] data) {
        data[5] = tip.getItem() instanceof DrillTipItem t ? t.tier().code() : 0;
        data[6] = tip.isEmpty() ? 0 : tip.getMaxDamage() - tip.getDamageValue();
        data[7] = layer;
        MinerFrame f = scan == null ? null : scan.frame;
        data[19] = f == null || f.cells() == 0 ? 0 : Math.min(100, cell * 100 / f.cells());
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putInt("mLayer", layer);
        tag.putInt("mCell", cell);
        tag.putInt("mPhase", phase.ordinal());
        tag.putBoolean("mVerified", verified);
        tag.putBoolean("mVia", viaPlane);
        if (headSet) {
            tag.putDouble("mhx", head.x);
            tag.putDouble("mhy", head.y);
            tag.putDouble("mhz", head.z);
        }
        if (workFrame != null) {
            tag.putIntArray("mFrame", workFrame.toArray());
        }
        if (!tip.isEmpty()) {
            tag.put("mTip", tip.save(registries));
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        layer = tag.getInt("mLayer");
        cell = tag.getInt("mCell");
        verified = tag.getBoolean("mVerified");
        int p = tag.getInt("mPhase");
        // после загрузки цель и блок не хранятся: фаза движения и ломки начинается с выбора блока
        phase = p == Phase.FETCH.ordinal() || p == Phase.HOME.ordinal() ? Phase.HOME : Phase.SELECT;
        viaPlane = tag.getBoolean("mVia") || phase == Phase.HOME;
        headSet = tag.contains("mhx");
        head = headSet ? new Vec3(tag.getDouble("mhx"), tag.getDouble("mhy"), tag.getDouble("mhz")) : Vec3.ZERO;
        workFrame = tag.contains("mFrame") ? MinerFrame.fromArray(tag.getIntArray("mFrame")) : null;
        tip = tag.contains("mTip") ? ItemStack.parse(registries, tag.getCompound("mTip")).orElse(ItemStack.EMPTY) : ItemStack.EMPTY;
        syncDirty = true;
    }

    @Override
    protected void updateBlockState() {
        boolean active = shown == MachineStatus.RUNNING;
        BlockState state = getBlockState();
        if (state.hasProperty(MachineBlock.ACTIVE) && state.getValue(MachineBlock.ACTIVE) != active) {
            level.setBlock(worldPosition, state.setValue(MachineBlock.ACTIVE, active), 3);
        }
    }

    /** Угол поворота для отрисовки доступен только клиенту. */
    public double headTipY() {
        return syncHead.y;
    }
}
