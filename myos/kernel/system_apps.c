#include "system_apps.h"
#include "browser.h"
#include "driver.h"
#include "fs.h"
#include "gui.h"
#include "notifications.h"
#include "settings.h"
#include "string.h"
#include "vga.h"

#define APP_COUNT 6

typedef void (*app_entry_t)(void);

typedef struct {
    const char* name;
    const char* description;
    app_entry_t entry;
} system_app_t;

static void app_terminal(void) {
    (void)gui_window_open("Terminal", 8, 5, 56, 13);
    notifications_push("Terminal launched");
}

static void app_files(void) {
    char buf[16];
    (void)gui_window_open("Files", 6, 3, 40, 12);
    vga_write_string("[apps] Files opened, count=");
    kitoa(fs_count(), buf);
    vga_write_string(buf);
    vga_write_string("\n");
}

static void app_settings(void) {
    os_settings_t* st = settings_get();
    char buf[16];

    (void)gui_window_open("Settings", 20, 5, 32, 11);
    vga_write_string("[apps] Settings wallpaper=");
    kitoa(st->wallpaper_enabled, buf);
    vga_write_string(buf);
    vga_write_string(" clouds=");
    kitoa(st->cloud_enabled, buf);
    vga_write_string(buf);
    vga_write_string("\n");
}

static void app_browser(void) {
    (void)gui_window_open("Browser", 10, 2, 60, 16);
    browser_home();
}

static void app_notifications(void) {
    char buf[16];
    (void)gui_window_open("Notifications", 16, 4, 44, 10);
    vga_write_string("[apps] Unread notifications=");
    kitoa(notifications_unread_count(), buf);
    vga_write_string(buf);
    vga_write_string("\n");
}

static void app_drivers(void) {
    char buf[16];
    (void)gui_window_open("Drivers", 12, 6, 48, 10);
    vga_write_string("[apps] Installed drivers=");
    kitoa(driver_installed_count(), buf);
    vga_write_string(buf);
    vga_write_string("\n");
}

static const system_app_t apps[APP_COUNT] = {
    {"terminal", "Command terminal", app_terminal},
    {"files", "RAM file manager", app_files},
    {"settings", "System settings", app_settings},
    {"browser", "Text mode web browser", app_browser},
    {"notifications", "Notification center", app_notifications},
    {"drivers", "Driver manager", app_drivers}
};

void system_apps_init(void) {
    (void)gui_icon_add("terminal", '>', 14, 2);
    (void)gui_icon_add("browser", '@', 14, 6);
    (void)gui_icon_add("drivers", 'D', 14, 10);
}

void system_apps_list(void) {
    int i;
    vga_write_string("system apps:\n");
    for (i = 0; i < APP_COUNT; i++) {
        vga_write_string("  ");
        vga_write_string(apps[i].name);
        vga_write_string(" - ");
        vga_write_string(apps[i].description);
        vga_write_string("\n");
    }
}

int system_app_open(const char* name) {
    int i;
    for (i = 0; i < APP_COUNT; i++) {
        if (kstrcmp(name, apps[i].name) == 0) {
            apps[i].entry();
            gui_redraw();
            return 0;
        }
    }
    return -1;
}
