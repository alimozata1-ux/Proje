#include "settings.h"

static os_settings_t g_settings;

void settings_init(void) {
    g_settings.wallpaper_enabled = 1;
    g_settings.cloud_enabled = 1;
    g_settings.taskbar_compact = 0;
}

os_settings_t* settings_get(void) {
    return &g_settings;
}

void settings_set_wallpaper(int enabled) {
    g_settings.wallpaper_enabled = enabled ? 1 : 0;
}

void settings_set_clouds(int enabled) {
    g_settings.cloud_enabled = enabled ? 1 : 0;
}

void settings_set_taskbar_compact(int enabled) {
    g_settings.taskbar_compact = enabled ? 1 : 0;
}
