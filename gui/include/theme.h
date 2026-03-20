#ifndef KONE_THEME_H
#define KONE_THEME_H

#include "../../lib/kone_types.h"

typedef struct {
    k_u32 background;
    k_u32 surface;
    k_u32 text;
    k_u32 accent;
} theme_palette_t;

void zk_theme_init(void);
int zk_theme_apply_light(void);
int zk_theme_apply_dark(void);
const theme_palette_t *zk_theme_current(void);

#endif
