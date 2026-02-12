#ifndef ALLOCATOR_H
#define ALLOCATOR_H

void allocator_init(void);
void* kmalloc(unsigned int size);
void kfree(void* ptr);

#endif
