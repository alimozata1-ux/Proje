#ifndef KONE_PERMISSIONS_H
#define KONE_PERMISSIONS_H

#include "../../lib/kone_types.h"

#define KONE_MAX_PERMS       128
#define KONE_MAX_APP_PERMS   32
#define KONE_MAX_APPS        64

typedef enum {
    PERM_NONE = 0,
    PERM_FS_READ,
    PERM_FS_WRITE,
    PERM_NET_CLIENT,
    PERM_UI_WINDOW,
    PERM_UI_NOTIFY,
    PERM_AUDIO_PLAY,
    PERM_SENSOR_TOUCH,
    PERM_SYSTEM_MONITOR,
    PERM_PLUGIN_LOAD,
    PERM_DEBUG_LOG,
} kone_perm_t;

typedef struct {
    char app_id[48];
    kone_perm_t granted[KONE_MAX_APP_PERMS];
    k_u32 granted_count;
    int sandbox_enabled;
} kone_app_acl_t;

void security_permissions_init(void);
int security_register_app(const char *app_id, int sandbox_enabled);
int security_grant(const char *app_id, kone_perm_t perm);
int security_check(const char *app_id, kone_perm_t perm);
const char *security_perm_name(kone_perm_t perm);

#endif
