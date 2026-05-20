#ifndef SUPABASE_CLIENT_H
#define SUPABASE_CLIENT_H
#include <stdint.h>

void supabase_init(const char *url, const char *anon_key);
int supabase_insert(const char *table, const char *json_data);
int supabase_select(const char *table, const char *select_query, char *out, uint32_t out_len);

#endif
