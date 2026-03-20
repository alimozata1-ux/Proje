#include "permissions.h"
#include "../../lib/kone_string.h"
#include "../console.h"

static kone_app_acl_t g_apps[KONE_MAX_APPS];
static k_u32 g_app_count;

static int find_app(const char *app_id) {
    for (k_u32 i = 0; i < g_app_count; i++) {
        if (k_strcmp(g_apps[i].app_id, app_id) == 0) {
            return (int)i;
        }
    }
    return -1;
}

const char *security_perm_name(kone_perm_t perm) {
    switch (perm) {
        case PERM_FS_READ: return "fs.read";
        case PERM_FS_WRITE: return "fs.write";
        case PERM_NET_CLIENT: return "net.client";
        case PERM_UI_WINDOW: return "ui.window";
        case PERM_UI_NOTIFY: return "ui.notify";
        case PERM_AUDIO_PLAY: return "audio.play";
        case PERM_SENSOR_TOUCH: return "sensor.touch";
        case PERM_SYSTEM_MONITOR: return "system.monitor";
        case PERM_PLUGIN_LOAD: return "plugin.load";
        case PERM_DEBUG_LOG: return "debug.log";
        default: return "none";
    }
}

void security_permissions_init(void) {
    g_app_count = 0;
    k_memset(g_apps, 0, sizeof(g_apps));
    console_puts("[SEC] Permission system initialized\n");
}

int security_register_app(const char *app_id, int sandbox_enabled) {
    if (!app_id || g_app_count >= KONE_MAX_APPS) return -1;
    if (find_app(app_id) >= 0) return -2;

    kone_app_acl_t *slot = &g_apps[g_app_count++];
    k_memset(slot, 0, sizeof(*slot));
    size_t n = k_strlen(app_id);
    if (n >= sizeof(slot->app_id)) n = sizeof(slot->app_id) - 1;
    k_memcpy(slot->app_id, app_id, n);
    slot->app_id[n] = '\0';
    slot->sandbox_enabled = sandbox_enabled ? 1 : 0;
    return 0;
}

int security_grant(const char *app_id, kone_perm_t perm) {
    int idx = find_app(app_id);
    if (idx < 0) return -1;

    kone_app_acl_t *app = &g_apps[idx];
    if (app->granted_count >= KONE_MAX_APP_PERMS) return -2;

    for (k_u32 i = 0; i < app->granted_count; i++) {
        if (app->granted[i] == perm) return 0;
    }

    app->granted[app->granted_count++] = perm;
    return 0;
}

int security_check(const char *app_id, kone_perm_t perm) {
    int idx = find_app(app_id);
    if (idx < 0) return 0;

    kone_app_acl_t *app = &g_apps[idx];
    if (!app->sandbox_enabled) return 1;

    for (k_u32 i = 0; i < app->granted_count; i++) {
        if (app->granted[i] == perm) return 1;
    }

    return 0;
}
