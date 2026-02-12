#ifndef SCHEDULER_H
#define SCHEDULER_H

void scheduler_init(void);
void scheduler_tick(void);
void timer_irq_handler(void);
void keyboard_irq_dispatch(void);

#endif
