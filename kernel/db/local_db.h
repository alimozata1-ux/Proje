#ifndef LOCAL_DB_H
#define LOCAL_DB_H
#include <stdint.h>

#define DB_MAX_ROWS 128
#define DB_MAX_ROW_LEN 192

typedef struct {
    char name[64];
    uint32_t row_count;
    char rows[DB_MAX_ROWS][DB_MAX_ROW_LEN];
} local_db_t;

int db_open(const char *filename);
int db_query(const char *query_str, char *out_buf, uint32_t out_len);

#endif
