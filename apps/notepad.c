#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include "../kernel/fs/fat.h"
#include <stdint.h>

typedef struct { Window *win; TextBox *tb; Button *save_btn; } NotepadApp;
static NotepadApp g_np;
static uint8_t g_save_sector[512];

static void np_save(void){
    for(int i=0;i<512;i++) g_save_sector[i]=0;
    for(uint32_t i=0;i<g_np.tb->buffer_index && i<511;i++) g_save_sector[i]=(uint8_t)g_np.tb->text_buffer[i];
    (void)ramdisk_write_sector(120, g_save_sector);
}

void notepad_open(void){
    g_np.win=window_create("Not Defteri - Adsiz",100,80,520,360,1);
    g_np.tb=textbox_create(8,36,504,316);
    g_np.save_btn=button_create(8,8,64,22,"Kaydet",np_save);
}
void notepad_draw(void){ if(!g_np.win) return; widget_draw_button(g_np.save_btn,g_np.win->x,g_np.win->y); widget_draw_textbox(g_np.tb,g_np.win->x,g_np.win->y);} 
void notepad_click(int mx,int my){ if(!g_np.win) return; if(widget_button_hit(g_np.save_btn,mx,my,g_np.win->x,g_np.win->y) && g_np.save_btn->on_click) g_np.save_btn->on_click(); g_np.tb->is_focused=widget_textbox_hit(g_np.tb,mx,my,g_np.win->x,g_np.win->y); }
void notepad_key(char c){ if(g_np.tb) widget_textbox_input(g_np.tb,c); }
