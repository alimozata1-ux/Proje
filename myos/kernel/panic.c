#include "panic.h"
#include "logger.h"
#include "serial.h"

void panic(const char* reason) {
    log_error("PANIC", reason);
    serial_write("System halted.\n");
    for (;;) {
        __asm__ __volatile__("cli; hlt");
    }
}

void panic_hex(const char* reason, unsigned int code) {
    log_error("PANIC", reason);
    serial_write("code=");
    serial_write_hex(code);
    serial_write("\n");
    for (;;) {
        __asm__ __volatile__("cli; hlt");
    }
}
