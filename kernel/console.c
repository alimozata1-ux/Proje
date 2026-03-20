#include "console.h"

/* VGA text mode tabanlı düşük seviye log çıkışı. */
static volatile k_u16 *const VGA = (k_u16 *)0xB8000;
static k_u8 row = 0;
static k_u8 col = 0;
static const k_u8 color = 0x0F;

static void scroll_if_needed(void) {
    if (row < 25) return;
    for (k_u32 r = 1; r < 25; r++) {
        for (k_u32 c = 0; c < 80; c++) {
            VGA[(r - 1) * 80 + c] = VGA[r * 80 + c];
        }
    }
    for (k_u32 c = 0; c < 80; c++) {
        VGA[24 * 80 + c] = ((k_u16)color << 8) | ' ';
    }
    row = 24;
}

void console_clear(void) {
    for (k_u32 i = 0; i < 80 * 25; i++) {
        VGA[i] = ((k_u16)color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void console_putc(char c) {
    if (c == '\n') {
        col = 0;
        row++;
        scroll_if_needed();
        return;
    }
    VGA[row * 80 + col] = ((k_u16)color << 8) | (k_u8)c;
    col++;
    if (col >= 80) {
        col = 0;
        row++;
        scroll_if_needed();
    }
}

void console_puts(const char *s) {
    while (s && *s) {
        console_putc(*s++);
    }
}
