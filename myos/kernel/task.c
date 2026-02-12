#include "task.h"
#include "user.h"
#include "vga.h"

#define MAX_TASKS 3
static task_t tasks[MAX_TASKS];

static void task1(void) {
    vga_write_string("[task] Task 1 (kernel) running\n");
}

static void task2(void) {
    vga_write_string("[task] Task 2 (kernel) running\n");
}

static void task_reset(task_t* t, const char* name, void (*entry)(void), task_mode_t mode) {
    t->entry = entry;
    t->eip = (unsigned int)entry;
    t->esp = (unsigned int)&t->stack[4095];
    t->state = TASK_READY;
    t->mode = mode;
    t->name = name;
    t->run_count = 0;
}

void task_setup(void) {
    task_reset(&tasks[0], "kworker-1", task1, TASK_KERNEL);
    task_reset(&tasks[1], "kworker-2", task2, TASK_KERNEL);

    tasks[2].entry = user_mode_demo;
    tasks[2].eip = user_entry_point();
    tasks[2].esp = user_stack_top();
    tasks[2].state = TASK_READY;
    tasks[2].mode = TASK_USER;
    tasks[2].name = "user-demo";
    tasks[2].run_count = 0;
}

task_t* task_list(void) {
    return tasks;
}

int task_count(void) {
    return MAX_TASKS;
}

task_t* task_get(int index) {
    if (index < 0 || index >= MAX_TASKS) {
        return (task_t*)0;
    }
    return &tasks[index];
}
