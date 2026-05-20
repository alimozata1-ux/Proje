#include "../net/net_stack.h"
#include <stdint.h>
#include "window.h"
#include "../graphics.h"

static void fill_rect(int x,int y,int w,int h,uint32_t c){ draw_rect(x,y,w,h,c); }

void draw_window_frame(Window *win) {
    if (!win || !win->active) return;
    fill_rect(win->x, win->y, win->width, win->height, 0x00ECECEC);
    for (int i=0;i<24;i++) {
        uint32_t blue = 0x000053E2 + ((uint32_t)i<<8);
        fill_rect(win->x, win->y+i, win->width, 1, blue);
    }
    fill_rect(win->x+4, win->y+4, 12, 12, 0x00FFFFFF);
    fill_rect(win->x + win->width - 22, win->y + 4, 16, 16, 0x00D32F2F);
    fill_rect(win->x + win->width - 18, win->y + 11, 8, 2, 0x00FFFFFF);
    for (int i=0;i<win->width;i++) { put_pixel(win->x+i, win->y, 0x006E89D6); put_pixel(win->x+i, win->y+win->height-1, 0x006E89D6); }
    for (int i=0;i<win->height;i++) { put_pixel(win->x, win->y+i, 0x006E89D6); put_pixel(win->x+win->width-1, win->y+i, 0x006E89D6); }
}

void draw_taskbar(void) {
    uint32_t w = graphics_width(), h = graphics_height();
    fill_rect(0, (int)h - 30, (int)w, 30, 0x00245EDD);
    fill_rect(0, (int)h - 30, 110, 30, 0x00388E3C);
    uint32_t tray = g_net_activity_blink ? 0x000053E2 : 0x00A0B8E8;
    fill_rect((int)w-54,(int)h-24,20,14,tray);
    fill_rect((int)w-30,(int)h-24,20,14,tray);
}
