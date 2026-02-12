#ifndef TYPES_H
#define TYPES_H

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;

typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
typedef signed long long s64;

typedef u32 size_t;
typedef s32 ssize_t;

typedef enum {
    FALSE = 0,
    TRUE = 1
} bool_t;

#endif
