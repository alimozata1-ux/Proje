#include "desktop.h"
#include "../graphics.h"
#include "window.h"
#include "../apps/launcher.h"

static DesktopIcon icons[MAX_DESKTOP_ICONS];
static uint32_t icon_count=0;
static uint32_t icon_img[64]={0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,
0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00FFD24A};
static void open_notepad(void){ launch_notepad(); }
static void open_calc(void){ launch_calc(); }
static void open_docs(void){ launch_image_viewer(); }
static void open_terminal(void){ launch_terminal(); }
static void open_settings(void){ launch_settings(); }
static void open_ledger(void){ launch_ledger(); }
static void open_cmd(void){ launch_terminal(); }
static void open_cp(void){ launch_control_panel(); }
static void add_icon(const char*t,int x,int y, void (*cb)(void)){ DesktopIcon*i=&icons[icon_count++]; i->id=icon_count; int j=0; for(;j<31&&t[j];++j)i->title[j]=t[j]; i->title[j]=0; i->x=x;i->y=y;i->width=64;i->height=64;i->is_selected=0;i->icon_data=icon_img;i->on_double_click=cb;i->last_click_tick=0; }

void desktop_init(void){ icon_count=0; add_icon("Not Defteri",16,40,open_notepad); add_icon("Hesap Makinesi",16,130,open_calc); add_icon("Resimlerim",16,220,open_docs); add_icon("Terminal",16,310,open_terminal); add_icon("Ayarlar",16,400,open_settings); add_icon("Borc Defteri",16,490,open_ledger); add_icon("Komut Istemi",96,40,open_cmd); add_icon("Denetim Masasi",96,130,open_cp); }
void desktop_draw(void){ for(uint32_t n=0;n<icon_count;n++){ DesktopIcon*i=&icons[n]; if(i->is_selected) draw_rect(i->x-2,i->y-2,i->width+4,i->height+4,0x000053E2); for(int py=0;py<8;py++) for(int px=0;px<8;px++) put_pixel(i->x+px*6,i->y+py*6,i->icon_data[py*8+px]); } }
void desktop_handle_click(int mx,int my,uint32_t tick){
    int hit=-1;
    for(uint32_t n=0;n<icon_count;n++){ DesktopIcon*i=&icons[n]; if(mx>=i->x&&my>=i->y&&mx<i->x+i->width&&my<i->y+i->height){ hit=(int)n; break; }}
    for(uint32_t n=0;n<icon_count;n++) icons[n].is_selected=0;
    if(hit<0) return;
    DesktopIcon*i=&icons[hit]; i->is_selected=1;
    if(tick - i->last_click_tick <= 25){ if(i->on_double_click) i->on_double_click(); i->last_click_tick=0; }
    else i->last_click_tick=tick;
}
