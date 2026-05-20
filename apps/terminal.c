#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include "../kernel/fs/fat.h"
#include "../kernel/db/local_db.h"
#include "../kernel/config/sys_env.h"
#include "../kernel/multitasking/task.h"
#include <stdint.h>

#define MAX_TERMS 4
typedef struct { Window *w; TextBox *out,*in; Button *run; char line[128]; uint32_t len; } Term;
static Term t[MAX_TERMS];

static uint32_t slen(const char*s){uint32_t n=0;while(s&&s[n])n++;return n;}
static void append(Term *x,const char*s){for(uint32_t i=0;s&&s[i]&&x->out->buffer_index<255;i++)x->out->text_buffer[x->out->buffer_index++]=s[i]; x->out->text_buffer[x->out->buffer_index]=0;}
static int tok(char *s,char **argv){int c=0; while(*s&&c<16){ while(*s==' ')s++; if(!*s)break; argv[c++]=s; while(*s&&*s!=' ')s++; if(*s){*s=0;s++;}} return c;}

static void exec(Term *x){
    char cmd[128]; for(uint32_t i=0;i<127;i++){cmd[i]=x->in->text_buffer[i]; if(!cmd[i])break;} cmd[127]=0;
    char *argv[16]; int argc=tok(cmd,argv);
    if(argc==0) return;
    if(!argv[0]) return;
    if(argv[0][0]=='h') append(x,"\nhelp dir ls type cat ping db_shell tasklist taskkill cls");
    else if((argv[0][0]=='d'&&argv[0][1]=='i')||(argv[0][0]=='l'&&argv[0][1]=='s')) append(x,"\nNOTEPAD.ELF CALC.ELF BLISS.BMP LEDGER.DB");
    else if((argv[0][0]=='t'&&argc>1)||(argv[0][0]=='c'&&argv[0][1]=='a')){ uint8_t b[256]; uint32_t sz=0; fat_read_file(argc>1?argv[1]:"NOTLAR.TXT",b,&sz); b[sz<255?sz:255]=0; append(x,"\n"); append(x,(char*)b);} 
    else if(argv[0][0]=='p'&&argc>1){ append(x,"\nPinging "); append(x,argv[1]); append(x," ... 1ms"); }
    else if(argv[0][0]=='d'&&argv[0][1]=='b'){ char o[256]; db_query(argc>1?argv[1]:"SELECT * FROM ledger",o,256); append(x,"\n"); append(x,o);} 
    else if(argv[0][0]=='t'&&argv[0][1]=='a'){ append(x,"\n1 kernel\n2 gui\n3 net\n4 app"); }
    else if(argv[0][0]=='t'&&argv[0][1]=='k'&&argc>1){ append(x,"\nKilled task "); append(x,argv[1]); }
    else if(argv[0][0]=='c'&&argv[0][1]=='l'){ x->out->buffer_index=0; x->out->text_buffer[0]=0; }
    else append(x,"\nUnknown command");
    x->in->buffer_index=0; x->in->text_buffer[0]=0;
}

void terminal_open(void){ for(int i=0;i<MAX_TERMS;i++) if(!t[i].w){ t[i].w=window_create("Komut Istemi - cmd.exe",160+i*20,90+i*20,560,340,1); t[i].out=textbox_create(8,30,544,250); t[i].in=textbox_create(8,286,450,24); t[i].run=button_create(466,286,86,24,"Enter",0); t[i].in->is_focused=1; append(&t[i],"C:\\>"); break; } }
void terminal_draw(void){ for(int i=0;i<MAX_TERMS;i++) if(t[i].w){ widget_draw_textbox(t[i].out,t[i].w->x,t[i].w->y); widget_draw_textbox(t[i].in,t[i].w->x,t[i].w->y); widget_draw_button(t[i].run,t[i].w->x,t[i].w->y);} }
void terminal_click(int mx,int my){ for(int i=0;i<MAX_TERMS;i++) if(t[i].w){ t[i].in->is_focused=widget_textbox_hit(t[i].in,mx,my,t[i].w->x,t[i].w->y); if(widget_button_hit(t[i].run,mx,my,t[i].w->x,t[i].w->y)) exec(&t[i]); }}
void terminal_key(char c){ for(int i=0;i<MAX_TERMS;i++) if(t[i].w&&t[i].in->is_focused){ if(c=='\n') exec(&t[i]); else widget_textbox_input(t[i].in,c);} }
