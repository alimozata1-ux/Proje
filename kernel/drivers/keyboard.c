#include <stdint.h>
#include "../cpu/idt.h"

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ __volatile__("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

volatile char keyboard_last_char = 0;

static const char scancode_ascii[128] = {
    0,27,'1','2','3','4','5','6','7','8','9','0','-','=',8,9,
    'q','w','e','r','t','y','u','i','o','p','[',']','\n',0,'a','s',
    'd','f','g','h','j','k','l',';',39,'`',0,'\\','z','x','c','v',
    'b','n','m',',','.','/',0,'*',0,' ',0,0,0,0,0,0,
};

static void keyboard_callback(registers_t *r) {
    (void)r;
    uint8_t scancode = inb(0x60);
    if (scancode & 0x80) return;
    if (scancode < 128) keyboard_last_char = scancode_ascii[scancode];
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_callback);
}
