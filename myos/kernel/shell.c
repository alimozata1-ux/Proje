#include "shell.h"
#include "allocator.h"
#include "browser.h"
#include "fs.h"
#include "gui.h"
#include "keyboard_buffer.h"
#include "logger.h"
#include "string.h"
#include "syscall_table.h"
#include "vga.h"

#define SHELL_INPUT_MAX 128

static char shell_input[SHELL_INPUT_MAX];
static int shell_len = 0;

static void shell_prompt(void) {
    vga_write_string("\nmyos> ");
}

static void shell_clear(void) {
    vga_clear();
    vga_write_string("MyOS educational shell\n");
}

static void shell_print_number(unsigned int value) {
    char buf[16];
    kutoa(value, buf);
    vga_write_string(buf);
}

static void shell_cmd_help(void) {
    vga_write_string("Commands:\n");
    vga_write_string("  help                 - show command list\n");
    vga_write_string("  clear                - clear screen\n");
    vga_write_string("  echo TEXT            - print TEXT\n");
    vga_write_string("  alloc N              - allocate N bytes\n");
    vga_write_string("  info                 - print kernel info\n");
    vga_write_string("  map                  - paging summary\n");
    vga_write_string("  sched                - scheduler summary\n");
    vga_write_string("  sys                  - syscall summary\n");
    vga_write_string("  ls                   - list files\n");
    vga_write_string("  touch NAME           - create file\n");
    vga_write_string("  rm NAME              - delete file\n");
    vga_write_string("  cat NAME             - show file content\n");
    vga_write_string("  write NAME TEXT      - overwrite file\n");
    vga_write_string("  append NAME TEXT     - append to file\n");
    vga_write_string("  run NAME             - run exe-like file\n");
    vga_write_string("  gui                  - draw GUI demo\n");
    vga_write_string("  winopen TITLE        - open new window\n");
    vga_write_string("  winclose ID          - close window\n");
    vga_write_string("  winfocus ID          - focus/bring-to-front\n");
    vga_write_string("  winlist              - list windows\n");
    vga_write_string("  iconlist             - list desktop icons\n");
    vga_write_string("  iconadd NAME         - add desktop icon\n");
    vga_write_string("  icondel ID           - remove desktop icon\n");
    vga_write_string("  browser home         - open home page\n");
    vga_write_string("  browser open URL     - open URL\n");
    vga_write_string("  browser back         - back history\n");
    vga_write_string("  browser forward      - forward history\n");
    vga_write_string("  browser tabs         - list tabs\n");
    vga_write_string("  browser tab ID       - switch tab\n");
    vga_write_string("  browser close ID     - close tab\n");
    vga_write_string("  browser bm URL       - bookmark URL\n");
    vga_write_string("  browser bms          - list bookmarks\n");
}

static void shell_cmd_alloc(const char* arg) {
    unsigned int size = (unsigned int)katoi(arg);
    void* ptr = kmalloc(size);
    if (!ptr) {
        vga_write_string("alloc failed\n");
        return;
    }
    vga_write_string("allocated ");
    shell_print_number(size);
    vga_write_string(" bytes\n");
}

static void shell_cmd_info(void) {
    vga_write_string("kernel: 32-bit protected mode\n");
    vga_write_string("paging: enabled, first 4MB identity map\n");
    vga_write_string("scheduler: preemptive round-robin\n");
    vga_write_string("input: irq keyboard + buffer\n");
    vga_write_string("filesystem: in-memory ramfs\n");
}

static void shell_cmd_map(void) {
    vga_write_string("PDE[0] present\n");
    vga_write_string("PTE[0..1023] 4KB identity\n");
    vga_write_string("VGA page supervisor-only\n");
}

static void shell_cmd_sched(void) {
    vga_write_string("tick source: PIT IRQ0\n");
    vga_write_string("policy: round-robin\n");
    vga_write_string("supports: kernel + user task\n");
}

static void shell_cmd_sys(void) {
    vga_write_string("syscall int: 0x80\n");
    vga_write_string("id=1: write string\n");
}

static void shell_cmd_ls(void) {
    int i;
    int found = 0;
    for (i = 0; i < FS_MAX_FILES; i++) {
        fs_node_t* node = fs_get(i);
        if (node && node->used) {
            vga_write_string(node->name);
            if (node->type == FS_FILE_EXEC) {
                vga_write_string(" [exe]");
            }
            vga_write_string(" (");
            shell_print_number(node->size);
            vga_write_string(" bytes)\n");
            found = 1;
        }
    }

    if (!found) {
        vga_write_string("(empty)\n");
    }
}

