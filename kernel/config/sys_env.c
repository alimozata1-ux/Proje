#include "sys_env.h"
SystemConfig g_syscfg;
static void cpy(char *d,const char*s,uint32_t n){uint32_t i=0;for(;i+1<n&&s&&s[i];i++)d[i]=s[i];d[i]=0;}
void sys_env_init(void){ g_syscfg.ip[0]=10;g_syscfg.ip[1]=0;g_syscfg.ip[2]=2;g_syscfg.ip[3]=15; g_syscfg.subnet[0]=255;g_syscfg.subnet[1]=255;g_syscfg.subnet[2]=255;g_syscfg.subnet[3]=0; g_syscfg.gateway[0]=10;g_syscfg.gateway[1]=0;g_syscfg.gateway[2]=2;g_syscfg.gateway[3]=2; cpy(g_syscfg.active_user,"Osman",32); g_syscfg.desktop_color=0x00245EDD; g_syscfg.fps_limit=60; cpy(g_syscfg.supabase_url,"supabase.local",128); cpy(g_syscfg.supabase_key,"anon-key",192);} 
void sys_env_set_ip(uint8_t a,uint8_t b,uint8_t c,uint8_t d){ g_syscfg.ip[0]=a;g_syscfg.ip[1]=b;g_syscfg.ip[2]=c;g_syscfg.ip[3]=d; }
void sys_env_set_theme(uint32_t color){ g_syscfg.desktop_color=color; }
void sys_env_set_fps(uint32_t fps){ g_syscfg.fps_limit=fps?fps:60; }
void sys_env_set_supabase(const char *url,const char *key){ cpy(g_syscfg.supabase_url,url,128); cpy(g_syscfg.supabase_key,key,192); }
