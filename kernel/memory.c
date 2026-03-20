#include "memory.h"
#include "console.h"

#define HEAP_SIZE (64 * 1024)

/* Basit bump allocator (erken boot aşaması için). */
static k_u8 heap[HEAP_SIZE];
static k_u32 heap_offset;

void xk_memory_init(void) {
    heap_offset = 0;
    console_puts("[X] Memory init (bump allocator)\n");
}

void *xk_kmalloc(k_u32 size) {
    if (heap_offset + size > HEAP_SIZE) {
        return 0;
    }
    void *p = &heap[heap_offset];
    heap_offset += size;
    return p;
}
