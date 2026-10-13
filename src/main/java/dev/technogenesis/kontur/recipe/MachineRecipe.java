package dev.technogenesis.kontur.recipe;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.technogenesis.kontur.registry.KonturRecipes;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.Fluid;
import net.neoforged.neoforge.fluids.FluidStack;

/**
 * Универсальный рецепт машины Контура: предмет и/или жидкость на входе, предметы с шансом и жидкости на выходе,
 * полная энергия цикла и время. Всё хранится в JSON, баланс не требует правки кода.
 */
public class MachineRecipe implements Recipe<MachineRecipeInput> {

    public record ItemInput(Ingredient ingredient, int count) {
        public static final Codec<ItemInput> CODEC = RecordCodecBuilder.create(i -> i.group(
                Ingredient.CODEC_NONEMPTY.fieldOf("ingredient").forGetter(ItemInput::ingredient),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("count", 1).forGetter(ItemInput::count)
        ).apply(i, ItemInput::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, ItemInput> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.fromCodecWithRegistries(Ingredient.CODEC_NONEMPTY), ItemInput::ingredient,
                ByteBufCodecs.VAR_INT, ItemInput::count,
                ItemInput::new);

        public boolean test(ItemStack stack) {
            return ingredient.test(stack);
        }
    }

    /** Любая из перечисленных жидкостей (например, обычная или техническая вода). */
    public record FluidInput(List<Fluid> fluids, int amount) {
        public static final Codec<FluidInput> CODEC = RecordCodecBuilder.create(i -> i.group(
                BuiltInRegistries.FLUID.byNameCodec().listOf().fieldOf("fluids").forGetter(FluidInput::fluids),
                ExtraCodecs.POSITIVE_INT.fieldOf("amount").forGetter(FluidInput::amount)
        ).apply(i, FluidInput::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, FluidInput> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.registry(Registries.FLUID).apply(ByteBufCodecs.list()), FluidInput::fluids,
                ByteBufCodecs.VAR_INT, FluidInput::amount,
                FluidInput::new);

        public boolean accepts(Fluid fluid) {
            return fluids.contains(fluid);
        }

        public boolean test(FluidStack stack) {
            return !stack.isEmpty() && accepts(stack.getFluid()) && stack.getAmount() >= amount;
        }
    }

    public record ChanceResult(Item item, int count, float chance) {
        public static final Codec<ChanceResult> CODEC = RecordCodecBuilder.create(i -> i.group(
                BuiltInRegistries.ITEM.byNameCodec().fieldOf("id").forGetter(ChanceResult::item),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("count", 1).forGetter(ChanceResult::count),
                Codec.floatRange(0.0f, 1.0f).optionalFieldOf("chance", 1.0f).forGetter(ChanceResult::chance)
        ).apply(i, ChanceResult::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, ChanceResult> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.registry(Registries.ITEM), ChanceResult::item,
                ByteBufCodecs.VAR_INT, ChanceResult::count,
                ByteBufCodecs.FLOAT, ChanceResult::chance,
                ChanceResult::new);

        public ItemStack stack() {
            return new ItemStack(item, count);
        }
    }

    public record FluidOutput(Fluid fluid, int amount) {
        public static final Codec<FluidOutput> CODEC = RecordCodecBuilder.create(i -> i.group(
                BuiltInRegistries.FLUID.byNameCodec().fieldOf("fluid").forGetter(FluidOutput::fluid),
                ExtraCodecs.POSITIVE_INT.fieldOf("amount").forGetter(FluidOutput::amount)
        ).apply(i, FluidOutput::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, FluidOutput> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.registry(Registries.FLUID), FluidOutput::fluid,
                ByteBufCodecs.VAR_INT, FluidOutput::amount,
                FluidOutput::new);

        public FluidStack stack() {
            return new FluidStack(fluid, amount);
        }
    }

    private final KonturRecipes.Kind kind;
    private final Optional<ItemInput> input;
    /** Второй предмет на входе (сплавы): кладётся во второй входной слот. */
    private final Optional<ItemInput> inputB;
    private final Optional<FluidInput> fluidInput;
    private final List<ChanceResult> results;
    private final List<FluidOutput> fluidResults;
    private final int energy;
    private final int time;

    public MachineRecipe(KonturRecipes.Kind kind, Optional<ItemInput> input, Optional<ItemInput> inputB,
                         Optional<FluidInput> fluidInput, List<ChanceResult> results, List<FluidOutput> fluidResults,
                         int energy, int time) {
        this.kind = kind;
        this.input = input;
        this.inputB = inputB;
        this.fluidInput = fluidInput;
        this.results = results;
        this.fluidResults = fluidResults;
        this.energy = energy;
        this.time = Math.max(1, time);
    }

