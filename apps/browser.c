#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include <stdint.h>
static Window*win; static TextBox*addr; static Button*go; static char lines[8][64];
static void go_click(void){ const char*t="GET / HTTP/1.0"; for(int i=0;i<14;i++) lines[0][i]=t[i]; lines[0][14]=0; }
void browser_open(void){ win=window_create("Internet Explorer",180,70,620,420,1); addr=textbox_create(10,10,500,24); go=button_create(520,10,80,24,"Git",go_click);} 
void browser_draw(void){ if(!win)return; widget_draw_textbox(addr,win->x,win->y); widget_draw_button(go,win->x,win->y);} 
void browser_click(int mx,int my){ if(!win)return; if(widget_button_hit(go,mx,my,win->x,win->y)&&go->on_click)go->on_click(); addr->is_focused=widget_textbox_hit(addr,mx,my,win->x,win->y);} 
void browser_key(char c){ if(addr) widget_textbox_input(addr,c);} 
