#ifndef KONE_GUI_CORE_H
#define KONE_GUI_CORE_H

#include "../../lib/kone_types.h"

#define GUI_MAX_WINDOWS 32
#define GUI_TITLE_MAX   48

typedef struct {
    int used;
    int id;
    int x;
    int y;
    int w;
    int h;
    int z;
    int minimized;
    int maximized;
    char title[GUI_TITLE_MAX];
} gui_window_t;

typedef struct {
    k_u32 width;
    k_u32 height;
    k_u32 *pixels;
} gui_framebuffer_t;

void zk_gui_core_init(k_u32 width, k_u32 height);
int zk_window_create(const char *title, int x, int y, int w, int h);
int zk_window_move(int id, int nx, int ny);
int zk_window_resize(int id, int nw, int nh);
int zk_window_minimize(int id);
int zk_window_maximize(int id);
int zk_window_close(int id);
void zk_window_focus(int id);
void zk_render_frame(void);

#endif
