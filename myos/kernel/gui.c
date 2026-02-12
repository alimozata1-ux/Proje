#include "gui.h"
#include "memory.h"
#include "notifications.h"
#include "settings.h"
#include "string.h"

#define VGA_MEMORY ((volatile unsigned short*)0xB8000)
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

#define COLOR_BG 0x1F
#define COLOR_BORDER 0x1E
#define COLOR_TITLE 0x1F
#define COLOR_TEXT 0x1F
#define COLOR_TASKBAR 0x17
#define COLOR_TASKBTN 0x1E
#define COLOR_ICON 0x1F
#define COLOR_SKY 0x1F
#define COLOR_GRASS 0x2F

static gui_window_t gui_windows[GUI_MAX_WINDOWS];
static gui_icon_t gui_icons[GUI_MAX_ICONS];
static int gui_next_id = 1;
static int gui_next_icon_id = 1;
static int gui_focused_id = -1;

static unsigned short vga_entry(char c, unsigned char color) {
    return ((unsigned short)color << 8) | (unsigned char)c;
}

static void gui_put_at(int x, int y, char c, unsigned char color) {
    if (x < 0 || x >= VGA_WIDTH || y < 0 || y >= VGA_HEIGHT) {
        return;
    }
    VGA_MEMORY[y * VGA_WIDTH + x] = vga_entry(c, color);
}

static void gui_fill_rect(int x, int y, int w, int h, char c, unsigned char color) {
    int row;
    int col;
    for (row = 0; row < h; row++) {
        for (col = 0; col < w; col++) {
            gui_put_at(x + col, y + row, c, color);
        }
    }
}

static void gui_write_at(int x, int y, const char* text, unsigned char color) {
    while (*text && x < VGA_WIDTH) {
        gui_put_at(x++, y, *text++, color);
    }
}

static void gui_draw_wallpaper(void) {
    int y;
    int x;

    /* Bliss benzeri: ustte gokyuzu, altta yesil tepe */
    for (y = 0; y < VGA_HEIGHT - 1; y++) {
        for (x = 0; x < VGA_WIDTH; x++) {
            int hill_line = 12 + ((x - 40) * (x - 40)) / 220;
            if (y >= hill_line) {
                gui_put_at(x, y, ' ', COLOR_GRASS);
            } else {
                gui_put_at(x, y, ' ', COLOR_SKY);
            }
        }
    }

    if (settings_get()->cloud_enabled) {
        /* Bulutlar */
        gui_write_at(8, 2, " ~~  ~~ ", COLOR_TEXT);
        gui_write_at(28, 4, "~~~~~~", COLOR_TEXT);
        gui_write_at(54, 3, " ~~~~ ", COLOR_TEXT);
    }
}

static void gui_draw_taskbar(void) {
    int i;
    int cursor = 1;
    char nbuf[16];
    gui_fill_rect(0, VGA_HEIGHT - 1, VGA_WIDTH, 1, ' ', COLOR_TASKBAR);
    gui_write_at(1, VGA_HEIGHT - 1, "MyOS", COLOR_TASKBAR);
    gui_write_at(6, VGA_HEIGHT - 1, "N:", COLOR_TASKBAR);
    kitoa(notifications_unread_count(), nbuf);
    gui_write_at(8, VGA_HEIGHT - 1, nbuf, COLOR_TASKBAR);
    cursor = settings_get()->taskbar_compact ? 11 : 13;

    for (i = 0; i < GUI_MAX_WINDOWS; i++) {
        gui_window_t* w = &gui_windows[i];
        int j;
        if (!w->used) {
            continue;
        }

        if (cursor >= VGA_WIDTH - 2) {
            break;
        }

        gui_put_at(cursor++, VGA_HEIGHT - 1, '[', COLOR_TASKBTN);
        if (w->id == gui_focused_id) {
            gui_put_at(cursor++, VGA_HEIGHT - 1, '*', COLOR_TASKBTN);
        }

        for (j = 0; w->title[j] && j < 8 && cursor < VGA_WIDTH - 2; j++) {
            gui_put_at(cursor++, VGA_HEIGHT - 1, w->title[j], COLOR_TASKBTN);
        }

        gui_put_at(cursor++, VGA_HEIGHT - 1, ']', COLOR_TASKBTN);
        if (cursor < VGA_WIDTH - 1) {
            gui_put_at(cursor++, VGA_HEIGHT - 1, ' ', COLOR_TASKBAR);
        }
    }
}

