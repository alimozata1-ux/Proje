#ifndef KSTRING_H
#define KSTRING_H

#include "types.h"

size_t kstrlen(const char* s);
size_t kstrnlen(const char* s, size_t max_len);
char* kstrcpy(char* dst, const char* src);
char* kstrncpy(char* dst, const char* src, size_t n);
int kstrcmp(const char* a, const char* b);
int kstrncmp(const char* a, const char* b, size_t n);
char* kstrchr(const char* s, int c);
char* kstrrchr(const char* s, int c);

int katoi(const char* s);
void kutoa(u32 value, char* out);
void kitoa(s32 value, char* out);

#endif
