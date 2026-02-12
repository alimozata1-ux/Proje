#include "scheduler.h"
#include "keyboard.h"
#include "paging.h"
#include "task.h"
#include "string.h"
#include "vga.h"

extern void isr_irq0(void);
extern void isr_irq1(void);
extern void isr_page_fault(void);
extern void isr_syscall(void);
extern void idt_load(unsigned int idt_ptr_addr);
extern void enter_user_mode(unsigned int eip, unsigned int user_esp);

struct idt_entry {
    unsigned short base_low;
    unsigned short selector;
    unsigned char zero;
    unsigned char flags;
    unsigned short base_high;
} __attribute__((packed));

struct idt_ptr {
    unsigned short limit;
    unsigned int base;
} __attribute__((packed));

static struct idt_entry idt[256];
static struct idt_ptr idt_descriptor;

static int current_task = -1;
static int user_task_started = 0;
static unsigned int sched_ticks = 0;
static unsigned int quantum_ticks = 5;
static unsigned int quantum_progress = 0;

static void outb(unsigned short port, unsigned char value) {
    __asm__ __volatile__("outb %0, %1" : : "a"(value), "dN"(port));
}

static void io_wait(void) {
    __asm__ __volatile__("outb %%al, $0x80" : : "a"(0));
}

static void idt_set_gate(int index, unsigned int base, unsigned short selector, unsigned char flags) {
    idt[index].base_low = base & 0xFFFF;
    idt[index].selector = selector;
    idt[index].zero = 0;
    idt[index].flags = flags;
    idt[index].base_high = (base >> 16) & 0xFFFF;
}

static void pic_remap(void) {
    outb(0x20, 0x11);
    io_wait();
    outb(0xA0, 0x11);
    io_wait();

    outb(0x21, 0x20);
    io_wait();
    outb(0xA1, 0x28);
    io_wait();

    outb(0x21, 0x04);
    io_wait();
    outb(0xA1, 0x02);
    io_wait();

    outb(0x21, 0x01);
    io_wait();
    outb(0xA1, 0x01);
    io_wait();

    outb(0x21, 0xFC); /* IRQ0 + IRQ1 açık */
    outb(0xA1, 0xFF);
}

static void pit_init(unsigned int frequency) {
    unsigned int divisor = 1193180U / frequency;

    outb(0x43, 0x36);
    outb(0x40, (unsigned char)(divisor & 0xFF));
    outb(0x40, (unsigned char)((divisor >> 8) & 0xFF));
}

static void scheduler_note_tick(void) {
    task_t* current;
    char num[16];

    if ((sched_ticks % 100U) != 0U) {
        return;
    }

    current = task_get(current_task);
    if (!current) {
        return;
    }

    vga_write_string("[sched] tick=");
    kitoa((int)sched_ticks, num);
    vga_write_string(num);
    vga_write_string(" task=");
    vga_write_string(current->name ? current->name : "unknown");
    vga_write_string(" runs=");
    kitoa((int)current->run_count, num);
    vga_write_string(num);
    vga_write_string("\n");
}

void scheduler_init(void) {
    int i;

    for (i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    pic_remap();

    idt_set_gate(14, (unsigned int)isr_page_fault, 0x08, 0x8E);
    idt_set_gate(32, (unsigned int)isr_irq0, 0x08, 0x8E);
    idt_set_gate(33, (unsigned int)isr_irq1, 0x08, 0x8E);
    idt_set_gate(128, (unsigned int)isr_syscall, 0x08, 0xEE); /* DPL=3 */

    idt_descriptor.limit = sizeof(idt) - 1;
    idt_descriptor.base = (unsigned int)&idt;

    idt_load((unsigned int)&idt_descriptor);

    paging_init();
    task_setup();
    pit_init(100);
}

void scheduler_tick(void) {
    task_t* tasks = task_list();
    int total = task_count();

    sched_ticks++;
    quantum_progress++;

    if (total <= 0) {
        return;
    }

    if (current_task < 0) {
        current_task = 0;
        tasks[current_task].state = TASK_RUNNING;
    }

    if (quantum_progress >= quantum_ticks) {
        tasks[current_task].state = TASK_READY;
        current_task = (current_task + 1) % total;
        tasks[current_task].state = TASK_RUNNING;
        quantum_progress = 0;
    }

    tasks[current_task].run_count++;

    if (tasks[current_task].mode == TASK_USER) {
        if (!user_task_started) {
            user_task_started = 1;
            enter_user_mode(tasks[current_task].eip, tasks[current_task].esp);
        }
        scheduler_note_tick();
        return;
    }

    tasks[current_task].entry();
    scheduler_note_tick();
}

void timer_irq_handler(void) {
    scheduler_tick();
    outb(0x20, 0x20);
}

void keyboard_irq_dispatch(void) {
    keyboard_irq_handler();
    outb(0x20, 0x20);
}
