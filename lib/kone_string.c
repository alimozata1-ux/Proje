#include "kone_string.h"

size_t k_strlen(const char *s) {
    size_t n = 0;
    while (s && s[n]) {
        n++;
    }
    return n;
}

void *k_memset(void *dst, int value, size_t n) {
    k_u8 *d = (k_u8 *)dst;
    for (size_t i = 0; i < n; i++) {
        d[i] = (k_u8)value;
    }
    return dst;
}

void *k_memcpy(void *dst, const void *src, size_t n) {
    k_u8 *d = (k_u8 *)dst;
    const k_u8 *s = (const k_u8 *)src;
    for (size_t i = 0; i < n; i++) {
        d[i] = s[i];
    }
    return dst;
}

int k_strcmp(const char *a, const char *b) {
    size_t i = 0;
    while (a[i] && b[i]) {
        if (a[i] != b[i]) {
            return (int)((unsigned char)a[i] - (unsigned char)b[i]);
        }
        i++;
    }
    return (int)((unsigned char)a[i] - (unsigned char)b[i]);
}
