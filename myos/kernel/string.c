#include "string.h"

size_t kstrlen(const char* s) {
    size_t len = 0;
    while (s[len]) {
        len++;
    }
    return len;
}

size_t kstrnlen(const char* s, size_t max_len) {
    size_t len = 0;
    while (len < max_len && s[len]) {
        len++;
    }
    return len;
}

char* kstrcpy(char* dst, const char* src) {
    size_t i = 0;
    while (src[i]) {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
    return dst;
}

char* kstrncpy(char* dst, const char* src, size_t n) {
    size_t i;
    for (i = 0; i < n && src[i]; i++) {
        dst[i] = src[i];
    }
    for (; i < n; i++) {
        dst[i] = '\0';
    }
    return dst;
}

int kstrcmp(const char* a, const char* b) {
    while (*a && *b && *a == *b) {
        a++;
        b++;
    }
    return (int)(unsigned char)*a - (int)(unsigned char)*b;
}

int kstrncmp(const char* a, const char* b, size_t n) {
    size_t i;
    for (i = 0; i < n; i++) {
        if (a[i] != b[i] || a[i] == '\0' || b[i] == '\0') {
            return (int)(unsigned char)a[i] - (int)(unsigned char)b[i];
        }
    }
    return 0;
}

char* kstrchr(const char* s, int c) {
    while (*s) {
        if (*s == (char)c) {
            return (char*)s;
        }
        s++;
    }
    return (c == 0) ? (char*)s : (char*)0;
}

char* kstrrchr(const char* s, int c) {
    const char* last = 0;
    while (*s) {
        if (*s == (char)c) {
            last = s;
        }
        s++;
    }
    if (c == 0) {
        return (char*)s;
    }
    return (char*)last;
}

int katoi(const char* s) {
    int sign = 1;
    int result = 0;
    if (*s == '-') {
        sign = -1;
        s++;
    }
    while (*s >= '0' && *s <= '9') {
        result = result * 10 + (*s - '0');
        s++;
    }
    return result * sign;
}

void kutoa(u32 value, char* out) {
    char tmp[16];
    int i = 0;
    int j;
    if (value == 0) {
        out[0] = '0';
        out[1] = '\0';
        return;
    }
    while (value > 0) {
        tmp[i++] = (char)('0' + (value % 10U));
        value /= 10U;
    }
    for (j = 0; j < i; j++) {
        out[j] = tmp[i - j - 1];
    }
    out[i] = '\0';
}

void kitoa(s32 value, char* out) {
    if (value < 0) {
        out[0] = '-';
        kutoa((u32)(-value), out + 1);
    } else {
        kutoa((u32)value, out);
    }
}
