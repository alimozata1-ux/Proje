#ifndef GUI_H
#define GUI_H

#define GUI_MAX_WINDOWS 8
#define GUI_TITLE_MAX 24
#define GUI_MAX_ICONS 12
#define GUI_ICON_LABEL_MAX 12

typedef struct {
    int used;
    int id;
    int x;
    int y;
    int w;
    int h;
    char title[GUI_TITLE_MAX];
} gui_window_t;

typedef struct {
    int used;
    int id;
    int x;
    int y;
    char glyph;
    char label[GUI_ICON_LABEL_MAX];
} gui_icon_t;

void gui_init(void);
void gui_draw_desktop(void);
void gui_draw_window(int x, int y, int w, int h, const char* title);
void gui_redraw(void);
void gui_demo(void);

int gui_window_open(const char* title, int x, int y, int w, int h);
int gui_window_close(int id);
int gui_window_focus(int id);
int gui_window_count(void);
gui_window_t* gui_window_get(int index);

int gui_icon_add(const char* label, char glyph, int x, int y);
int gui_icon_remove(int id);
int gui_icon_count(void);
gui_icon_t* gui_icon_get(int index);

void gui_start_menu_toggle(void);
void gui_start_menu_open_terminal(void);

#endif
