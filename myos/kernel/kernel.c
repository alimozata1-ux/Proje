#include "allocator.h"
#include "diagnostics.h"
#include "gui.h"
#include "keyboard.h"
#include "kernel_mode.h"
#include "logger.h"
#include "scheduler.h"
#include "settings.h"
#include "serial.h"
#include "shell.h"
#include "vga.h"

void kernel_main(void) {
    vga_clear();
    serial_init();

    log_info("kernel", "boot start");

    allocator_init();
    kernel_mode_init();
    scheduler_init();
    keyboard_init();
    shell_init();
    settings_init();
    gui_init();
    diagnostics_init();

    log_info("kernel", "interrupts on");

    __asm__ __volatile__("sti");

    for (;;) {
        shell_tick();
        diagnostics_tick();
        __asm__ __volatile__("hlt");
    }
}
