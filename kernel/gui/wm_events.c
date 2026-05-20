#include <stdint.h>
#include "window.h"

extern int32_t mouse_x;
extern int32_t mouse_y;
extern uint8_t mouse_left;

static uint8_t prev_left = 0;
static uint8_t dragging = 0;
static uint32_t drag_win_id = 0;
static int drag_off_x = 0, drag_off_y = 0;

void wm_handle_events(void) {
    Window *top = window_get_top_at(mouse_x, mouse_y);

    if (mouse_left && !prev_left) {
        if (top) {
            window_bring_to_front(top->id);
            int title_hit = (mouse_y >= top->y && mouse_y < top->y + 24);
            int close_hit = (mouse_x >= top->x + top->width - 22 && mouse_x < top->x + top->width - 6 &&
                             mouse_y >= top->y + 4 && mouse_y < top->y + 20);
            if (close_hit) {
                window_destroy(top->id);
            } else if (title_hit && top->is_draggable) {
                dragging = 1;
                drag_win_id = top->id;
                drag_off_x = mouse_x - top->x;
                drag_off_y = mouse_y - top->y;
            }
        }
    }

    if (!mouse_left) {
        dragging = 0;
        drag_win_id = 0;
    }

    if (dragging) {
        for (uint32_t i=0;i<window_count();i++) {
            Window *w = window_get_by_index(i);
            if (w && w->id == drag_win_id) {
                w->x = mouse_x - drag_off_x;
                w->y = mouse_y - drag_off_y;
                break;
            }
        }
    }

    prev_left = mouse_left;
}
