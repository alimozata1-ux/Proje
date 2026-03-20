#include "include/theme.h"
#include "../kernel/console.h"

static theme_palette_t current_theme;

void zk_theme_init(void) {
    zk_theme_apply_dark();
    console_puts("[Z] Theme engine initialized\n");
}

int zk_theme_apply_light(void) {
    current_theme.background = 0xEFEFEF;
    current_theme.surface = 0xFFFFFF;
    current_theme.text = 0x121212;
    current_theme.accent = 0x0057FF;
    return 0;
}

int zk_theme_apply_dark(void) {
    current_theme.background = 0x101318;
    current_theme.surface = 0x1D2330;
    current_theme.text = 0xE6E9EF;
    current_theme.accent = 0x56A6FF;
    return 0;
}

const theme_palette_t *zk_theme_current(void) {
    return &current_theme;
}
