#include "touch.h"
#include "../kernel/console.h"

static touch_point_t g_touch;

void yk_touch_init(void) {
    g_touch.x = 0;
    g_touch.y = 0;
    g_touch.down = 0;
    console_puts("[Y] Touch simulation initialized\n");
}

void yk_touch_update(int mouse_x, int mouse_y, int mouse_down) {
    g_touch.x = mouse_x;
    g_touch.y = mouse_y;
    g_touch.down = mouse_down;
}

touch_point_t yk_touch_get(void) {
    return g_touch;
}
