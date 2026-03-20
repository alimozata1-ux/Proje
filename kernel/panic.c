#include "kernel.h"
#include "console.h"

void kernel_panic(const char *reason) {
    console_puts("\n*** KERNEL PANIC ***\n");
    console_puts(reason ? reason : "unknown");
    console_puts("\nSystem halted.\n");
    for (;;) {
        __asm__ volatile ("hlt");
    }
}
