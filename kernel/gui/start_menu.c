#include "start_menu.h"
#include "../graphics.h"

static StartMenu g_menu;
void start_menu_init(void){ g_menu.is_open=0; g_menu.width=260; g_menu.height=360; g_menu.x=0; g_menu.y=(int)graphics_height()-30-g_menu.height; g_menu.hover_item=-1; }
StartMenu *start_menu_get(void){ return &g_menu; }
void start_menu_toggle(void){ g_menu.is_open=!g_menu.is_open; }
void start_menu_draw(void){ if(!g_menu.is_open) return; draw_rect(g_menu.x,g_menu.y,g_menu.width,g_menu.height,0x00ECE9D8); draw_rect(g_menu.x,g_menu.y,96,g_menu.height,0x000053E2); draw_rect(g_menu.x+96,g_menu.y,g_menu.width-96,g_menu.height,0x00CFE3FF); draw_rect(g_menu.x+110,g_menu.y+16,120,60,0x00FFFFFF); if(g_menu.hover_item==0) draw_rect(g_menu.x+100,g_menu.y+90,145,24,0x006FA8FF); if(g_menu.hover_item==1) draw_rect(g_menu.x+100,g_menu.y+320,145,24,0x006FA8FF); draw_rect(g_menu.x+100,g_menu.y+320,145,24,0x00388E3C); }
int start_menu_handle_click(int mx,int my){ if(!g_menu.is_open) return 0; if(mx<g_menu.x||my<g_menu.y||mx>=g_menu.x+g_menu.width||my>=g_menu.y+g_menu.height){ g_menu.is_open=0; return 1; } if(mx>=g_menu.x+100&&mx<g_menu.x+245&&my>=g_menu.y+320&&my<g_menu.y+344){ g_menu.is_open=0; }
 return 1; }
void start_menu_handle_hover(int mx,int my){ g_menu.hover_item=-1; if(!g_menu.is_open) return; if(mx>=g_menu.x+100&&mx<g_menu.x+245&&my>=g_menu.y+90&&my<g_menu.y+114) g_menu.hover_item=0; if(mx>=g_menu.x+100&&mx<g_menu.x+245&&my>=g_menu.y+320&&my<g_menu.y+344) g_menu.hover_item=1; }
