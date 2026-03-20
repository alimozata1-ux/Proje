#ifndef KONE_SANDBOX_H
#define KONE_SANDBOX_H

#include "../../lib/kone_types.h"

#define KONE_SANDBOX_NAME_MAX 48

typedef struct {
    char app_id[KONE_SANDBOX_NAME_MAX];
    k_u32 mem_limit_kb;
    k_u32 cpu_budget_percent;
    int enabled;
} sandbox_profile_t;

void sandbox_init(void);
int sandbox_configure(const char *app_id, k_u32 mem_limit_kb, k_u32 cpu_budget_percent);
int sandbox_is_allowed(const char *app_id, k_u32 requested_kb);

#endif
