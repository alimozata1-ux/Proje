#include "driver.h"
#include "memory.h"
#include "string.h"

static driver_info_t g_drivers[DRIVER_MAX];

static void set_driver(int idx, const char* name, const char* desc) {
    g_drivers[idx].used = 1;
    g_drivers[idx].installed = 0;
    kstrncpy(g_drivers[idx].name, name, DRIVER_NAME_MAX - 1);
    g_drivers[idx].name[DRIVER_NAME_MAX - 1] = '\0';
    kstrncpy(g_drivers[idx].description, desc, DRIVER_DESC_MAX - 1);
    g_drivers[idx].description[DRIVER_DESC_MAX - 1] = '\0';
}

void driver_init(void) {
    kmemset(g_drivers, 0, sizeof(g_drivers));
    set_driver(0, "ps2kbd", "PS/2 keyboard input driver");
    set_driver(1, "vga", "VGA text output driver");
    set_driver(2, "pit", "Programmable interval timer driver");
    set_driver(3, "ramfs", "In-memory filesystem driver");
    set_driver(4, "netstub", "Educational network stack stub");
    set_driver(5, "soundstub", "Educational sound driver stub");

    g_drivers[0].installed = 1;
    g_drivers[1].installed = 1;
    g_drivers[2].installed = 1;
    g_drivers[3].installed = 1;
}

int driver_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < DRIVER_MAX; i++) {
        if (g_drivers[i].used) {
            count++;
        }
    }
    return count;
}

int driver_find(const char* query, int* indices, int cap) {
    int i;
    int out = 0;

    if (!query || !query[0]) {
        for (i = 0; i < DRIVER_MAX && out < cap; i++) {
            if (g_drivers[i].used) {
                indices[out++] = i;
            }
        }
        return out;
    }

    for (i = 0; i < DRIVER_MAX && out < cap; i++) {
        const char* n;
        const char* d;
        if (!g_drivers[i].used) {
            continue;
        }

        n = g_drivers[i].name;
        d = g_drivers[i].description;

        while (*n) {
            if (kstrncmp(n, query, kstrlen(query)) == 0) {
                indices[out++] = i;
                break;
            }
            n++;
        }

        if (out > 0 && indices[out - 1] == i) {
            continue;
        }

        while (*d) {
            if (kstrncmp(d, query, kstrlen(query)) == 0) {
                indices[out++] = i;
                break;
            }
            d++;
        }
    }
    return out;
}

driver_info_t* driver_get(int index) {
    if (index < 0 || index >= DRIVER_MAX) {
        return (driver_info_t*)0;
    }
    if (!g_drivers[index].used) {
        return (driver_info_t*)0;
    }
    return &g_drivers[index];
}

driver_info_t* driver_get_by_name(const char* name) {
    int i;
    for (i = 0; i < DRIVER_MAX; i++) {
        if (!g_drivers[i].used) {
            continue;
        }
        if (kstrcmp(g_drivers[i].name, name) == 0) {
            return &g_drivers[i];
        }
    }
    return (driver_info_t*)0;
}

int driver_install(const char* name) {
    int i;
    for (i = 0; i < DRIVER_MAX; i++) {
        if (!g_drivers[i].used) {
            continue;
        }
        if (kstrcmp(g_drivers[i].name, name) == 0) {
            if (g_drivers[i].installed) {
                return 1;
            }
            g_drivers[i].installed = 1;
            return 0;
        }
    }
    return -1;
}

int driver_uninstall(const char* name) {
    driver_info_t* d = driver_get_by_name(name);
    if (!d) {
        return -1;
    }
    if (!d->installed) {
        return 1;
    }
    d->installed = 0;
    return 0;
}

int driver_installed_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < DRIVER_MAX; i++) {
        if (g_drivers[i].used && g_drivers[i].installed) {
            count++;
        }
    }
    return count;
}
