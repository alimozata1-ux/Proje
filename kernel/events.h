#ifndef KONE_EVENTS_H
#define KONE_EVENTS_H

typedef enum {
    EVT_NONE = 0,
    EVT_TOUCH,
    EVT_KEY,
    EVT_WINDOW
} event_type_t;

void event_system_init(void);
void event_push(event_type_t ev);

event_type_t event_poll(void);

#endif
