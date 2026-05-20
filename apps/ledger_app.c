#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include "../kernel/db/local_db.h"
#include "../kernel/net/supabase_client.h"

static Window *win; static TextBox *name_tb,*amt_tb,*desc_tb,*list_tb; static Button *save_btn,*list_btn;
static volatile int bg_state=0; static char bg_query[256];

static void cpy(char *d,const char*s,int n){int i=0;for(;i+1<n&&s&&s[i];i++)d[i]=s[i];d[i]=0;}

static void ledger_bg_task(void){
    char out[512];
    db_query(bg_query,out,sizeof(out));
    supabase_insert("ledger","{\"sync\":true}");
    bg_state=0;
}

static void on_save(void){
    char q[256];
    cpy(q,"INSERT INTO ledger VALUES (",256);
    int p=26; const char*arr[3]={name_tb->text_buffer,amt_tb->text_buffer,desc_tb->text_buffer};
    for(int a=0;a<3;a++){ for(int i=0;arr[a][i]&&p<250;i++) q[p++]=arr[a][i]; if(a<2&&p<250) q[p++]=','; }
    if(p<255) q[p++]=')'; q[p]=0; cpy(bg_query,q,sizeof(bg_query)); bg_state=1; ledger_bg_task();
}
static void on_list(void){ char out[512]; db_query("SELECT * FROM ledger",out,sizeof(out)); cpy(list_tb->text_buffer,out,256); list_tb->buffer_index=0; while(list_tb->text_buffer[list_tb->buffer_index]) list_tb->buffer_index++; }

void ledger_open(void){
    db_open("LEDGER.DB"); supabase_init("supabase.local","anon-key");
    win=window_create("Borc Defteri",240,90,560,420,1);
    name_tb=textbox_create(20,40,220,24); amt_tb=textbox_create(260,40,120,24); desc_tb=textbox_create(20,80,360,24);
    list_tb=textbox_create(20,130,520,230);
    save_btn=button_create(400,40,120,28,"Kaydet",on_save); list_btn=button_create(400,80,120,28,"Listele",on_list);
}
void ledger_draw(void){ if(!win)return; widget_draw_textbox(name_tb,win->x,win->y); widget_draw_textbox(amt_tb,win->x,win->y); widget_draw_textbox(desc_tb,win->x,win->y); widget_draw_textbox(list_tb,win->x,win->y); widget_draw_button(save_btn,win->x,win->y); widget_draw_button(list_btn,win->x,win->y); }
void ledger_click(int mx,int my){ if(!win)return; name_tb->is_focused=widget_textbox_hit(name_tb,mx,my,win->x,win->y); amt_tb->is_focused=widget_textbox_hit(amt_tb,mx,my,win->x,win->y); desc_tb->is_focused=widget_textbox_hit(desc_tb,mx,my,win->x,win->y); if(widget_button_hit(save_btn,mx,my,win->x,win->y)&&save_btn->on_click)save_btn->on_click(); if(widget_button_hit(list_btn,mx,my,win->x,win->y)&&list_btn->on_click)list_btn->on_click(); }
void ledger_key(char c){ if(name_tb&&name_tb->is_focused) widget_textbox_input(name_tb,c); if(amt_tb&&amt_tb->is_focused) widget_textbox_input(amt_tb,c); if(desc_tb&&desc_tb->is_focused) widget_textbox_input(desc_tb,c); }
