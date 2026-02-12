#include "shell.h"
#include "allocator.h"
#include "browser.h"
#include "driver.h"
#include "feature_hub.h"
#include "fs.h"
#include "gui.h"
#include "keyboard_buffer.h"
#include "logger.h"
#include "notifications.h"
#include "settings.h"
#include "string.h"
#include "syscall_table.h"
#include "system_apps.h"
#include "task.h"
#include "vga.h"

#define SHELL_INPUT_MAX 128

static char shell_input[SHELL_INPUT_MAX];
static int shell_len = 0;

static void shell_prompt(void) {
    vga_write_string("\nmyos> ");
}

static void shell_print_number(int value) {
    char buf[16];
    kitoa(value, buf);
    vga_write_string(buf);
}

static const char* skip_spaces(const char* s) {
    while (*s == ' ') {
        s++;
    }
    return s;
}

static int starts_with(const char* text, const char* prefix) {
    while (*prefix) {
        if (*text != *prefix) {
            return 0;
        }
        text++;
        prefix++;
    }
    return 1;
}

static void shell_clear(void) {
    vga_clear();
    vga_write_string("MyOS educational shell\n");
}

static void shell_cmd_help(void) {
    vga_write_string("Commands:\n");
    vga_write_string("  help, clear, echo TEXT, alloc N\n");
    vga_write_string("  ls, touch NAME, rm NAME, cat NAME\n");
    vga_write_string("  write NAME TEXT, append NAME TEXT, run NAME\n");
    vga_write_string("  gui, winopen TITLE, winclose ID, winfocus ID, winlist\n");
    vga_write_string("  iconlist, iconadd NAME, icondel ID\n");
    vga_write_string("  browser home|open URL|back|forward|tabs|tab ID|close ID|bm URL|bms\n");
    vga_write_string("  settings show|wallpaper 0|1|clouds 0|1|taskbar 0|1\n");
    vga_write_string("  notif add TEXT|list|readall|clear\n");
    vga_write_string("  driver list|find TEXT|install NAME|uninstall NAME|info NAME|installed\n");
    vga_write_string("  tasks, apps, app open NAME\n");
    vga_write_string("  features, feature run NAME, feature count\n");
}

static void shell_cmd_alloc(const char* arg) {
    int size = katoi(arg);
    void* ptr = kmalloc((unsigned int)size);
    if (!ptr) {
        vga_write_string("alloc failed\n");
        return;
    }
    vga_write_string("allocated bytes=");
    shell_print_number(size);
    vga_write_string("\n");
}

static void shell_cmd_ls(void) {
    int i;
    int found = 0;
    for (i = 0; i < FS_MAX_FILES; i++) {
        fs_node_t* node = fs_get(i);
        if (!node || !node->used) {
            continue;
        }
        vga_write_string(node->name);
        if (node->type == FS_FILE_EXEC) {
            vga_write_string(" [exe]");
        }
        vga_write_string(" (");
        shell_print_number((int)node->size);
        vga_write_string(" bytes)\n");
        found = 1;
    }
    if (!found) {
        vga_write_string("(empty)\n");
    }
}

static void shell_cmd_touch(const char* name) {
    vga_write_string(fs_create(name) == 0 ? "created\n" : "create failed\n");
}

static void shell_cmd_rm(const char* name) {
    vga_write_string(fs_delete(name) == 0 ? "deleted\n" : "delete failed\n");
}

static void shell_cmd_cat(const char* name) {
    char buf[FS_DATA_MAX];
    if (fs_read(name, buf, FS_DATA_MAX) < 0) {
        vga_write_string("read failed\n");
        return;
    }
    vga_write_string(buf);
    vga_write_string("\n");
}

