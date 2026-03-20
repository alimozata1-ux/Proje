#include "shared_memory.h"
#include "memory.h"
#include "console.h"
#include "../lib/kone_string.h"

static shm_region_t regions[SHM_REGION_MAX];

void shm_init(void) {
    k_memset(regions, 0, sizeof(regions));
    console_puts("[X] Shared memory initialized\n");
}

static int find_region(const char *name) {
    for (int i = 0; i < SHM_REGION_MAX; i++) {
        if (regions[i].used && k_strcmp(regions[i].name, name) == 0) {
            return i;
        }
    }
    return -1;
}

int shm_create(const char *name, k_u32 owner_pid, k_u32 size) {
    if (!name || size == 0) return -1;
    if (find_region(name) >= 0) return -2;

    int slot = -1;
    for (int i = 0; i < SHM_REGION_MAX; i++) {
        if (!regions[i].used) {
            slot = i;
            break;
        }
    }
    if (slot < 0) return -3;

    k_u8 *mem = (k_u8 *)xk_kmalloc(size);
    if (!mem) return -4;

    regions[slot].used = 1;
    regions[slot].owner_pid = owner_pid;
    regions[slot].size = size;
    regions[slot].base = mem;

    size_t n = k_strlen(name);
    if (n >= SHM_NAME_MAX) n = SHM_NAME_MAX - 1;
    k_memcpy(regions[slot].name, name, n);
    regions[slot].name[n] = '\0';

    return 0;
}

shm_region_t *shm_open(const char *name) {
    int idx = find_region(name);
    if (idx < 0) return 0;
    return &regions[idx];
}

int shm_destroy(const char *name) {
    int idx = find_region(name);
    if (idx < 0) return -1;
    regions[idx].used = 0;
    return 0;
}
