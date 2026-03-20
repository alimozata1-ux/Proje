#ifndef KONE_KFS_H
#define KONE_KFS_H

#include "../lib/kone_types.h"

#define KFS_MAX_NODES 64
#define KFS_NAME_MAX  32
#define KFS_DATA_MAX  256

typedef enum {
    KFS_NODE_FILE = 1,
    KFS_NODE_DIR  = 2
} kfs_node_type_t;

typedef struct {
    int used;
    kfs_node_type_t type;
    int parent;
    char name[KFS_NAME_MAX];
    k_u8 data[KFS_DATA_MAX];
    k_u32 size;
} kfs_node_t;

void kfs_init(void);
int kfs_mkdir(const char *name);
int kfs_create(const char *name, const void *data, k_u32 len);

#endif
