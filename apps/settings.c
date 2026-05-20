#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include "../kernel/net/net_stack.h"
#include <stdint.h>

static Window *win;
static TextBox *name_tb,*ip_tb,*mac_tb;
static Button *apply_btn,*about_btn;

static void set_text(TextBox *t, const char *s){ t->buffer_index=0; for(uint32_t i=0;s[i]&&i<255;i++) t->text_buffer[t->buffer_index++]=s[i]; t->text_buffer[t->buffer_index]=0; }
static void apply_settings(void){
    if(!ip_tb||!mac_tb) return;
    int a=10,b=0,c=2,d=15; /* basit: sabit örnek */
    g_net_ip[0]=a; g_net_ip[1]=b; g_net_ip[2]=c; g_net_ip[3]=d;
    g_net_mac[0]=0x52; g_net_mac[1]=0x54; g_net_mac[2]=0x00; g_net_mac[3]=0x12; g_net_mac[4]=0x34; g_net_mac[5]=0x56;
}
static void about_info(void){ set_text(name_tb,"LunaOS XP Ayarlar - v1.0"); }

void settings_open(void){
    win=window_create("Denetim Masasi - Ayarlar",180,90,620,420,1);
    name_tb=textbox_create(140,50,300,24); ip_tb=textbox_create(140,100,300,24); mac_tb=textbox_create(140,150,300,24);
    apply_btn=button_create(140,200,120,28,"Uygula",apply_settings); about_btn=button_create(280,200,120,28,"Hakkinda",about_info);
    set_text(name_tb,"Osman"); set_text(ip_tb,"10.0.2.15"); set_text(mac_tb,"52:54:00:12:34:56");
}
void settings_draw(void){ if(!win)return; widget_draw_textbox(name_tb,win->x,win->y); widget_draw_textbox(ip_tb,win->x,win->y); widget_draw_textbox(mac_tb,win->x,win->y); widget_draw_button(apply_btn,win->x,win->y); widget_draw_button(about_btn,win->x,win->y); }
void settings_click(int mx,int my){ if(!win)return; name_tb->is_focused=widget_textbox_hit(name_tb,mx,my,win->x,win->y); ip_tb->is_focused=widget_textbox_hit(ip_tb,mx,my,win->x,win->y); mac_tb->is_focused=widget_textbox_hit(mac_tb,mx,my,win->x,win->y); if(widget_button_hit(apply_btn,mx,my,win->x,win->y)&&apply_btn->on_click)apply_btn->on_click(); if(widget_button_hit(about_btn,mx,my,win->x,win->y)&&about_btn->on_click)about_btn->on_click(); }
void settings_key(char c){ if(name_tb&&name_tb->is_focused) widget_textbox_input(name_tb,c); if(ip_tb&&ip_tb->is_focused) widget_textbox_input(ip_tb,c); if(mac_tb&&mac_tb->is_focused) widget_textbox_input(mac_tb,c); }
