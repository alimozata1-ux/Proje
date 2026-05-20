#ifndef WINDOW_H
#define WINDOW_H

#include <stdint.h>

#define MAX_WINDOWS 16
#define TITLE_MAX_LEN 32

typedef struct {
    uint32_t id;
    char title[TITLE_MAX_LEN];
    int x, y;
    int width, height;
    uint8_t is_draggable;
    uint8_t is_focused;
    uint32_t *window_buffer;
    uint8_t active;
} Window;

void window_manager_init(void);
Window *window_create(const char *title, int x, int y, int w, int h, uint8_t draggable);
void window_destroy(uint32_t id);
void window_bring_to_front(uint32_t id);
Window *window_get_top_at(int x, int y);
Window *window_get_by_index(uint32_t idx);
uint32_t window_count(void);

#endif
