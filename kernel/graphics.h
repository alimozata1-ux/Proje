#ifndef GRAPHICS_H
#define GRAPHICS_H
#include <stdint.h>

void graphics_init(uint32_t lfb_addr, uint32_t width, uint32_t height, uint32_t bpp);
void put_pixel(int x, int y, uint32_t color);
void clear_screen(uint32_t color);
void draw_rect(int x, int y, int width, int height, uint32_t color);
void draw_icon(int x, int y, const uint32_t *icon_data, int icon_w, int icon_h);
void screen_blit(void);
void gdt_sanity_check(void);
uint32_t graphics_width(void);
uint32_t graphics_height(void);

#endif
