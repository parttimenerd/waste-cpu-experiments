#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void wait(int seconds);

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <seconds>\n", argv[0]);
        return 1;
    }

    int seconds = atoi(argv[1]); // Parse argument to int
    printf("Waiting for %d seconds...\n", seconds);

    wait(seconds);

    printf("Done!\n");
    return 0;
}