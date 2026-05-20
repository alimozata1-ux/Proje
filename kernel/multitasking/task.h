#ifndef TASK_H
#define TASK_H

#include <stdint.h>

typedef enum {
    TASK_READY = 0,
    TASK_RUNNING = 1,
    TASK_BLOCKED = 2
} task_state_t;

typedef struct {
    uint32_t esp;
    uint32_t ebp;
    uint32_t eip;
    uint32_t eflags;
    uint32_t eax, ebx, ecx, edx, esi, edi;
    uint32_t cr3;
} cpu_registers_t;

typedef struct {
    uint32_t task_id;
    cpu_registers_t regs;
    uint32_t page_directory;
    task_state_t state;
    void (*entry)(void);
    uint8_t has_started;
} task_t;

void tasking_init(void);
int task_create(void (*entry)(void), uint32_t page_directory);
void task_schedule_tick(void);
task_t *task_current(void);

#endif
