#include "keyboard.h"
#include "keyboard_buffer.h"
#include "vga.h"

static const char scancode_map[128] = {
    0,   27,  '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t','q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n', 0,
    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,   '\\','z',
    'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0,   '*', 0,   ' ', 0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   '-', 0,   0,   0,   '+', 0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0
};

static unsigned char inb_local(unsigned short port) {
    unsigned char value;
    __asm__ __volatile__("inb %1, %0" : "=a"(value) : "dN"(port));
    return value;
}

void keyboard_init(void) {
    kbd_buffer_init();
}

void keyboard_irq_handler(void) {
    unsigned char scancode = inb_local(0x60);

    if (scancode & 0x80) {
        return;
    }

    if (scancode < 128) {
        char c = scancode_map[scancode];
        if (c) {
            kbd_buffer_push(c);
            vga_put_char(c);
        }
    }
}
