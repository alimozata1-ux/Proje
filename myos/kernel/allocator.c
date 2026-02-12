#include "allocator.h"

extern unsigned int __heap_start;
extern unsigned int __heap_end;

static unsigned int heap_current;

void allocator_init(void) {
    heap_current = (unsigned int)&__heap_start;
}

void* kmalloc(unsigned int size) {
    unsigned int aligned = (size + 7U) & ~7U;
    unsigned int next = heap_current + aligned;

    if (next > (unsigned int)&__heap_end) {
        return (void*)0;
    }

    {
        void* ptr = (void*)heap_current;
        heap_current = next;
        return ptr;
    }
}

void kfree(void* ptr) {
    (void)ptr;
    /* Minimal bump allocator: geri verme yok (eğitsel sadelik). */
}
