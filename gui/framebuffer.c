#include "include/gui_core.h"
#include "../kernel/console.h"
#include "../kernel/memory.h"
#include "../lib/kone_string.h"

static gui_framebuffer_t g_fb;

static void fb_clear(k_u32 color) {
    if (!g_fb.pixels) return;
    for (k_u32 i = 0; i < g_fb.width * g_fb.height; i++) {
        g_fb.pixels[i] = color;
    }
}

static void fb_fill_rect(int x, int y, int w, int h, k_u32 color) {
    if (!g_fb.pixels || w <= 0 || h <= 0) return;
    for (int yy = 0; yy < h; yy++) {
        int py = y + yy;
        if (py < 0 || py >= (int)g_fb.height) continue;
        for (int xx = 0; xx < w; xx++) {
            int px = x + xx;
            if (px < 0 || px >= (int)g_fb.width) continue;
            g_fb.pixels[(k_u32)py * g_fb.width + (k_u32)px] = color;
        }
    }
}

void zk_gui_core_init(k_u32 width, k_u32 height) {
    g_fb.width = width;
    g_fb.height = height;
    g_fb.pixels = (k_u32 *)xk_kmalloc(width * height * sizeof(k_u32));
    if (!g_fb.pixels) {
        console_puts("[Z] GUI framebuffer alloc failed\n");
        return;
    }
    fb_clear(0x101318);
    console_puts("[Z] GUI core framebuffer initialized\n");
}

void zk_framebuffer_init(void) {
    zk_gui_core_init(1024, 600);
    fb_fill_rect(0, 0, 1024, 28, 0x1E2433);   /* Android-like status bar */
    fb_fill_rect(0, 556, 1024, 44, 0x1A202D); /* taskbar */
    console_puts("[Z] Framebuffer abstraction initialized\n");
}