static int split_token(const char* src, char* out, int out_cap, const char** next) {
    int i = 0;
    src = skip_spaces(src);
    if (*src == '\0') {
        out[0] = '\0';
        if (next) *next = src;
        return 0;
    }
    while (*src && *src != ' ' && i < out_cap - 1) {
        out[i++] = *src++;
    }
    out[i] = '\0';
    if (next) *next = src;
    return i;
}

static void shell_cmd_write(const char* args, int append) {
    char name[FS_NAME_MAX];
    const char* rest;

    if (split_token(args, name, FS_NAME_MAX, &rest) == 0) {
        vga_write_string("missing name\n");
        return;
    }
    rest = skip_spaces(rest);
    if (*rest == '\0') {
        vga_write_string("missing text\n");
        return;
    }

    if (!fs_exists(name) && fs_create(name) != 0) {
        vga_write_string("create failed\n");
        return;
    }

    if (append) {
        vga_write_string(fs_append(name, rest) == 0 ? "appended\n" : "append failed\n");
    } else {
        vga_write_string(fs_write(name, rest) == 0 ? "written\n" : "write failed\n");
    }
}

static void shell_cmd_run(const char* name) {
    char buffer[FS_DATA_MAX];
    if (!fs_exists(name)) {
        vga_write_string("run failed: missing file\n");
        return;
    }
    if (!fs_is_exec(name)) {
        vga_write_string("run failed: not executable\n");
        return;
    }
    if (fs_read(name, buffer, FS_DATA_MAX) < 0) {
        vga_write_string("run failed: read error\n");
        return;
    }
    vga_write_string("[exec] ");
    vga_write_string(name);
    vga_write_string("\n");
    vga_write_string(buffer);
}

static void shell_cmd_winlist(void) {
    int i;
    int found = 0;
    for (i = 0; i < GUI_MAX_WINDOWS; i++) {
        gui_window_t* w = gui_window_get(i);
        if (!w) continue;
        vga_write_string("id=");
        shell_print_number(w->id);
        vga_write_string(" title=");
        vga_write_string(w->title);
        vga_write_string("\n");
        found = 1;
    }
    if (!found) vga_write_string("no windows\n");
}

static void shell_cmd_winopen(const char* title) {
    int id = gui_window_open(title, 6, 4, 40, 10);
    if (id < 0) {
        vga_write_string("winopen failed\n");
        return;
    }
    vga_write_string("opened window id=");
    shell_print_number(id);
    vga_write_string("\n");
}

static void shell_cmd_iconlist(void) {
    int i;
    int found = 0;
    for (i = 0; i < GUI_MAX_ICONS; i++) {
        gui_icon_t* icon = gui_icon_get(i);
        if (!icon) continue;
        vga_write_string("id=");
        shell_print_number(icon->id);
        vga_write_string(" label=");
        vga_write_string(icon->label);
        vga_write_string("\n");
        found = 1;
    }
    if (!found) vga_write_string("no icons\n");
}

static void shell_cmd_iconadd(const char* label) {
    int count = gui_icon_count();
    int id = gui_icon_add(label, '*', 2 + ((count % 4) * 10), 2 + ((count / 4) * 4));
    if (id < 0) {
        vga_write_string("iconadd failed\n");
        return;
    }
    vga_write_string("icon added id=");
    shell_print_number(id);
    vga_write_string("\n");
}

static void shell_cmd_browser(const char* args) {
    if (kstrcmp(args, "home") == 0) return browser_home();
    if (kstrcmp(args, "back") == 0) return browser_back();
    if (kstrcmp(args, "forward") == 0) return browser_forward();
    if (kstrcmp(args, "tabs") == 0) return browser_tabs();
    if (kstrcmp(args, "bms") == 0) return browser_bookmarks();
    if (starts_with(args, "open ")) return browser_open(args + 5);
    if (starts_with(args, "tab ")) return browser_switch(katoi(args + 4));
    if (starts_with(args, "close ")) return browser_close(katoi(args + 6));
    if (starts_with(args, "bm ")) return browser_bookmark_add(args + 3);
    vga_write_string("browser: unknown subcommand\n");
}

