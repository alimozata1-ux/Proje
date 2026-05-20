#ifndef XP_ASSETS_H
#define XP_ASSETS_H
#include <stdint.h>

extern const uint32_t xp_luna_palette[2048];
extern const uint8_t xp_gradient_lut[2048];
uint32_t xp_palette_get(uint32_t idx);
uint8_t xp_lut_get(uint32_t idx);

#endif
