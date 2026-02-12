#include "io.h"

u8 inb(u16 port) {
    u8 value;
    __asm__ __volatile__("inb %1, %0" : "=a"(value) : "dN"(port));
    return value;
}

u16 inw(u16 port) {
    u16 value;
    __asm__ __volatile__("inw %1, %0" : "=a"(value) : "dN"(port));
    return value;
}

u32 inl(u16 port) {
    u32 value;
    __asm__ __volatile__("inl %1, %0" : "=a"(value) : "dN"(port));
    return value;
}

void outb(u16 port, u8 value) {
    __asm__ __volatile__("outb %0, %1" : : "a"(value), "dN"(port));
}

void outw(u16 port, u16 value) {
    __asm__ __volatile__("outw %0, %1" : : "a"(value), "dN"(port));
}

void outl(u16 port, u32 value) {
    __asm__ __volatile__("outl %0, %1" : : "a"(value), "dN"(port));
}

void io_wait(void) {
    __asm__ __volatile__("outb %%al, $0x80" : : "a"(0));
}
