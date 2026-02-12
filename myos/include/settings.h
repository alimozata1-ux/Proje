#ifndef SETTINGS_H
#define SETTINGS_H

typedef struct {
    int wallpaper_enabled;
    int cloud_enabled;
    int taskbar_compact;
    int desktop_enabled;
    int brightness;
    int theme_dark;
} os_settings_t;

void settings_init(void);
os_settings_t* settings_get(void);
void settings_set_wallpaper(int enabled);
void settings_set_clouds(int enabled);
void settings_set_taskbar_compact(int enabled);
void settings_set_desktop_enabled(int enabled);
void settings_set_brightness(int value);
void settings_set_theme_dark(int enabled);

#endif
