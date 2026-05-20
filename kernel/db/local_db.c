#include "local_db.h"
#include "../storage/ramdisk.h"

static local_db_t g_db;
static uint8_t g_loaded=0;

static uint32_t slen(const char *s){uint32_t n=0; while(s&&s[n]) n++; return n;}
static int starts(const char *s,const char *p){uint32_t i=0; for(;p[i];i++) if(s[i]!=p[i]) return 0; return 1;}
static void cpy(char *d,const char *s,uint32_t n){uint32_t i=0; for(;i+1<n&&s&&s[i];i++) d[i]=s[i]; d[i]=0;}

static void db_flush(void){
    const uint8_t *raw=(const uint8_t*)&g_db;
    for(uint32_t sec=0; sec<64; ++sec){ uint8_t b[512]; for(uint32_t i=0;i<512;i++) b[i]=raw[sec*512+i]; ramdisk_write_sector(300+sec,b); }
}
static void db_load(void){
    uint8_t *raw=(uint8_t*)&g_db;
    for(uint32_t sec=0; sec<64; ++sec){ uint8_t b[512]; ramdisk_read_sector(300+sec,b); for(uint32_t i=0;i<512;i++) raw[sec*512+i]=b[i]; }
}

int db_open(const char *filename){
    if(!filename) return -1;
    if(!g_loaded){ db_load(); g_loaded=1; }
    if(g_db.name[0]==0){ cpy(g_db.name,filename,sizeof(g_db.name)); g_db.row_count=0; db_flush(); }
    return 0;
}

int db_query(const char *q, char *out, uint32_t out_len){
    if(!q||!out||out_len==0) return -1;
    out[0]=0;
    if(starts(q,"INSERT INTO")){
        const char *v=q; while(*v && *v!='(') v++; if(!*v) return -1; v++;
        if(g_db.row_count>=DB_MAX_ROWS) return -1;
        char *row=g_db.rows[g_db.row_count++];
        uint32_t i=0; while(v[i]&&v[i]!=')'&&i<DB_MAX_ROW_LEN-1){ row[i]=v[i]; i++; } row[i]=0;
        db_flush(); cpy(out,"OK",out_len); return 0;
    }
    if(starts(q,"SELECT * FROM")){
        uint32_t pos=0;
        for(uint32_t r=0;r<g_db.row_count;r++){
            const char *row=g_db.rows[r];
            for(uint32_t i=0; row[i] && pos+2<out_len; i++) out[pos++]=row[i];
            if(pos+2<out_len){ out[pos++]='\n'; out[pos]=0; }
        }
        return 0;
    }
    cpy(out,"ERR",out_len);
    return -1;
}
