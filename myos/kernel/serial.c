#include "serial.h"
#include "io.h"

#define COM1_PORT 0x3F8

static const char hex_digits[] = "0123456789ABCDEF";

void serial_init(void) {
    outb(COM1_PORT + 1, 0x00);
    outb(COM1_PORT + 3, 0x80);
    outb(COM1_PORT + 0, 0x03);
    outb(COM1_PORT + 1, 0x00);
    outb(COM1_PORT + 3, 0x03);
    outb(COM1_PORT + 2, 0xC7);
    outb(COM1_PORT + 4, 0x0B);
}

int serial_is_ready(void) {
    return (inb(COM1_PORT + 5) & 0x20) != 0;
}

void serial_write_char(char c) {
    int retry = 0;
    while (!serial_is_ready() && retry < 100000) {
        retry++;
    }
    outb(COM1_PORT, (u8)c);
}

void serial_write(const char* s) {
    while (*s) {
        if (*s == '\n') {
            serial_write_char('\r');
        }
        serial_write_char(*s++);
    }
}

void serial_write_hex(u32 value) {
    int shift;
    serial_write("0x");
    for (shift = 28; shift >= 0; shift -= 4) {
        serial_write_char(hex_digits[(value >> shift) & 0xF]);
    }
}
