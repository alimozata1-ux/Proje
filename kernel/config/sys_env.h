#ifndef SYS_ENV_H
#define SYS_ENV_H
#include <stdint.h>

typedef struct {
    uint8_t ip[4], subnet[4], gateway[4];
    char active_user[32];
    uint32_t desktop_color;
    uint32_t fps_limit;
    char supabase_url[128];
    char supabase_key[192];
} SystemConfig;

extern SystemConfig g_syscfg;
void sys_env_init(void);
void sys_env_set_ip(uint8_t a,uint8_t b,uint8_t c,uint8_t d);
void sys_env_set_theme(uint32_t color);
void sys_env_set_fps(uint32_t fps);
void sys_env_set_supabase(const char *url,const char *key);

#endif
