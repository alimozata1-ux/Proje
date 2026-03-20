#include "kfs.h"
#include "../kernel/console.h"
#include "../lib/kone_string.h"

static kfs_node_t nodes[KFS_MAX_NODES];

static int alloc_node(void) {
    for (int i = 0; i < KFS_MAX_NODES; i++) {
        if (!nodes[i].used) {
            nodes[i].used = 1;
            return i;
        }
    }
    return -1;
}

void kfs_init(void) {
    k_memset(nodes, 0, sizeof(nodes));
    int root = alloc_node();
    nodes[root].type = KFS_NODE_DIR;
    nodes[root].parent = -1;
    k_memcpy(nodes[root].name, "/", 2);
    console_puts("[KFS] Root mounted\n");
}

int kfs_mkdir(const char *name) {
    int n = alloc_node();
    if (n < 0) return -1;
    nodes[n].type = KFS_NODE_DIR;
    nodes[n].parent = 0;
    k_memcpy(nodes[n].name, name, k_strlen(name) + 1);
    return n;
}

int kfs_create(const char *name, const void *data, k_u32 len) {
    if (len > KFS_DATA_MAX) return -1;
    int n = alloc_node();
    if (n < 0) return -1;
    nodes[n].type = KFS_NODE_FILE;
    nodes[n].parent = 0;
    nodes[n].size = len;
    k_memcpy(nodes[n].name, name, k_strlen(name) + 1);
    k_memcpy(nodes[n].data, data, len);
    return n;
}
