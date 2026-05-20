#include "widgets.h"
#include "../graphics.h"

static Button g_buttons[MAX_BUTTONS]; static uint32_t g_btn_count=0;
static TextBox g_textboxes[MAX_TEXTBOXES]; static uint32_t g_tb_count=0;
static uint32_t gid=1;

static void strcp(char *d,const char*s,int n){int i=0; for(;i<n-1&&s&&s[i];++i)d[i]=s[i]; d[i]=0;}

void widgets_init(void){g_btn_count=0; g_tb_count=0; gid=1;}
Button *button_create(int x,int y,int w,int h,const char *label,void (*on_click)(void)){ if(g_btn_count>=MAX_BUTTONS)return 0; Button*b=&g_buttons[g_btn_count++]; b->id=gid++; b->x=x;b->y=y;b->width=w;b->height=h;b->is_pressed=0;b->on_click=on_click; strcp(b->label,label,32); return b; }
TextBox *textbox_create(int x,int y,int w,int h){ if(g_tb_count>=MAX_TEXTBOXES)return 0; TextBox*t=&g_textboxes[g_tb_count++]; t->id=gid++; t->x=x;t->y=y;t->width=w;t->height=h;t->buffer_index=0;t->is_focused=0;t->text_buffer[0]=0; return t; }

void widget_draw_button(Button *b, int ox, int oy){ if(!b)return; int x=ox+b->x,y=oy+b->y; draw_rect(x,y,b->width,b->height,0x00ECE9D8); draw_rect(x,y,b->width,2,0x000053E2); draw_rect(x,y,2,b->height,0x000053E2); if(b->is_pressed){ draw_rect(x+2,y+2,b->width-4,b->height-4,0x00D8D5C4);} else { draw_rect(x+2,y+2,b->width-4,b->height-4,0x00F8F8F8);} }
void widget_draw_textbox(TextBox *t, int ox, int oy){ if(!t)return; int x=ox+t->x,y=oy+t->y; draw_rect(x,y,t->width,t->height,0x00FFFFFF); uint32_t c=t->is_focused?0x000053E2:0x00666666; draw_rect(x,y,t->width,2,c); draw_rect(x,y,2,t->height,c); draw_rect(x,y+t->height-2,t->width,2,c); draw_rect(x+t->width-2,y,2,t->height,c); }
int widget_button_hit(Button *b, int px, int py, int ox, int oy){ int x=ox+b->x,y=oy+b->y; return px>=x&&py>=y&&px<x+b->width&&py<y+b->height; }
int widget_textbox_hit(TextBox *t, int px, int py, int ox, int oy){ int x=ox+t->x,y=oy+t->y; return px>=x&&py>=y&&px<x+t->width&&py<y+t->height; }
void widget_textbox_input(TextBox *t, char c){ if(!t||!t->is_focused||!c)return; if(c==8){ if(t->buffer_index>0){t->buffer_index--; t->text_buffer[t->buffer_index]=0;} return;} if(t->buffer_index<255){ t->text_buffer[t->buffer_index++]=c; t->text_buffer[t->buffer_index]=0; } }
