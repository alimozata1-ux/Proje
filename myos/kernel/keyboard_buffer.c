#include "keyboard_buffer.h"

static char kbd_buffer[KBD_BUFFER_CAPACITY];
static int kbd_head = 0;
static int kbd_tail = 0;
static int kbd_count = 0;

void kbd_buffer_init(void) {
    kbd_head = 0;
    kbd_tail = 0;
    kbd_count = 0;
}

int kbd_buffer_push(char c) {
    if (kbd_count >= KBD_BUFFER_CAPACITY) {
        return 0;
    }

    kbd_buffer[kbd_tail] = c;
    kbd_tail = (kbd_tail + 1) % KBD_BUFFER_CAPACITY;
    kbd_count++;
    return 1;
}

int kbd_buffer_pop(char* out) {
    if (kbd_count <= 0) {
        return 0;
    }

    *out = kbd_buffer[kbd_head];
    kbd_head = (kbd_head + 1) % KBD_BUFFER_CAPACITY;
    kbd_count--;
    return 1;
}

int kbd_buffer_size(void) {
    return kbd_count;
}

int kbd_buffer_empty(void) {
    return kbd_count == 0;
}
