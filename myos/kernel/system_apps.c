#include "system_apps.h"
#include "browser.h"
#include "driver.h"
#include "fs.h"
#include "gui.h"
#include "notifications.h"
#include "settings.h"
#include "string.h"
#include "task.h"
#include "vga.h"

#define APP_COUNT 12

#define NOTEPAD_FILE "notes.txt"

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

static void app_calculator(void) {
    int a = 24;
    int b = 6;
    int add = a + b;
    int sub = a - b;
    int mul = a * b;
    int div = b ? (a / b) : 0;
    char buf[16];

    (void)gui_window_open("Calculator", 24, 3, 28, 11);
    vga_write_string("[calc] a=24 b=6\n");
    vga_write_string("[calc] add=");
    kitoa(add, buf);
    vga_write_string(buf);
    vga_write_string(" sub=");
    kitoa(sub, buf);
    vga_write_string(buf);
    vga_write_string(" mul=");
    kitoa(mul, buf);
    vga_write_string(buf);
    vga_write_string(" div=");
    kitoa(div, buf);
    vga_write_string(buf);
    vga_write_string("\n");
}

static void app_notepad(void) {
    char content[FS_DATA_MAX];

    (void)gui_window_open("Notepad", 18, 4, 40, 12);

    if (!fs_exists(NOTEPAD_FILE)) {
        (void)fs_create(NOTEPAD_FILE);
        (void)fs_write(NOTEPAD_FILE, "MyOS Notepad\n");
    }

    (void)fs_append(NOTEPAD_FILE, "- new note line\n");
    if (fs_read(NOTEPAD_FILE, content, FS_DATA_MAX) < 0) {
        vga_write_string("[notepad] read failed\n");
        return;
    }

    vga_write_string("[notepad] ");
    vga_write_string(NOTEPAD_FILE);
    vga_write_string("\n");
    vga_write_string(content);
}

static void app_this_computer(void) {
    char buf[16];

    (void)gui_window_open("This Computer", 12, 2, 54, 14);
    vga_write_string("[pc] This Computer\n");

    vga_write_string("[pc] files=");
    kitoa(fs_count(), buf);
    vga_write_string(buf);

    vga_write_string(" drivers=");
    kitoa(driver_installed_count(), buf);
    vga_write_string(buf);

    vga_write_string(" tasks=");
    kitoa(task_count(), buf);
    vga_write_string(buf);

    vga_write_string(" windows=");
    kitoa(gui_window_count(), buf);
    vga_write_string(buf);

    vga_write_string(" icons=");
    kitoa(gui_icon_count(), buf);
    vga_write_string(buf);

    vga_write_string("\n");
}

static void app_system_monitor(void) {
    char buf[16];
    int i;

    (void)gui_window_open("System Monitor", 8, 1, 62, 15);
    vga_write_string("[monitor] tasks:\n");

    for (i = 0; i < task_count(); i++) {
        task_t* t = task_get(i);
        if (!t) {
            continue;
        }

        vga_write_string("  ");
        vga_write_string(t->name ? t->name : "unnamed");
        vga_write_string(" mode=");
        vga_write_string(t->mode == TASK_USER ? "user" : "kernel");
        vga_write_string(" runs=");
        kitoa((int)t->run_count, buf);
        vga_write_string(buf);
        vga_write_string("\n");
    }

    vga_write_string("[monitor] unread notifications=");
    kitoa(notifications_unread_count(), buf);
    vga_write_string(buf);
    vga_write_string("\n");
}


static void app_display_settings(void) {
    os_settings_t* st = settings_get();
    char buf[16];

    (void)gui_window_open("Display Settings", 20, 2, 36, 12);
    vga_write_string("[display] desktop=");
    kitoa(st->desktop_enabled, buf);
    vga_write_string(buf);
    vga_write_string(" wallpaper=");
    kitoa(st->wallpaper_enabled, buf);
    vga_write_string(buf);
    vga_write_string(" clouds=");
    kitoa(st->cloud_enabled, buf);
    vga_write_string(buf);
    vga_write_string("\n[display] brightness=");
    kitoa(st->brightness, buf);
    vga_write_string(buf);
    vga_write_string(" theme_dark=");
    kitoa(st->theme_dark, buf);
    vga_write_string(buf);
    vga_write_string("\n");
}

static void app_desktop(void) {
    int icons;
    int windows;
    char buf[16];

    (void)gui_window_open("Desktop", 10, 3, 58, 14);
    icons = gui_icon_count();
    windows = gui_window_count();

    vga_write_string("[desktop] manager\n");
    vga_write_string("[desktop] icons=");
    kitoa(icons, buf);
    vga_write_string(buf);
    vga_write_string(" windows=");
    kitoa(windows, buf);
    vga_write_string(buf);
    vga_write_string("\n");
}


static const system_app_t apps[APP_COUNT] = {
    {"terminal", "Command terminal", app_terminal},
    {"files", "RAM file manager", app_files},
    {"settings", "System settings", app_settings},
    {"browser", "Text mode web browser", app_browser},
    {"notifications", "Notification center", app_notifications},
    {"drivers", "Driver manager", app_drivers},
    {"calculator", "Basic arithmetic app", app_calculator},
    {"notepad", "Simple notes app", app_notepad},
    {"thispc", "This Computer overview", app_this_computer},
    {"monitor", "System monitor", app_system_monitor},
    {"display", "Display settings", app_display_settings},
    {"desktop", "Desktop manager", app_desktop}
};

void system_apps_init(void) {
    (void)gui_icon_add("terminal", '>', 14, 2);
    (void)gui_icon_add("browser", '@', 14, 6);
    (void)gui_icon_add("drivers", 'D', 14, 10);
    (void)gui_icon_add("calc", '+', 26, 2);
    (void)gui_icon_add("notes", 'N', 26, 6);
    (void)gui_icon_add("thispc", 'C', 26, 10);
    (void)gui_icon_add("monitor", 'M', 26, 14);
    (void)gui_icon_add("display", 'V', 38, 2);
    (void)gui_icon_add("desktop", 'T', 38, 6);
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

    if (kstrcmp(name, "hesapmakinesi") == 0 || kstrcmp(name, "calc") == 0) {
        app_calculator();
        gui_redraw();
        return 0;
    }

    if (kstrcmp(name, "notdefteri") == 0 || kstrcmp(name, "notes") == 0) {
        app_notepad();
        gui_redraw();
        return 0;
    }

    if (kstrcmp(name, "bu-bilgisayar") == 0) {
        app_this_computer();
        gui_redraw();
        return 0;
    }

    if (kstrcmp(name, "goruntu") == 0) {
        app_display_settings();
        gui_redraw();
        return 0;
    }

    if (kstrcmp(name, "masaustu") == 0) {
        app_desktop();
        gui_redraw();
        return 0;
    }

    return -1;
}
