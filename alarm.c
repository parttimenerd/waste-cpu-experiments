#include "main.h"

#include <unistd.h>
#include <signal.h>
#include <setjmp.h>

static jmp_buf jump_buffer;

void alarm_handler(int sig) {
    // Jump to the label when alarm fires
    longjmp(jump_buffer, 1);
}

void wait(int seconds) {
    // Set up the alarm handler
    signal(SIGALRM, alarm_handler);
    
    // Set the jump point
    if (setjmp(jump_buffer) == 0) {
        // First time through - set alarm and start infinite loop
        alarm(seconds);
        while (1);
    }
}