#ifndef KONE_STRING_H
#define KONE_STRING_H

#include "kone_types.h"

size_t k_strlen(const char *s);
void *k_memset(void *dst, int value, size_t n);
void *k_memcpy(void *dst, const void *src, size_t n);
int k_strcmp(const char *a, const char *b);

#endif
