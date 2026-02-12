#include "memory.h"

void* kmemset(void* dest, int value, size_t count) {
    size_t i;
    unsigned char* d = (unsigned char*)dest;
    for (i = 0; i < count; i++) {
        d[i] = (unsigned char)value;
    }
    return dest;
}

void* kmemcpy(void* dest, const void* src, size_t count) {
    size_t i;
    unsigned char* d = (unsigned char*)dest;
    const unsigned char* s = (const unsigned char*)src;
    for (i = 0; i < count; i++) {
        d[i] = s[i];
    }
    return dest;
}

void* kmemmove(void* dest, const void* src, size_t count) {
    size_t i;
    unsigned char* d = (unsigned char*)dest;
    const unsigned char* s = (const unsigned char*)src;

    if (d == s || count == 0) {
        return dest;
    }

    if (d < s) {
        for (i = 0; i < count; i++) {
            d[i] = s[i];
        }
    } else {
        for (i = count; i > 0; i--) {
            d[i - 1] = s[i - 1];
        }
    }

    return dest;
}

int kmemcmp(const void* a, const void* b, size_t count) {
    size_t i;
    const unsigned char* pa = (const unsigned char*)a;
    const unsigned char* pb = (const unsigned char*)b;
    for (i = 0; i < count; i++) {
        if (pa[i] != pb[i]) {
            return (int)pa[i] - (int)pb[i];
        }
    }
    return 0;
}

u32 align_up(u32 value, u32 alignment) {
    if (alignment == 0) {
        return value;
    }
    return (value + alignment - 1U) & ~(alignment - 1U);
}

u32 align_down(u32 value, u32 alignment) {
    if (alignment == 0) {
        return value;
    }
    return value & ~(alignment - 1U);
}
