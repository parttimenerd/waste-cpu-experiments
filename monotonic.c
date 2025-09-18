#include "main.h"
#include <time.h>

long own_clock_nanos() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e9 + ts.tv_nsec;
}

void my_wait(int seconds) {
    long end_time = own_clock_nanos() + seconds * 1e9;
    while (own_clock_nanos() < end_time) {
        // cpu wasting loop
    }
}
