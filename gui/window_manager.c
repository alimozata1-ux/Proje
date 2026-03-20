#include "include/gui_core.h"
#include "../kernel/console.h"
#include "../lib/kone_string.h"

static gui_window_t g_windows[GUI_MAX_WINDOWS];
static int g_next_id = 1;

static gui_window_t *find_by_id(int id) {
    for (int i = 0; i < GUI_MAX_WINDOWS; i++) {
        if (g_windows[i].used && g_windows[i].id == id) {
            return &g_windows[i];
        }
    }
    return 0;
}

static int next_z(void) {
    int z = 0;
    for (int i = 0; i < GUI_MAX_WINDOWS; i++) {
        if (g_windows[i].used && g_windows[i].z >= z) z = g_windows[i].z + 1;
    }
    return z;
}

int zk_window_create(const char *title, int x, int y, int w, int h) {
    for (int i = 0; i < GUI_MAX_WINDOWS; i++) {
        if (!g_windows[i].used) {
            g_windows[i].used = 1;
            g_windows[i].id = g_next_id++;
            g_windows[i].x = x;
            g_windows[i].y = y;
            g_windows[i].w = w;
            g_windows[i].h = h;
            g_windows[i].z = next_z();
            g_windows[i].minimized = 0;
            g_windows[i].maximized = 0;
            size_t n = k_strlen(title);
            if (n >= GUI_TITLE_MAX) n = GUI_TITLE_MAX - 1;
            k_memcpy(g_windows[i].title, title, n);
            g_windows[i].title[n] = '\0';
            return g_windows[i].id;
        }
    }
    return -1;
}

int zk_window_move(int id, int nx, int ny) {
    gui_window_t *w = find_by_id(id);
    if (!w) return -1;
    w->x = nx;
    w->y = ny;
    return 0;
}

int zk_window_resize(int id, int nw, int nh) {
    gui_window_t *w = find_by_id(id);
    if (!w || nw < 80 || nh < 80) return -1;
    w->w = nw;
    w->h = nh;
    return 0;
}

int zk_window_minimize(int id) {
    gui_window_t *w = find_by_id(id);
    if (!w) return -1;
    w->minimized = 1;
    w->maximized = 0;
    return 0;
}

int zk_window_maximize(int id) {
    gui_window_t *w = find_by_id(id);
    if (!w) return -1;
    w->maximized = 1;
    w->minimized = 0;
    w->x = 0;
    w->y = 28;
    w->w = 1024;
    w->h = 528;
    return 0;
}

int zk_window_close(int id) {
    gui_window_t *w = find_by_id(id);
    if (!w) return -1;
    w->used = 0;
    return 0;
}

void zk_window_focus(int id) {
    gui_window_t *w = find_by_id(id);
    if (!w) return;
    w->z = next_z();
}

void zk_window_manager_init(void) {
    k_memset(g_windows, 0, sizeof(g_windows));

    int term = zk_window_create("Terminal", 80, 72, 620, 380);
    int files = zk_window_create("Dosya Yonetici", 240, 110, 520, 340);
    zk_window_focus(term);
    zk_window_minimize(files);

    console_puts("[Z] Window manager initialized (Android-like task workflow)\n");
}
