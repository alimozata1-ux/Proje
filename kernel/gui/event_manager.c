#include <stdint.h>
#include "start_menu.h"
#include "window.h"
#include "desktop.h"
#include "widgets.h"
#include "../apps/launcher.h"

extern int32_t mouse_x, mouse_y;
extern uint8_t mouse_left;
extern volatile char keyboard_last_char;
extern volatile uint32_t timer_ticks;

static uint8_t prev_left=0;
static TextBox *focused_tb=0;

void ui_event_pump(void){
    start_menu_handle_hover(mouse_x, mouse_y);
    if(mouse_left && !prev_left){
        if(start_menu_handle_click(mouse_x,mouse_y)){ prev_left=mouse_left; return; }
        int taskbar_y=768-30;
        if(mouse_y>=taskbar_y && mouse_x<110){ start_menu_toggle(); prev_left=mouse_left; return; }

        Window *top=window_get_top_at(mouse_x,mouse_y);
        if(top){ window_bring_to_front(top->id); prev_left=mouse_left; return; }

        desktop_handle_click(mouse_x,mouse_y,timer_ticks);
        apps_on_left_click(mouse_x,mouse_y);
    }

    if(mouse_left && prev_left) apps_on_right_click(mouse_x,mouse_y);
    if(keyboard_last_char && focused_tb){ widget_textbox_input(focused_tb, keyboard_last_char);}
    if(keyboard_last_char){ apps_on_key(keyboard_last_char); keyboard_last_char=0; }
    prev_left=mouse_left;
}
