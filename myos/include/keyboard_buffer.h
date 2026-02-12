#ifndef KEYBOARD_BUFFER_H
#define KEYBOARD_BUFFER_H

#include "types.h"

#define KBD_BUFFER_CAPACITY 256

void kbd_buffer_init(void);
int kbd_buffer_push(char c);
int kbd_buffer_pop(char* out);
int kbd_buffer_size(void);
int kbd_buffer_empty(void);

#endif