    public static MapCodec<MachineRecipe> codec(KonturRecipes.Kind kind) {
        return RecordCodecBuilder.mapCodec(i -> i.group(
                ItemInput.CODEC.optionalFieldOf("input").forGetter(r -> r.input),
                ItemInput.CODEC.optionalFieldOf("input_b").forGetter(r -> r.inputB),
                FluidInput.CODEC.optionalFieldOf("fluid_input").forGetter(r -> r.fluidInput),
                ChanceResult.CODEC.listOf().fieldOf("results").forGetter(r -> r.results),
                FluidOutput.CODEC.listOf().optionalFieldOf("fluid_results", List.of()).forGetter(r -> r.fluidResults),
                ExtraCodecs.NON_NEGATIVE_INT.fieldOf("energy").forGetter(r -> r.energy),
                ExtraCodecs.POSITIVE_INT.fieldOf("time").forGetter(r -> r.time)
        ).apply(i, (in, inB, fin, res, fres, e, t) -> new MachineRecipe(kind, in, inB, fin, res, fres, e, t)));
    }

    public static StreamCodec<RegistryFriendlyByteBuf, MachineRecipe> streamCodec(KonturRecipes.Kind kind) {
        StreamCodec<RegistryFriendlyByteBuf, Optional<ItemInput>> item = ByteBufCodecs.optional(ItemInput.STREAM_CODEC);
        StreamCodec<RegistryFriendlyByteBuf, Optional<FluidInput>> fluid = ByteBufCodecs.optional(FluidInput.STREAM_CODEC);
        StreamCodec<RegistryFriendlyByteBuf, List<ChanceResult>> res = ChanceResult.STREAM_CODEC.apply(ByteBufCodecs.list());
        StreamCodec<RegistryFriendlyByteBuf, List<FluidOutput>> fres = FluidOutput.STREAM_CODEC.apply(ByteBufCodecs.list());
        return StreamCodec.of((buf, r) -> {
            item.encode(buf, r.input);
            item.encode(buf, r.inputB);
            fluid.encode(buf, r.fluidInput);
            res.encode(buf, r.results);
            fres.encode(buf, r.fluidResults);
            ByteBufCodecs.VAR_INT.encode(buf, r.energy);
            ByteBufCodecs.VAR_INT.encode(buf, r.time);
        }, buf -> {
            Optional<ItemInput> in = item.decode(buf);
            Optional<ItemInput> inB = item.decode(buf);
            Optional<FluidInput> fin = fluid.decode(buf);
            List<ChanceResult> results = res.decode(buf);
            List<FluidOutput> fluidResults = fres.decode(buf);
            int energy = ByteBufCodecs.VAR_INT.decode(buf);
            int time = ByteBufCodecs.VAR_INT.decode(buf);
            return new MachineRecipe(kind, in, inB, fin, results, fluidResults, energy, time);
        });
    }

    public Optional<ItemInput> input() {
        return input;
    }

    public Optional<ItemInput> inputB() {
        return inputB;
    }

    public Optional<FluidInput> fluidInput() {
        return fluidInput;
    }

    public List<ChanceResult> results() {
        return results;
    }

    public List<FluidOutput> fluidResults() {
        return fluidResults;
    }

    /** Полная энергия цикла, FE. */
    public int energy() {
        return energy;
    }

    /** Длительность цикла, тики. */
    public int time() {
        return time;
    }

    /** Энергия, которую нужно заплатить на данном тике; сумма по всем тикам цикла равна ровно energy(). */
    public int energyForTick(int tickIndex) {
        return (int) ((long) energy * (tickIndex + 1) / time) - (int) ((long) energy * tickIndex / time);
    }

    public boolean matchesItemOnly(ItemStack stack) {
        return input.map(in -> in.test(stack) && stack.getCount() >= in.count()).orElse(true);
    }

    @Override
    public boolean matches(MachineRecipeInput in, Level level) {
        if (input.isPresent() && !(input.get().test(in.stack()) && in.stack().getCount() >= input.get().count())) {
            return false;
        }
        if (inputB.isPresent() && !(inputB.get().test(in.stackB()) && in.stackB().getCount() >= inputB.get().count())) {
            return false;
        }
        return fluidInput.map(f -> f.test(in.fluid())).orElse(true);
    }

    @Override
    public ItemStack assemble(MachineRecipeInput in, HolderLookup.Provider registries) {
        return results.isEmpty() ? ItemStack.EMPTY : results.get(0).stack();
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return true;
    }

    @Override
    public ItemStack getResultItem(HolderLookup.Provider registries) {
        return results.isEmpty() ? ItemStack.EMPTY : results.get(0).stack();
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return kind.serializer.get();
    }

    @Override
    public RecipeType<?> getType() {
        return kind.type.get();
    }

    @Override
    public boolean isSpecial() {
        return true;
    }
}
