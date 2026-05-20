#include <stdint.h>
#include "../cpu/idt.h"
#include "../graphics.h"
#include "../fs/fat.h"

static uint32_t sys_put_pixel(uint32_t x, uint32_t y, uint32_t color) {
    put_pixel((int)x, (int)y, color);
    return 0;
}

static uint32_t sys_open_file(uint32_t fname_ptr, uint32_t out_ptr) {
    const char *fname = (const char*)(uintptr_t)fname_ptr;
    uint8_t *out = (uint8_t*)(uintptr_t)out_ptr;
    uint32_t size = 0;
    if (fat_read_file(fname, out, &size) != 0) return 0xFFFFFFFFu;
    return size;
}

static uint32_t syscall_dispatch(uint32_t num, uint32_t a, uint32_t b, uint32_t c) {
    (void)c;
    switch (num) {
        case 1: return sys_put_pixel(a, b, 0x00FFFFFF);
        case 2: return sys_open_file(a, b);
        default: return 0xFFFFFFFFu;
    }
}

void syscall_handler(registers_t *r) {
    r->eax = syscall_dispatch(r->eax, r->ebx, r->ecx, r->edx);
}

void syscall_init(void) {
    isr_install_handler(128, syscall_handler);
}
