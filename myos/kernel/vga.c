#include "vga.h"

#define VGA_MEMORY ((volatile unsigned short*)0xB8000)
#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_COLOR 0x0F

static int cursor_row = 0;
static int cursor_col = 0;

static unsigned short vga_entry(char c, unsigned char color) {
    return ((unsigned short)color << 8) | (unsigned char)c;
}

void vga_clear(void) {
    int i;
    for (i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        VGA_MEMORY[i] = vga_entry(' ', VGA_COLOR);
    }
    cursor_row = 0;
    cursor_col = 0;
}

void vga_put_char(char c) {
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        int index = cursor_row * VGA_WIDTH + cursor_col;
        VGA_MEMORY[index] = vga_entry(c, VGA_COLOR);
        cursor_col++;
        if (cursor_col >= VGA_WIDTH) {
            cursor_col = 0;
            cursor_row++;
        }
    }

    if (cursor_row >= VGA_HEIGHT) {
        cursor_row = 0;
    }
}

void vga_write_string(const char* str) {
    while (*str) {
        vga_put_char(*str++);
    }
}
