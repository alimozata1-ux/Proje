#include "../net/net_stack.h"
#include <stdint.h>
#include "../cpu/idt.h"
#include "../multitasking/task.h"

static inline void outb(uint16_t port, uint8_t value) {
    __asm__ __volatile__("outb %0, %1" : : "a"(value), "Nd"(port));
}

volatile uint32_t timer_ticks = 0;
volatile uint8_t frame_ready = 0;
static uint32_t frame_accum = 0;

static void timer_callback(registers_t *r) {
    (void)r;
    timer_ticks++;
    task_schedule_tick();
    frame_accum += 60;
    if (g_net_activity_blink) g_net_activity_blink--;
    if (frame_accum >= 100) {
        frame_accum -= 100;
        frame_ready = 1;
    }
}

void timer_init(uint32_t frequency_hz) {
    if (frequency_hz == 0) frequency_hz = 100;
    uint32_t divisor = 1193180u / frequency_hz;

    irq_install_handler(0, timer_callback);
    outb(0x43, 0x36);
    outb(0x40, (uint8_t)(divisor & 0xFF));
    outb(0x40, (uint8_t)((divisor >> 8) & 0xFF));
}
