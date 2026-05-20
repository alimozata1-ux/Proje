#include "supabase_client.h"
#include "net_stack.h"

static char g_url[128];
static char g_key[192];
static char g_last_http[1024];

static void cpy(char *d,const char *s,uint32_t n){uint32_t i=0;for(;i+1<n&&s&&s[i];i++)d[i]=s[i];d[i]=0;}
static uint32_t slen(const char *s){uint32_t n=0;while(s&&s[n])n++;return n;}

void supabase_init(const char *url,const char *anon_key){ cpy(g_url,url,sizeof(g_url)); cpy(g_key,anon_key,sizeof(g_key)); }

int supabase_insert(const char *table,const char *json_data){
    if(!table||!json_data) return -1;
    uint32_t p=0; const char *m="POST /rest/v1/"; for(uint32_t i=0;m[i];i++) g_last_http[p++]=m[i];
    for(uint32_t i=0;table[i];i++) g_last_http[p++]=table[i];
    const char *h=" HTTP/1.1\r\nHost: "; for(uint32_t i=0;h[i];i++) g_last_http[p++]=h[i];
    for(uint32_t i=0;g_url[i];i++) g_last_http[p++]=g_url[i];
    const char *k="\r\nContent-Type: application/json\r\napikey: "; for(uint32_t i=0;k[i];i++) g_last_http[p++]=k[i];
    for(uint32_t i=0;g_key[i];i++) g_last_http[p++]=g_key[i];
    const char *a="\r\nAuthorization: Bearer "; for(uint32_t i=0;a[i];i++) g_last_http[p++]=a[i];
    for(uint32_t i=0;g_key[i];i++) g_last_http[p++]=g_key[i];
    const char *e="\r\n\r\n"; for(uint32_t i=0;e[i];i++) g_last_http[p++]=e[i];
    for(uint32_t i=0;json_data[i];i++) g_last_http[p++]=json_data[i]; g_last_http[p]=0;
    g_net_activity_blink=8; return 0;
}

int supabase_select(const char *table,const char *sel,char *out,uint32_t out_len){
    if(!table||!sel||!out||out_len<8) return -1;
    (void)supabase_insert(table,"{}");
    cpy(out,"[{\"status\":\"queued\"}]",out_len);
    return 0;
}