static void shell_cmd_settings_show(void) {
    os_settings_t* st = settings_get();
    vga_write_string("settings:\n  wallpaper=");
    shell_print_number(st->wallpaper_enabled);
    vga_write_string("\n  clouds=");
    shell_print_number(st->cloud_enabled);
    vga_write_string("\n  taskbar_compact=");
    shell_print_number(st->taskbar_compact);
    vga_write_string("\n");
}

static void shell_cmd_settings(const char* args) {
    if (kstrcmp(args, "show") == 0) return shell_cmd_settings_show();
    if (starts_with(args, "wallpaper ")) {
        settings_set_wallpaper(katoi(args + 10)); gui_redraw(); vga_write_string("settings: wallpaper updated\n"); return;
    }
    if (starts_with(args, "clouds ")) {
        settings_set_clouds(katoi(args + 7)); gui_redraw(); vga_write_string("settings: clouds updated\n"); return;
    }
    if (starts_with(args, "taskbar ")) {
        settings_set_taskbar_compact(katoi(args + 8)); gui_redraw(); vga_write_string("settings: taskbar updated\n"); return;
    }
    vga_write_string("settings: unknown option\n");
}

static void shell_cmd_notif(const char* args) {
    if (starts_with(args, "add ")) {
        notifications_push(args + 4);
        gui_redraw();
        vga_write_string("notification added\n");
        return;
    }
    if (kstrcmp(args, "list") == 0) {
        int i; int found = 0;
        for (i = 0; i < NOTIFY_MAX; i++) {
            notification_t* n = notifications_get(i);
            if (!n) continue;
            vga_write_string("- ");
            vga_write_string(n->read ? "[read] " : "[new] ");
            vga_write_string(n->text);
            vga_write_string("\n");
            found = 1;
        }
        if (!found) vga_write_string("no notifications\n");
        return;
    }
    if (kstrcmp(args, "readall") == 0) {
        notifications_mark_all_read(); gui_redraw(); vga_write_string("notifications marked read\n"); return;
    }
    if (kstrcmp(args, "clear") == 0) {
        notifications_clear(); gui_redraw(); vga_write_string("notifications cleared\n"); return;
    }
    vga_write_string("notif: unknown subcommand\n");
}

static void shell_cmd_driver(const char* args) {
    if (kstrcmp(args, "list") == 0 || kstrcmp(args, "installed") == 0) {
        int i;
        int found = 0;
        for (i = 0; i < DRIVER_MAX; i++) {
            driver_info_t* d = driver_get(i);
            if (!d) continue;
            if (kstrcmp(args, "installed") == 0 && !d->installed) continue;
            vga_write_string(d->installed ? "[on] " : "[off] ");
            vga_write_string(d->name);
            vga_write_string(" - ");
            vga_write_string(d->description);
            vga_write_string("\n");
            found = 1;
        }
        if (!found) vga_write_string("no drivers\n");
        return;
    }

    if (starts_with(args, "find ")) {
        int idx[DRIVER_MAX];
        int n = driver_find(args + 5, idx, DRIVER_MAX);
        int i;
        if (n <= 0) {
            vga_write_string("driver: no match\n");
            return;
        }
        for (i = 0; i < n; i++) {
            driver_info_t* d = driver_get(idx[i]);
            if (!d) continue;
            vga_write_string(d->installed ? "[on] " : "[off] ");
            vga_write_string(d->name);
            vga_write_string(" - ");
            vga_write_string(d->description);
            vga_write_string("\n");
        }
        return;
    }

    if (starts_with(args, "install ")) {
        int rc = driver_install(args + 8);
        if (rc == 0) {
            notifications_push("Driver installed");
            gui_redraw();
            vga_write_string("driver installed\n");
        } else if (rc == 1) {
            vga_write_string("driver already installed\n");
        } else {
            vga_write_string("driver not found\n");
        }
        return;
    }

    if (starts_with(args, "uninstall ")) {
        int rc = driver_uninstall(args + 10);
        if (rc == 0) {
            notifications_push("Driver uninstalled");
            gui_redraw();
            vga_write_string("driver uninstalled\n");
        } else if (rc == 1) {
            vga_write_string("driver already disabled\n");
        } else {
            vga_write_string("driver not found\n");
        }
        return;
    }

    if (starts_with(args, "info ")) {
        driver_info_t* d = driver_get_by_name(args + 5);
        if (!d) {
            vga_write_string("driver not found\n");
            return;
        }
        vga_write_string("name=");
        vga_write_string(d->name);
        vga_write_string("\nstatus=");
        vga_write_string(d->installed ? "installed" : "not-installed");
        vga_write_string("\ndesc=");
        vga_write_string(d->description);
        vga_write_string("\n");
        return;
    }

    vga_write_string("driver: unknown subcommand\n");
}