static void gui_draw_icons(void) {
    int i;
    int j;
    for (i = 0; i < GUI_MAX_ICONS; i++) {
        gui_icon_t* icon = &gui_icons[i];
        if (!icon->used) {
            continue;
        }

        gui_put_at(icon->x, icon->y, '[', COLOR_ICON);
        gui_put_at(icon->x + 1, icon->y, icon->glyph, COLOR_ICON);
        gui_put_at(icon->x + 2, icon->y, ']', COLOR_ICON);

        for (j = 0; icon->label[j] && j < GUI_ICON_LABEL_MAX - 1; j++) {
            gui_put_at(icon->x + j, icon->y + 1, icon->label[j], COLOR_ICON);
        }
    }
}

void gui_init(void) {
    kmemset(gui_windows, 0, sizeof(gui_windows));
    kmemset(gui_icons, 0, sizeof(gui_icons));
    gui_next_id = 1;
    gui_next_icon_id = 1;
    gui_focused_id = -1;

    (void)gui_icon_add("superx323", '*', 2, 2);
    (void)gui_icon_add("files", '#', 2, 6);
    (void)gui_icon_add("shell", '>', 2, 10);
}

void gui_draw_desktop(void) {
    if (settings_get()->wallpaper_enabled) {
        gui_draw_wallpaper();
    } else {
        gui_fill_rect(0, 0, VGA_WIDTH, VGA_HEIGHT - 1, ' ', COLOR_BG);
    }
    gui_draw_icons();
    gui_draw_taskbar();
}

void gui_draw_window(int x, int y, int w, int h, const char* title) {
    int i;

    if (w < 4 || h < 4) {
        return;
    }

    gui_fill_rect(x, y, w, h, ' ', COLOR_BG);

    for (i = 0; i < w; i++) {
        gui_put_at(x + i, y, '-', COLOR_BORDER);
        gui_put_at(x + i, y + h - 1, '-', COLOR_BORDER);
    }

    for (i = 0; i < h; i++) {
        gui_put_at(x, y + i, '|', COLOR_BORDER);
        gui_put_at(x + w - 1, y + i, '|', COLOR_BORDER);
    }

    gui_put_at(x, y, '+', COLOR_BORDER);
    gui_put_at(x + w - 1, y, '+', COLOR_BORDER);
    gui_put_at(x, y + h - 1, '+', COLOR_BORDER);
    gui_put_at(x + w - 1, y + h - 1, '+', COLOR_BORDER);

    if (title) {
        gui_write_at(x + 2, y, title, COLOR_TITLE);
    }
}

void gui_redraw(void) {
    int i;
    gui_draw_desktop();
    for (i = 0; i < GUI_MAX_WINDOWS; i++) {
        gui_window_t* w = &gui_windows[i];
        if (!w->used) {
            continue;
        }
        gui_draw_window(w->x, w->y, w->w, w->h, w->title);
        gui_write_at(w->x + 2, w->y + 2, "Window content", COLOR_TEXT);
    }
    gui_draw_taskbar();
}

static int gui_find_slot_by_id(int id) {
    int i;
    for (i = 0; i < GUI_MAX_WINDOWS; i++) {
        if (gui_windows[i].used && gui_windows[i].id == id) {
            return i;
        }
    }
    return -1;
}

static int gui_find_icon_slot_by_id(int id) {
    int i;
    for (i = 0; i < GUI_MAX_ICONS; i++) {
        if (gui_icons[i].used && gui_icons[i].id == id) {
            return i;
        }
    }
    return -1;
}

