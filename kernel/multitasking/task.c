#include "task.h"

#define MAX_TASKS 8

static task_t tasks[MAX_TASKS];
static uint32_t task_count = 0;
static uint32_t current_idx = 0;
static uint32_t next_task_id = 1;

static void task_idle_a(void) { for (;;) { __asm__ __volatile__("pause"); } }
static void task_idle_b(void) { for (;;) { __asm__ __volatile__("nop"); } }

void tasking_init(void) {
    task_count = 0;
    current_idx = 0;
    next_task_id = 1;

    tasks[0].task_id = next_task_id++;
    tasks[0].page_directory = 0;
    tasks[0].state = TASK_RUNNING;
    tasks[0].entry = 0;
    tasks[0].has_started = 1;
    task_count = 1;

    (void)task_create(task_idle_a, 0);
    (void)task_create(task_idle_b, 0);
}

int task_create(void (*entry)(void), uint32_t page_directory) {
    if (task_count >= MAX_TASKS || entry == 0) return -1;
    task_t *t = &tasks[task_count++];
    t->task_id = next_task_id++;
    t->regs.esp = 0;
    t->regs.ebp = 0;
    t->regs.eip = (uint32_t)(uintptr_t)entry;
    t->regs.eflags = 0x202;
    t->regs.eax = t->regs.ebx = t->regs.ecx = t->regs.edx = 0;
    t->regs.esi = t->regs.edi = 0;
    t->regs.cr3 = page_directory;
    t->page_directory = page_directory;
    t->state = TASK_READY;
    t->entry = entry;
    t->has_started = 0;
    return (int)t->task_id;
}

task_t *task_current(void) { return &tasks[current_idx]; }

void task_schedule_tick(void) {
    task_t *cur = &tasks[current_idx];
    __asm__ __volatile__("mov %%esp,%0" : "=r"(cur->regs.esp));
    __asm__ __volatile__("mov %%ebp,%0" : "=r"(cur->regs.ebp));
    cur->state = TASK_READY;

    for (uint32_t step = 1; step <= task_count; ++step) {
        uint32_t idx = (current_idx + step) % task_count;
        if (tasks[idx].state == TASK_READY || tasks[idx].state == TASK_RUNNING) {
            current_idx = idx;
            break;
        }
    }

    task_t *next = &tasks[current_idx];
    next->state = TASK_RUNNING;
    if (!next->has_started && next->entry) {
        next->has_started = 1;
        next->entry();
    }

    if (next->regs.esp != 0) {
        __asm__ __volatile__("mov %0,%%esp" : : "r"(next->regs.esp));
    }
    if (next->regs.ebp != 0) {
        __asm__ __volatile__("mov %0,%%ebp" : : "r"(next->regs.ebp));
    }
}
