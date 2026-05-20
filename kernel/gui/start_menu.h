#ifndef START_MENU_H
#define START_MENU_H
#include <stdint.h>

typedef struct {
    uint8_t is_open;
    int x,y,width,height;
    int hover_item;
} StartMenu;

void start_menu_init(void);
StartMenu *start_menu_get(void);
void start_menu_toggle(void);
void start_menu_draw(void);
int start_menu_handle_click(int mx,int my);
void start_menu_handle_hover(int mx,int my);

#endif
