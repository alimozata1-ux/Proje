#ifndef TASK_H
#define TASK_H

typedef enum {
    TASK_READY = 0,
    TASK_RUNNING = 1
} task_state_t;

typedef enum {
    TASK_KERNEL = 0,
    TASK_USER = 1
} task_mode_t;

typedef struct {
    unsigned int esp;
    unsigned int eip;
    task_state_t state;
    task_mode_t mode;
    void (*entry)(void);
    unsigned char stack[4096];
} task_t;

void task_setup(void);
task_t* task_list(void);
int task_count(void);

#endif
