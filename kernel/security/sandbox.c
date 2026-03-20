#include "sandbox.h"
#include "../../lib/kone_string.h"
#include "../console.h"

#define SANDBOX_CAP 64

static sandbox_profile_t profiles[SANDBOX_CAP];

void sandbox_init(void) {
    k_memset(profiles, 0, sizeof(profiles));
    console_puts("[SEC] Sandbox manager initialized\n");
}

static int find_profile(const char *app_id) {
    for (int i = 0; i < SANDBOX_CAP; i++) {
        if (profiles[i].enabled && k_strcmp(profiles[i].app_id, app_id) == 0) {
            return i;
        }
    }
    return -1;
}

int sandbox_configure(const char *app_id, k_u32 mem_limit_kb, k_u32 cpu_budget_percent) {
    if (!app_id || cpu_budget_percent > 100) return -1;

    int idx = find_profile(app_id);
    if (idx < 0) {
        for (int i = 0; i < SANDBOX_CAP; i++) {
            if (!profiles[i].enabled) {
                idx = i;
                break;
            }
        }
    }
    if (idx < 0) return -2;

    sandbox_profile_t *p = &profiles[idx];
    p->enabled = 1;
    p->mem_limit_kb = mem_limit_kb;
    p->cpu_budget_percent = cpu_budget_percent;

    size_t n = k_strlen(app_id);
    if (n >= KONE_SANDBOX_NAME_MAX) n = KONE_SANDBOX_NAME_MAX - 1;
    k_memcpy(p->app_id, app_id, n);
    p->app_id[n] = '\0';

    return 0;
}

int sandbox_is_allowed(const char *app_id, k_u32 requested_kb) {
    int idx = find_profile(app_id);
    if (idx < 0) return 1;
    return requested_kb <= profiles[idx].mem_limit_kb;
}