static void shell_cmd_tasks(void) {
    int i;
    int total = task_count();

    vga_write_string("tasks:\n");
    for (i = 0; i < total; i++) {
        task_t* t = task_get(i);
        char num[16];

        if (!t) {
            continue;
        }

        vga_write_string("  #");
        kitoa(i, num);
        vga_write_string(num);
        vga_write_string(" ");
        vga_write_string(t->name ? t->name : "unnamed");
        vga_write_string(" mode=");
        vga_write_string(t->mode == TASK_USER ? "user" : "kernel");
        vga_write_string(" state=");
        vga_write_string(t->state == TASK_RUNNING ? "running" : "ready");
        vga_write_string(" runs=");
        kitoa((int)t->run_count, num);
        vga_write_string(num);
        vga_write_string("\n");
    }
}

static void shell_cmd_apps(const char* args) {
    if (kstrcmp(args, "list") == 0 || args[0] == '\0') {
        system_apps_list();
        return;
    }

    if (starts_with(args, "open ")) {
        const char* name = skip_spaces(args + 5);
        if (name[0] == '\0') {
            vga_write_string("app: missing name\n");
            return;
        }

        if (system_app_open(name) == 0) {
            vga_write_string("app launched\n");
        } else {
            vga_write_string("app not found\n");
        }
        return;
    }

    vga_write_string("app: use 'apps' or 'app open NAME'\n");
}


static void shell_cmd_feature(const char* args) {
    char num[16];

    if (kstrcmp(args, "list") == 0 || kstrcmp(args, "") == 0) {
        feature_hub_list();
        return;
    }

    if (kstrcmp(args, "count") == 0) {
        vga_write_string("feature count=");
        kitoa(feature_hub_count(), num);
        vga_write_string(num);
        vga_write_string("\n");
        return;
    }

    if (starts_with(args, "run ")) {
        if (feature_hub_run(skip_spaces(args + 4)) == 0) {
            vga_write_string("feature executed\n");
        } else {
            vga_write_string("feature not found\n");
        }
        return;
    }

    vga_write_string("feature: use 'features' or 'feature run NAME'\n");
}


