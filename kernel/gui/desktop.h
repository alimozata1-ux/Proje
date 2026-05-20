#ifndef DESKTOP_H
#define DESKTOP_H
#include <stdint.h>

#define MAX_DESKTOP_ICONS 16

typedef struct {
    uint32_t id;
    char title[32];
    int x,y,width,height;
    uint8_t is_selected;
    uint32_t *icon_data;
    void (*on_double_click)(void);
    uint32_t last_click_tick;
} DesktopIcon;

void desktop_init(void);
void desktop_draw(void);
void desktop_handle_click(int mx,int my,uint32_t tick);

#endif
