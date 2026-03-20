#ifndef KONE_PLUGIN_H
#define KONE_PLUGIN_H

#include "../lib/kone_types.h"

#define PLUGIN_MAX 64

typedef struct {
    int used;
    char name[40];
    k_u32 version;
} plugin_info_t;

void plugin_system_init(void);
int plugin_register(const char *name, k_u32 version);

#endif
