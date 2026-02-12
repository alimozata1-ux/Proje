#include "settings.h"

static os_settings_t g_settings;

static int clamp_0_100(int value) {
    if (value < 0) {
        return 0;
    }
    if (value > 100) {
        return 100;
    }
    return value;
}

void settings_init(void) {
    g_settings.wallpaper_enabled = 1;
    g_settings.cloud_enabled = 1;
    g_settings.taskbar_compact = 0;
    g_settings.desktop_enabled = 1;
    g_settings.brightness = 75;
    g_settings.theme_dark = 0;
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

void settings_set_desktop_enabled(int enabled) {
    g_settings.desktop_enabled = enabled ? 1 : 0;
}

void settings_set_brightness(int value) {
    g_settings.brightness = clamp_0_100(value);
}

void settings_set_theme_dark(int enabled) {
    g_settings.theme_dark = enabled ? 1 : 0;
}
