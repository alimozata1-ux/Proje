#include <stdint.h>
#include <stddef.h>
#include "graphics.h"

#define MAX_WIDTH  1024
#define MAX_HEIGHT 768

static uint32_t *g_lfb = (uint32_t *)0;
static uint32_t g_width = 0;
static uint32_t g_height = 0;
static uint32_t g_bpp = 0;

static uint32_t backbuffer[MAX_WIDTH * MAX_HEIGHT];

struct gdt_ptr {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed));

const uint32_t folder_icon_8x8[64] = {
    0x00000000,0x00000000,0x00C99000,0x00C99000,0x00C99000,0x00C99000,0x00000000,0x00000000,
    0x00000000,0x00E1A800,0x00F0B800,0x00F0B800,0x00F0B800,0x00E1A800,0x00C99000,0x00000000,
    0x00C99000,0x00F4C400,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00F4C400,0x00E1A800,0x00C99000,
    0x00C99000,0x00F4C400,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00F4C400,0x00C99000,
    0x00C99000,0x00F4C400,0x00FFD24A,0x00FFE07A,0x00FFE07A,0x00FFD24A,0x00F4C400,0x00C99000,
    0x00C99000,0x00F4C400,0x00FFD24A,0x00FFD24A,0x00FFD24A,0x00F4C400,0x00E1A800,0x00C99000,
    0x00000000,0x00E1A800,0x00F0B800,0x00F0B800,0x00F0B800,0x00E1A800,0x00C99000,0x00000000,
    0x00000000,0x00000000,0x00C99000,0x00C99000,0x00C99000,0x00C99000,0x00000000,0x00000000
};

void gdt_sanity_check(void) {
    struct gdt_ptr gdt = {0, 0};
    __asm__ __volatile__("sgdt %0" : "=m"(gdt));

    if (gdt.limit == 0 || gdt.base == 0) {
        for (;;) {
            __asm__ __volatile__("cli; hlt");
        }
    }
}

void graphics_init(uint32_t lfb_addr, uint32_t width, uint32_t height, uint32_t bpp) {
    g_lfb = (uint32_t *)(uintptr_t)lfb_addr;
    g_width = (width > MAX_WIDTH) ? MAX_WIDTH : width;
    g_height = (height > MAX_HEIGHT) ? MAX_HEIGHT : height;
    g_bpp = bpp;
}

void put_pixel(int x, int y, uint32_t color) {
    if (x < 0 || y < 0) return;
    if ((uint32_t)x >= g_width || (uint32_t)y >= g_height) return;

    backbuffer[(uint32_t)y * g_width + (uint32_t)x] = color;
}

void clear_screen(uint32_t color) {
    uint32_t total = g_width * g_height;
    for (uint32_t i = 0; i < total; ++i) {
        backbuffer[i] = color;
    }
}

void draw_rect(int x, int y, int width, int height, uint32_t color) {
    if (width <= 0 || height <= 0) return;

    for (int py = 0; py < height; ++py) {
        for (int px = 0; px < width; ++px) {
            put_pixel(x + px, y + py, color);
        }
    }
}

void draw_icon(int x, int y, const uint32_t *icon_data, int icon_w, int icon_h) {
    if (icon_data == NULL || icon_w <= 0 || icon_h <= 0) return;

    for (int row = 0; row < icon_h; ++row) {
        for (int col = 0; col < icon_w; ++col) {
            uint32_t color = icon_data[row * icon_w + col];
            if (color != 0x00000000u) {
                put_pixel(x + col, y + row, color);
            }
        }
    }
}

void screen_blit(void) {
    if (g_lfb == NULL || g_bpp != 32) return;

    uint32_t total = g_width * g_height;
    for (uint32_t i = 0; i < total; ++i) {
        g_lfb[i] = backbuffer[i];
    }
}

uint32_t graphics_width(void) { return g_width; }
uint32_t graphics_height(void) { return g_height; }