static void shell_cmd_touch(const char* name) {
    int rc = fs_create(name);
    if (rc == 0) {
        vga_write_string("created\n");
    } else {
        vga_write_string("create failed\n");
    }
}

static void shell_cmd_rm(const char* name) {
    int rc = fs_delete(name);
    if (rc == 0) {
        vga_write_string("deleted\n");
    } else {
        vga_write_string("delete failed\n");
    }
}

static void shell_cmd_cat(const char* name) {
    char buffer[FS_DATA_MAX];
    int rc = fs_read(name, buffer, FS_DATA_MAX);
    if (rc < 0) {
        vga_write_string("read failed\n");
        return;
    }
    vga_write_string(buffer);
    vga_write_string("\n");
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
        if (!w) {
            continue;
        }
        vga_write_string("id=");
        shell_print_number((unsigned int)w->id);
        vga_write_string(" title=");
        vga_write_string(w->title);
        vga_write_string("\n");
        found = 1;
    }
    if (!found) {
        vga_write_string("no windows\n");
    }
}

static void shell_cmd_winopen(const char* title) {
    int id = gui_window_open(title, 6, 4, 40, 10);
    if (id < 0) {
        vga_write_string("winopen failed\n");
        return;
    }
    vga_write_string("opened window id=");
    shell_print_number((unsigned int)id);
    vga_write_string("\n");
}

static void shell_cmd_winclose(const char* arg) {
    int id = katoi(arg);
    if (gui_window_close(id) == 0) {
        vga_write_string("window closed\n");
    } else {
        vga_write_string("winclose failed\n");
    }
}

static void shell_cmd_winfocus(const char* arg) {
    int id = katoi(arg);
    if (gui_window_focus(id) == 0) {
        vga_write_string("window focused\n");
    } else {
        vga_write_string("winfocus failed\n");
    }
}

static void shell_cmd_iconlist(void) {
    int i;
    int found = 0;
    for (i = 0; i < GUI_MAX_ICONS; i++) {
        gui_icon_t* icon = gui_icon_get(i);
        if (!icon) {
            continue;
        }
        vga_write_string("id=");
        shell_print_number((unsigned int)icon->id);
        vga_write_string(" label=");
        vga_write_string(icon->label);
        vga_write_string("\n");
        found = 1;
    }
    if (!found) {
        vga_write_string("no icons\n");
    }
}

static void shell_cmd_iconadd(const char* label) {
    int count = gui_icon_count();
    int x = 2 + ((count % 4) * 10);
    int y = 2 + ((count / 4) * 4);
    int id = gui_icon_add(label, '*', x, y);

    if (id < 0) {
        vga_write_string("iconadd failed\n");
        return;
    }

    vga_write_string("icon added id=");
    shell_print_number((unsigned int)id);
    vga_write_string("\n");
}

