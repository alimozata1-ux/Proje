#include "notifications.h"
#include "memory.h"
#include "string.h"

static notification_t g_notifications[NOTIFY_MAX];

void notifications_init(void) {
    kmemset(g_notifications, 0, sizeof(g_notifications));
}

static int find_free_slot(void) {
    int i;
    for (i = 0; i < NOTIFY_MAX; i++) {
        if (!g_notifications[i].used) {
            return i;
        }
    }
    return -1;
}

static void shift_left(void) {
    int i;
    for (i = 1; i < NOTIFY_MAX; i++) {
        g_notifications[i - 1] = g_notifications[i];
    }
    kmemset(&g_notifications[NOTIFY_MAX - 1], 0, sizeof(notification_t));
}

void notifications_push(const char* text) {
    int slot = find_free_slot();
    if (slot < 0) {
        shift_left();
        slot = NOTIFY_MAX - 1;
    }

    g_notifications[slot].used = 1;
    g_notifications[slot].read = 0;
    kstrncpy(g_notifications[slot].text, text ? text : "(empty)", NOTIFY_TEXT_MAX - 1);
    g_notifications[slot].text[NOTIFY_TEXT_MAX - 1] = '\0';
}

int notifications_unread_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < NOTIFY_MAX; i++) {
        if (g_notifications[i].used && !g_notifications[i].read) {
            count++;
        }
    }
    return count;
}

int notifications_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < NOTIFY_MAX; i++) {
        if (g_notifications[i].used) {
            count++;
        }
    }
    return count;
}

void notifications_mark_all_read(void) {
    int i;
    for (i = 0; i < NOTIFY_MAX; i++) {
        if (g_notifications[i].used) {
            g_notifications[i].read = 1;
        }
    }
}

void notifications_clear(void) {
    kmemset(g_notifications, 0, sizeof(g_notifications));
}

notification_t* notifications_get(int index) {
    if (index < 0 || index >= NOTIFY_MAX) {
        return (notification_t*)0;
    }
    if (!g_notifications[index].used) {
        return (notification_t*)0;
    }
    return &g_notifications[index];
}
