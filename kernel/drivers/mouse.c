#include <stdint.h>
#include "../cpu/idt.h"
#include "../graphics.h"

static inline void outb(uint16_t port, uint8_t value) {
    __asm__ __volatile__("outb %0, %1" : : "a"(value), "Nd"(port));
}
static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ __volatile__("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

int32_t mouse_x = 512;
int32_t mouse_y = 384;
uint8_t mouse_left = 0;
uint8_t mouse_right = 0;

static uint8_t mouse_cycle = 0;
static int8_t mouse_byte[3];

static void mouse_wait_write(void) { while (inb(0x64) & 0x02) {} }
static void mouse_wait_read(void) { while (!(inb(0x64) & 0x01)) {} }
static void mouse_write(uint8_t data) {
    mouse_wait_write(); outb(0x64, 0xD4);
    mouse_wait_write(); outb(0x60, data);
}
static uint8_t mouse_read(void) { mouse_wait_read(); return inb(0x60); }

static void mouse_callback(registers_t *r) {
    (void)r;
    uint8_t data = inb(0x60);
    if (mouse_cycle == 0 && !(data & 0x08)) return;

    mouse_byte[mouse_cycle++] = (int8_t)data;
    if (mouse_cycle < 3) return;
    mouse_cycle = 0;

    mouse_left = (uint8_t)(mouse_byte[0] & 0x1);
    mouse_right = (uint8_t)((mouse_byte[0] >> 1) & 0x1);

    mouse_x += mouse_byte[1];
    mouse_y -= mouse_byte[2];

    if (mouse_x < 0) mouse_x = 0;
    if (mouse_y < 0) mouse_y = 0;
    int32_t max_x = (int32_t)graphics_width() - 1;
    int32_t max_y = (int32_t)graphics_height() - 1;
    if (mouse_x > max_x) mouse_x = max_x;
    if (mouse_y > max_y) mouse_y = max_y;
}

void mouse_init(void) {
    irq_install_handler(12, mouse_callback);

    mouse_wait_write(); outb(0x64, 0xA8);
    mouse_wait_write(); outb(0x64, 0x20);
    mouse_wait_read();
    uint8_t status = inb(0x60) | 0x02;
    mouse_wait_write(); outb(0x64, 0x60);
    mouse_wait_write(); outb(0x60, status);

    mouse_write(0xF6); (void)mouse_read();
    mouse_write(0xF4); (void)mouse_read();
}
