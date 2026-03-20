#ifndef KONE_TOUCH_H
#define KONE_TOUCH_H

typedef struct {
    int x;
    int y;
    int down;
} touch_point_t;

void yk_touch_init(void);
void yk_touch_update(int mouse_x, int mouse_y, int mouse_down);
touch_point_t yk_touch_get(void);

#endif
