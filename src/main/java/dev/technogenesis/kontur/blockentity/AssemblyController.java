package dev.technogenesis.kontur.blockentity;

import dev.technogenesis.kontur.machine.AssemblyTracker;

/** Контроллер собираемой игроком машины: порты корпуса работают, только пока машина собрана и цела. */
public interface AssemblyController {
    AssemblyTracker tracker();

    default boolean isFormed() {
        return tracker().active();
    }
}
