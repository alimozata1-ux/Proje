#include "window.h"

static Window windows[MAX_WINDOWS];
static uint32_t order[MAX_WINDOWS];
static uint32_t win_count = 0;
static uint32_t next_id = 1;
static uint32_t buffers[MAX_WINDOWS][320*200];

static void str_copy(char *dst, const char *src, uint32_t max) {
    uint32_t i = 0;
    for (; i + 1 < max && src && src[i]; ++i) dst[i] = src[i];
    dst[i] = '\0';
}

void window_manager_init(void) {
    win_count = 0; next_id = 1;
    for (uint32_t i=0;i<MAX_WINDOWS;i++) { windows[i].active = 0; order[i]=0; }
}

Window *window_create(const char *title, int x, int y, int w, int h, uint8_t draggable) {
    if (win_count >= MAX_WINDOWS) return 0;
    uint32_t slot = win_count;
    Window *win = &windows[slot];
    win->id = next_id++;
    str_copy(win->title, title, TITLE_MAX_LEN);
    win->x=x; win->y=y; win->width=w; win->height=h;
    win->is_draggable=draggable; win->is_focused=0; win->active=1;
    win->window_buffer = buffers[slot];
    for (int i=0;i<320*200;i++) win->window_buffer[i]=0x00F3F3F3;
    order[win_count++] = slot;
    return win;
}

void window_destroy(uint32_t id) {
    for (uint32_t i=0;i<win_count;i++) {
        Window *w = &windows[order[i]];
        if (w->active && w->id == id) {
            w->active = 0;
            for (uint32_t j=i;j+1<win_count;j++) order[j]=order[j+1];
            win_count--;
            return;
        }
    }
}

void window_bring_to_front(uint32_t id) {
    for (uint32_t i=0;i<win_count;i++) {
        if (windows[order[i]].id == id) {
            uint32_t idx = order[i];
            for (uint32_t j=i;j+1<win_count;j++) order[j]=order[j+1];
            order[win_count-1]=idx;
            return;
        }
    }
}

Window *window_get_top_at(int x, int y) {
    for (int i=(int)win_count-1;i>=0;i--) {
        Window *w = &windows[order[i]];
        if (!w->active) continue;
        if (x>=w->x && y>=w->y && x<(w->x+w->width) && y<(w->y+w->height)) return w;
    }
    return 0;
}
Window *window_get_by_index(uint32_t idx) { if (idx>=win_count) return 0; return &windows[order[idx]]; }
uint32_t window_count(void) { return win_count; }
