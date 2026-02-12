#ifndef MEMORY_H
#define MEMORY_H

#include "types.h"

void* kmemset(void* dest, int value, size_t count);
void* kmemcpy(void* dest, const void* src, size_t count);
void* kmemmove(void* dest, const void* src, size_t count);
int kmemcmp(const void* a, const void* b, size_t count);

u32 align_up(u32 value, u32 alignment);
u32 align_down(u32 value, u32 alignment);

#endif