static void shell_cmd_icondel(const char* arg) {
    int id = katoi(arg);
    if (gui_icon_remove(id) == 0) {
        vga_write_string("icon removed\n");
    } else {
        vga_write_string("icondel failed\n");
    }
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

static void shell_cmd_browser(const char* args) {
    if (kstrcmp(args, "home") == 0) {
        browser_home();
        return;
    }

    if (kstrcmp(args, "back") == 0) {
        browser_back();
        return;
    }

    if (kstrcmp(args, "forward") == 0) {
        browser_forward();
        return;
    }

    if (kstrcmp(args, "tabs") == 0) {
        browser_tabs();
        return;
    }

    if (kstrcmp(args, "bms") == 0) {
        browser_bookmarks();
        return;
    }

    if (starts_with(args, "open ")) {
        browser_open(args + 5);
        return;
    }

    if (starts_with(args, "tab ")) {
        browser_switch(katoi(args + 4));
        return;
    }

    if (starts_with(args, "close ")) {
        browser_close(katoi(args + 6));
        return;
    }

    if (starts_with(args, "bm ")) {
        browser_bookmark_add(args + 3);
        return;
    }

    vga_write_string("browser: unknown subcommand\n");
}

static const char* skip_spaces(const char* s) {
    while (*s == ' ') {
        s++;
    }
    return s;
}

static int split_token(const char* src, char* out, int out_cap, const char** next) {
    int i = 0;
    src = skip_spaces(src);
    if (*src == '\0') {
        out[0] = '\0';
        if (next) {
            *next = src;
        }
        return 0;
    }

    while (*src && *src != ' ' && i < out_cap - 1) {
        out[i++] = *src++;
    }
    out[i] = '\0';

    if (next) {
        *next = src;
    }

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

    if (!fs_exists(name)) {
        if (fs_create(name) != 0) {
            vga_write_string("create failed\n");
            return;
        }
    }

    if (append) {
        if (fs_append(name, rest) == 0) {
            vga_write_string("appended\n");
        } else {
            vga_write_string("append failed\n");
        }
    } else {
        if (fs_write(name, rest) == 0) {
            vga_write_string("written\n");
        } else {
            vga_write_string("write failed\n");
        }
    }
}

static void shell_execute(const char* line) {
    if (kstrcmp(line, "help") == 0) {
        shell_cmd_help();
        return;
    }

    if (kstrcmp(line, "clear") == 0) {
        shell_clear();
        return;
    }

    if (kstrcmp(line, "info") == 0) {
        shell_cmd_info();
        return;
    }

    if (kstrcmp(line, "map") == 0) {
        shell_cmd_map();
        return;
    }

    if (kstrcmp(line, "sched") == 0) {
        shell_cmd_sched();
        return;
    }

    if (kstrcmp(line, "sys") == 0) {
        shell_cmd_sys();
        return;
    }

    if (kstrcmp(line, "ls") == 0) {
        shell_cmd_ls();
        return;
    }

    if (kstrncmp(line, "echo ", 5) == 0) {
        vga_write_string(line + 5);
        vga_write_string("\n");
        return;
    }

    if (kstrncmp(line, "alloc ", 6) == 0) {
        shell_cmd_alloc(line + 6);
        return;
    }

    if (kstrncmp(line, "touch ", 6) == 0) {
        shell_cmd_touch(skip_spaces(line + 6));
        return;
    }

    if (kstrncmp(line, "rm ", 3) == 0) {
        shell_cmd_rm(skip_spaces(line + 3));
        return;
    }

    if (kstrncmp(line, "cat ", 4) == 0) {
        shell_cmd_cat(skip_spaces(line + 4));
        return;
    }

    if (kstrncmp(line, "write ", 6) == 0) {
        shell_cmd_write(line + 6, 0);
        return;
    }

    if (kstrncmp(line, "append ", 7) == 0) {
        shell_cmd_write(line + 7, 1);
        return;
    }

    if (kstrncmp(line, "run ", 4) == 0) {
        shell_cmd_run(skip_spaces(line + 4));
        return;
    }

    if (kstrcmp(line, "gui") == 0) {
        gui_demo();
        return;
    }

    if (kstrcmp(line, "winlist") == 0) {
        shell_cmd_winlist();
        return;
    }

    if (kstrncmp(line, "winopen ", 8) == 0) {
        shell_cmd_winopen(skip_spaces(line + 8));
        return;
    }

    if (kstrncmp(line, "winclose ", 9) == 0) {
        shell_cmd_winclose(skip_spaces(line + 9));
        return;
    }

    if (kstrncmp(line, "winfocus ", 9) == 0) {
        shell_cmd_winfocus(skip_spaces(line + 9));
        return;
    }

    if (kstrcmp(line, "iconlist") == 0) {
        shell_cmd_iconlist();
        return;
    }

    if (kstrncmp(line, "iconadd ", 8) == 0) {
        shell_cmd_iconadd(skip_spaces(line + 8));
        return;
    }

    if (kstrncmp(line, "icondel ", 8) == 0) {
        shell_cmd_icondel(skip_spaces(line + 8));
        return;
    }

    if (kstrncmp(line, "browser ", 8) == 0) {
        shell_cmd_browser(skip_spaces(line + 8));
        return;
    }

    vga_write_string("unknown command\n");
}

void shell_init(void) {
    shell_len = 0;
    shell_input[0] = '\0';
    kbd_buffer_init();
    syscall_table_init();
    fs_init();
    browser_init();
    log_info("shell", "initialized");
    shell_prompt();
}

void shell_on_key(char c) {
    if (c == '\r') {
        c = '\n';
    }

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
