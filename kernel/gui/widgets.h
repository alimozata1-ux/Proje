#ifndef WIDGETS_H
#define WIDGETS_H
#include <stdint.h>

#define MAX_BUTTONS 64
#define MAX_TEXTBOXES 64

typedef struct {
    uint32_t id;
    int x, y, width, height;
    char label[32];
    uint8_t is_pressed;
    void (*on_click)(void);
} Button;

typedef struct {
    uint32_t id;
    int x, y, width, height;
    char text_buffer[256];
    uint32_t buffer_index;
    uint8_t is_focused;
} TextBox;

void widgets_init(void);
Button *button_create(int x,int y,int w,int h,const char *label,void (*on_click)(void));
TextBox *textbox_create(int x,int y,int w,int h);
void widget_draw_button(Button *b, int ox, int oy);
void widget_draw_textbox(TextBox *t, int ox, int oy);
int widget_button_hit(Button *b, int px, int py, int ox, int oy);
int widget_textbox_hit(TextBox *t, int px, int py, int ox, int oy);
void widget_textbox_input(TextBox *t, char c);

#endif