static void shell_execute(const char* line) {
    if (kstrcmp(line, "help") == 0) return shell_cmd_help();
    if (kstrcmp(line, "clear") == 0) return shell_clear();
    if (kstrcmp(line, "ls") == 0) return shell_cmd_ls();
    if (kstrncmp(line, "echo ", 5) == 0) { vga_write_string(line + 5); vga_write_string("\n"); return; }
    if (kstrncmp(line, "alloc ", 6) == 0) return shell_cmd_alloc(line + 6);
    if (kstrncmp(line, "touch ", 6) == 0) return shell_cmd_touch(skip_spaces(line + 6));
    if (kstrncmp(line, "rm ", 3) == 0) return shell_cmd_rm(skip_spaces(line + 3));
    if (kstrncmp(line, "cat ", 4) == 0) return shell_cmd_cat(skip_spaces(line + 4));
    if (kstrncmp(line, "write ", 6) == 0) return shell_cmd_write(line + 6, 0);
    if (kstrncmp(line, "append ", 7) == 0) return shell_cmd_write(line + 7, 1);
    if (kstrncmp(line, "run ", 4) == 0) return shell_cmd_run(skip_spaces(line + 4));

    if (kstrcmp(line, "gui") == 0) return gui_demo();
    if (kstrcmp(line, "winlist") == 0) return shell_cmd_winlist();
    if (kstrncmp(line, "winopen ", 8) == 0) return shell_cmd_winopen(skip_spaces(line + 8));
    if (kstrncmp(line, "winclose ", 9) == 0) {
        if (gui_window_close(katoi(skip_spaces(line + 9))) == 0) vga_write_string("window closed\n");
        else vga_write_string("winclose failed\n");
        return;
    }
    if (kstrncmp(line, "winfocus ", 9) == 0) {
        if (gui_window_focus(katoi(skip_spaces(line + 9))) == 0) vga_write_string("window focused\n");
        else vga_write_string("winfocus failed\n");
        return;
    }
    if (kstrcmp(line, "iconlist") == 0) return shell_cmd_iconlist();
    if (kstrncmp(line, "iconadd ", 8) == 0) return shell_cmd_iconadd(skip_spaces(line + 8));
    if (kstrncmp(line, "icondel ", 8) == 0) {
        if (gui_icon_remove(katoi(skip_spaces(line + 8))) == 0) vga_write_string("icon removed\n");
        else vga_write_string("icondel failed\n");
        return;
    }

    if (kstrncmp(line, "browser ", 8) == 0) return shell_cmd_browser(skip_spaces(line + 8));
    if (kstrncmp(line, "settings ", 9) == 0) return shell_cmd_settings(skip_spaces(line + 9));
    if (kstrncmp(line, "notif ", 6) == 0) return shell_cmd_notif(skip_spaces(line + 6));
    if (kstrncmp(line, "driver ", 7) == 0) return shell_cmd_driver(skip_spaces(line + 7));
    if (kstrcmp(line, "tasks") == 0) return shell_cmd_tasks();
    if (kstrcmp(line, "apps") == 0) return shell_cmd_apps("list");
    if (kstrncmp(line, "app ", 4) == 0) return shell_cmd_apps(skip_spaces(line + 4));
    if (kstrcmp(line, "features") == 0) return shell_cmd_feature("list");
    if (kstrncmp(line, "feature ", 8) == 0) return shell_cmd_feature(skip_spaces(line + 8));

    vga_write_string("unknown command\n");
}

void shell_init(void) {
    shell_len = 0;
    shell_input[0] = '\0';
    kbd_buffer_init();
    syscall_table_init();
    fs_init();
    browser_init();
    notifications_init();
    driver_init();
    system_apps_init();
    feature_hub_init();
    notifications_push("Welcome to MyOS");
    log_info("shell", "initialized");
    shell_prompt();
}

void shell_on_key(char c) {
    if (c == '\r') c = '\n';
    if (c == '\b') {
        if (shell_len > 0) {
            shell_len--;
            shell_input[shell_len] = '\0';
        }
        return;
    }
    if (c == '\n') {
        shell_input[shell_len] = '\0';
        shell_execute(shell_input);
        shell_len = 0;
        shell_input[0] = '\0';
        shell_prompt();
        return;
    }
    if (shell_len < SHELL_INPUT_MAX - 1) {
        shell_input[shell_len++] = c;
        shell_input[shell_len] = '\0';
    }
}

void shell_tick(void) {
    char c;
    int budget = 16;
    while (budget-- > 0 && kbd_buffer_pop(&c)) {
        shell_on_key(c);
    }
}
