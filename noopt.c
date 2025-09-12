#include "main.h"

// see https://stackoverflow.com/a/49353441
__attribute__((noinline, optnone, optimize(0))) void wait(int seconds) {
    clock_t end_time = clock() + seconds * CLOCKS_PER_SEC;
    while (clock() < end_time) {
        for (int i = 0; i < 1000000; i++);
    }
}