int gui_window_open(const char* title, int x, int y, int w, int h) {
    int i;
    int slot = -1;

    for (i = 0; i < GUI_MAX_WINDOWS; i++) {
        if (!gui_windows[i].used) {
            slot = i;
            break;
        }
    }

    if (slot < 0) {
        return -1;
    }

    if (x < 0) x = 0;
    if (y < 0) y = 0;
    if (w < 10) w = 10;
    if (h < 5) h = 5;
    if (x + w > VGA_WIDTH) w = VGA_WIDTH - x;
    if (y + h > VGA_HEIGHT - 1) h = (VGA_HEIGHT - 1) - y;

    gui_windows[slot].used = 1;
    gui_windows[slot].id = gui_next_id++;
    gui_windows[slot].x = x;
    gui_windows[slot].y = y;
    gui_windows[slot].w = w;
    gui_windows[slot].h = h;
    kstrncpy(gui_windows[slot].title, title ? title : "Window", GUI_TITLE_MAX - 1);
    gui_windows[slot].title[GUI_TITLE_MAX - 1] = '\0';

    gui_focused_id = gui_windows[slot].id;
    gui_redraw();
    return gui_windows[slot].id;
}

int gui_window_close(int id) {
    int slot = gui_find_slot_by_id(id);
    if (slot < 0) {
        return -1;
    }

    kmemset(&gui_windows[slot], 0, sizeof(gui_window_t));
    if (gui_focused_id == id) {
        gui_focused_id = -1;
    }
    gui_redraw();
    return 0;
}

int gui_window_focus(int id) {
    int slot = gui_find_slot_by_id(id);
    gui_window_t temp;
    int i;

    if (slot < 0) {
        return -1;
    }

    temp = gui_windows[slot];
    for (i = slot; i < GUI_MAX_WINDOWS - 1; i++) {
        gui_windows[i] = gui_windows[i + 1];
    }
    gui_windows[GUI_MAX_WINDOWS - 1] = temp;
    gui_focused_id = id;
    gui_redraw();
    return 0;
}

int gui_window_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < GUI_MAX_WINDOWS; i++) {
        if (gui_windows[i].used) {
            count++;
        }
    }
    return count;
}

gui_window_t* gui_window_get(int index) {
    if (index < 0 || index >= GUI_MAX_WINDOWS) {
        return (gui_window_t*)0;
    }
    if (!gui_windows[index].used) {
        return (gui_window_t*)0;
    }
    return &gui_windows[index];
}

int gui_icon_add(const char* label, char glyph, int x, int y) {
    int i;
    int slot = -1;

    for (i = 0; i < GUI_MAX_ICONS; i++) {
        if (!gui_icons[i].used) {
            slot = i;
            break;
        }
    }

    if (slot < 0) {
        return -1;
    }

    if (x < 0) x = 0;
    if (y < 0) y = 0;
    if (x > VGA_WIDTH - 3) x = VGA_WIDTH - 3;
    if (y > VGA_HEIGHT - 3) y = VGA_HEIGHT - 3;

    gui_icons[slot].used = 1;
    gui_icons[slot].id = gui_next_icon_id++;
    gui_icons[slot].x = x;
    gui_icons[slot].y = y;
    gui_icons[slot].glyph = glyph ? glyph : '*';
    kstrncpy(gui_icons[slot].label, label ? label : "icon", GUI_ICON_LABEL_MAX - 1);
    gui_icons[slot].label[GUI_ICON_LABEL_MAX - 1] = '\0';

    gui_redraw();
    return gui_icons[slot].id;
}

int gui_icon_remove(int id) {
    int slot = gui_find_icon_slot_by_id(id);
    if (slot < 0) {
        return -1;
    }
    kmemset(&gui_icons[slot], 0, sizeof(gui_icon_t));
    gui_redraw();
    return 0;
}

int gui_icon_count(void) {
    int i;
    int count = 0;
    for (i = 0; i < GUI_MAX_ICONS; i++) {
        if (gui_icons[i].used) {
            count++;
        }
    }
    return count;
}

gui_icon_t* gui_icon_get(int index) {
    if (index < 0 || index >= GUI_MAX_ICONS) {
        return (gui_icon_t*)0;
    }
    if (!gui_icons[index].used) {
        return (gui_icon_t*)0;
    }
    return &gui_icons[index];
}

void gui_demo(void) {
    gui_init();
    gui_window_open("System Monitor", 2, 1, 36, 10);
    gui_window_open("File Manager", 42, 2, 36, 12);
    gui_window_open("Console", 8, 13, 64, 9);
    gui_window_open("Settings", 24, 7, 28, 8);
    gui_redraw();
}
