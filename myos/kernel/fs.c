#include "fs.h"
#include "logger.h"
#include "memory.h"
#include "string.h"

static fs_node_t fs_nodes[FS_MAX_FILES];

static int fs_find_index(const char* name) {
    int i;
    for (i = 0; i < FS_MAX_FILES; i++) {
        if (fs_nodes[i].used && kstrcmp(fs_nodes[i].name, name) == 0) {
            return i;
        }
    }
    return -1;
}

static int fs_find_free_index(void) {
    int i;
    for (i = 0; i < FS_MAX_FILES; i++) {
        if (!fs_nodes[i].used) {
            return i;
        }
    }
    return -1;
}

void fs_init(void) {
    kmemset(fs_nodes, 0, sizeof(fs_nodes));
    (void)fs_create_exec("superx323", "#!/myos-exec\necho superx323 launched\n");
    log_info("fs", "ramfs initialized");
}

int fs_create(const char* name) {
    int idx;
    size_t len;

    if (!name || !name[0]) {
        return -1;
    }

    if (fs_find_index(name) >= 0) {
        return -2;
    }

    len = kstrlen(name);
    if (len >= FS_NAME_MAX) {
        return -3;
    }

    idx = fs_find_free_index();
    if (idx < 0) {
        return -4;
    }

    fs_nodes[idx].used = 1;
    fs_nodes[idx].type = FS_FILE_TEXT;
    kstrcpy(fs_nodes[idx].name, name);
    fs_nodes[idx].size = 0;
    fs_nodes[idx].data[0] = '\0';
    return 0;
}

int fs_create_exec(const char* name, const char* payload) {
    int rc = fs_create(name);
    int idx;
    if (rc != 0) {
        return rc;
    }

    idx = fs_find_index(name);
    if (idx < 0) {
        return -1;
    }

    fs_nodes[idx].type = FS_FILE_EXEC;
    if (payload) {
        return fs_write(name, payload);
    }

    return 0;
}

int fs_delete(const char* name) {
    int idx = fs_find_index(name);
    if (idx < 0) {
        return -1;
    }
    kmemset(&fs_nodes[idx], 0, sizeof(fs_node_t));
    return 0;
}

int fs_write(const char* name, const char* text) {
    int idx = fs_find_index(name);
    size_t len;

    if (idx < 0) {
        return -1;
    }

    len = kstrlen(text);
    if (len >= FS_DATA_MAX) {
        return -2;
    }

    kstrcpy(fs_nodes[idx].data, text);
    fs_nodes[idx].size = (u32)len;
    return 0;
}

int fs_append(const char* name, const char* text) {
    int idx = fs_find_index(name);
    size_t old_len;
    size_t add_len;

    if (idx < 0) {
        return -1;
    }

    old_len = kstrlen(fs_nodes[idx].data);
    add_len = kstrlen(text);
    if (old_len + add_len >= FS_DATA_MAX) {
        return -2;
    }

    kstrcpy(fs_nodes[idx].data + old_len, text);
    fs_nodes[idx].size = (u32)(old_len + add_len);
    return 0;
}

int fs_read(const char* name, char* out, u32 out_cap) {
    int idx = fs_find_index(name);
    size_t len;

    if (idx < 0) {
        return -1;
    }

    len = kstrlen(fs_nodes[idx].data);
    if (out_cap == 0 || len + 1 > out_cap) {
        return -2;
    }

    kstrcpy(out, fs_nodes[idx].data);
    return (int)len;
}

int fs_exists(const char* name) {
    return fs_find_index(name) >= 0;
}

int fs_is_exec(const char* name) {
    int idx = fs_find_index(name);
    if (idx < 0) {
        return 0;
    }
    return fs_nodes[idx].type == FS_FILE_EXEC;
}

int fs_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < FS_MAX_FILES; i++) {
        if (fs_nodes[i].used) {
            count++;
        }
    }
    return count;
}

fs_node_t* fs_get(int index) {
    if (index < 0 || index >= FS_MAX_FILES) {
        return (fs_node_t*)0;
    }
    return &fs_nodes[index];
}
