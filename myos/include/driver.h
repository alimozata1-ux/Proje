#ifndef DRIVER_H
#define DRIVER_H

#define DRIVER_MAX 24
#define DRIVER_NAME_MAX 24
#define DRIVER_DESC_MAX 64

typedef struct {
    int used;
    int installed;
    char name[DRIVER_NAME_MAX];
    char description[DRIVER_DESC_MAX];
} driver_info_t;

void driver_init(void);
int driver_count(void);
int driver_find(const char* query, int* indices, int cap);
driver_info_t* driver_get(int index);
int driver_install(const char* name);
int driver_uninstall(const char* name);
int driver_installed_count(void);
driver_info_t* driver_get_by_name(const char* name);

#endif
