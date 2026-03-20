#include "plugin.h"
#include "console.h"
#include "../lib/kone_string.h"

static plugin_info_t g_plugins[PLUGIN_MAX];

void plugin_system_init(void) {
    k_memset(g_plugins, 0, sizeof(g_plugins));
    console_puts("[SYS] Plugin system initialized\n");
}

int plugin_register(const char *name, k_u32 version) {
    for (int i = 0; i < PLUGIN_MAX; i++) {
        if (!g_plugins[i].used) {
            g_plugins[i].used = 1;
            g_plugins[i].version = version;
            size_t n = k_strlen(name);
            if (n > sizeof(g_plugins[i].name) - 1) n = sizeof(g_plugins[i].name) - 1;
            k_memcpy(g_plugins[i].name, name, n);
            g_plugins[i].name[n] = '\0';
            return 0;
        }
    }
    return -1;
}
