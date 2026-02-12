#include "syscall.h"
#include "syscall_table.h"

static unsigned int read_eax(void) {
    unsigned int value;
    __asm__ __volatile__("mov %%eax, %0" : "=r"(value));
    return value;
}

static unsigned int read_ebx(void) {
    unsigned int value;
    __asm__ __volatile__("mov %%ebx, %0" : "=r"(value));
    return value;
}

static unsigned int read_ecx(void) {
    unsigned int value;
    __asm__ __volatile__("mov %%ecx, %0" : "=r"(value));
    return value;
}

static unsigned int read_edx(void) {
    unsigned int value;
    __asm__ __volatile__("mov %%edx, %0" : "=r"(value));
    return value;
}

static unsigned int read_esi(void) {
    unsigned int value;
    __asm__ __volatile__("mov %%esi, %0" : "=r"(value));
    return value;
}

void syscall_write(const char* str) {
    (void)syscall_table_dispatch(1, (unsigned int)str, 0, 0, 0);
}

void syscall_handler(void) {
    unsigned int id = read_eax();
    unsigned int a = read_ebx();
    unsigned int b = read_ecx();
    unsigned int c = read_edx();
    unsigned int d = read_esi();

    (void)syscall_table_dispatch(id, a, b, c, d);
}
