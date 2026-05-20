#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include <stdint.h>

typedef struct { Window*win; TextBox*disp; Button*btn[16]; char expr[64]; uint32_t n; } CalcApp;
static CalcApp g;
static const char *labels[16] = {"7","8","9","/","4","5","6","*","1","2","3","-","0","C","=","+"};

static int eval_simple(const char*s){ int a=0,b=0; char op=0; int i=0; while(s[i]>='0'&&s[i]<='9'){a=a*10+s[i]-'0';i++;} op=s[i++]; while(s[i]>='0'&&s[i]<='9'){b=b*10+s[i]-'0';i++;} if(op=='+')return a+b; if(op=='-')return a-b; if(op=='*')return a*b; if(op=='/'&&b)return a/b; return a; }
static void on_btn_idx(int idx){ const char *l=labels[idx]; if(l[0]=='C'){ g.n=0; g.expr[0]=0; g.disp->buffer_index=0; g.disp->text_buffer[0]=0; return;} if(l[0]=='='){ int r=eval_simple(g.expr); g.n=0; char tmp[32]; int k=0,neg=0; if(r<0){neg=1;r=-r;} do{tmp[k++]='0'+(r%10); r/=10;}while(r); if(neg) tmp[k++]='-'; g.disp->buffer_index=0; for(int i=k-1;i>=0;i--) g.disp->text_buffer[g.disp->buffer_index++]=tmp[i]; g.disp->text_buffer[g.disp->buffer_index]=0; return;} if(g.n<63){ g.expr[g.n++]=l[0]; g.expr[g.n]=0; g.disp->text_buffer[g.disp->buffer_index++]=l[0]; g.disp->text_buffer[g.disp->buffer_index]=0; }}
void calc_open(void){ g.win=window_create("Hesap Makinesi",260,120,220,280,1); g.disp=textbox_create(10,10,200,30); g.disp->is_focused=0; g.n=0; g.expr[0]=0; int idx=0; for(int r=0;r<4;r++) for(int c=0;c<4;c++) g.btn[idx++]=button_create(10+c*50,50+r*50,44,44,labels[idx-1],0); }
void calc_draw(void){ if(!g.win)return; widget_draw_textbox(g.disp,g.win->x,g.win->y); for(int i=0;i<16;i++) widget_draw_button(g.btn[i],g.win->x,g.win->y); }
void calc_click(int mx,int my){ if(!g.win)return; for(int i=0;i<16;i++) if(widget_button_hit(g.btn[i],mx,my,g.win->x,g.win->y)) on_btn_idx(i); }
