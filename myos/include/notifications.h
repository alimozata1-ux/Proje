#ifndef NOTIFICATIONS_H
#define NOTIFICATIONS_H

#define NOTIFY_MAX 32
#define NOTIFY_TEXT_MAX 80

typedef struct {
    int used;
    int read;
    char text[NOTIFY_TEXT_MAX];
} notification_t;

void notifications_init(void);
void notifications_push(const char* text);
int notifications_unread_count(void);
int notifications_count(void);
void notifications_mark_all_read(void);
void notifications_clear(void);
notification_t* notifications_get(int index);

#endif
