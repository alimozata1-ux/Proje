#ifndef FS_H
#define FS_H

#include "types.h"

#define FS_MAX_FILES 32
#define FS_NAME_MAX 24
#define FS_DATA_MAX 512

typedef enum {
    FS_FILE_TEXT = 0,
    FS_FILE_EXEC = 1
} fs_file_type_t;

typedef struct {
    int used;
    fs_file_type_t type;
    char name[FS_NAME_MAX];
    u32 size;
    char data[FS_DATA_MAX];
} fs_node_t;

void fs_init(void);
int fs_create(const char* name);
int fs_create_exec(const char* name, const char* payload);
int fs_delete(const char* name);
int fs_write(const char* name, const char* text);
int fs_append(const char* name, const char* text);
int fs_read(const char* name, char* out, u32 out_cap);
int fs_exists(const char* name);
int fs_is_exec(const char* name);
int fs_count(void);
fs_node_t* fs_get(int index);

#endif
