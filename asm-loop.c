#include "main.h"

void wait(int seconds) {
    clock_t end_time = clock() + seconds * CLOCKS_PER_SEC;
    while (clock() < end_time) {
        for (int i = 0; i < 1000000; i++) {
            __asm__ ("");
        }
    }
}