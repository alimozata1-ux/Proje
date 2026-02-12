#include "task.h"
#include "user.h"
#include "vga.h"

#define MAX_TASKS 3

static task_t tasks[MAX_TASKS];

static void task1(void) {
    vga_write_string("Task 1 (kernel) calisiyor\n");
}

static void task2(void) {
    vga_write_string("Task 2 (kernel) calisiyor\n");
}

void task_setup(void) {
    tasks[0].entry = task1;
    tasks[0].eip = (unsigned int)task1;
    tasks[0].esp = (unsigned int)&tasks[0].stack[4095];
    tasks[0].state = TASK_READY;
    tasks[0].mode = TASK_KERNEL;

    tasks[1].entry = task2;
    tasks[1].eip = (unsigned int)task2;
    tasks[1].esp = (unsigned int)&tasks[1].stack[4095];
    tasks[1].state = TASK_READY;
    tasks[1].mode = TASK_KERNEL;

    tasks[2].entry = user_mode_demo;
    tasks[2].eip = user_entry_point();
    tasks[2].esp = user_stack_top();
    tasks[2].state = TASK_READY;
    tasks[2].mode = TASK_USER;
}

task_t* task_list(void) {
    return tasks;
}

int task_count(void) {
    return MAX_TASKS;
}
