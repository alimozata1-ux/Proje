#ifndef KONE_SHARED_MEMORY_H
#define KONE_SHARED_MEMORY_H

#include "../lib/kone_types.h"

#define SHM_REGION_MAX 64
#define SHM_NAME_MAX   32

typedef struct {
    int used;
    char name[SHM_NAME_MAX];
    k_u32 owner_pid;
    k_u32 size;
    k_u8 *base;
} shm_region_t;

void shm_init(void);
int shm_create(const char *name, k_u32 owner_pid, k_u32 size);
shm_region_t *shm_open(const char *name);
int shm_destroy(const char *name);

#endif
