#include "scheduler.h"
#include "console.h"

static unsigned tick_count;

void xk_scheduler_init(void) {
    tick_count = 0;
    console_puts("[X] Scheduler init\n");
}

void xk_scheduler_tick(void) {
    tick_count++;
    (void)tick_count;
}
