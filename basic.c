#include "main.h"

void my_wait(int seconds) {
    clock_t end_time = clock() + seconds * CLOCKS_PER_SEC;
    while (clock() < end_time) {
        // cpu wasting loop
    }
}
