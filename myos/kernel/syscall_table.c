#include "syscall_table.h"
#include "allocator.h"
#include "logger.h"
#include "memory.h"
#include "string.h"
#include "vga.h"

#define SYSCALL_MAX 64

static syscall_fn_t syscall_table[SYSCALL_MAX];

static u32 sys_nop(u32 a, u32 b, u32 c, u32 d) {
    (void)a; (void)b; (void)c; (void)d;
    return 0;
}

static u32 sys_write(u32 ptr, u32 b, u32 c, u32 d) {
    (void)b; (void)c; (void)d;
    vga_write_string((const char*)ptr);
    return 0;
}

static u32 sys_strlen(u32 ptr, u32 b, u32 c, u32 d) {
    (void)b; (void)c; (void)d;
    return (u32)kstrlen((const char*)ptr);
}

static u32 sys_alloc(u32 size, u32 b, u32 c, u32 d) {
    (void)b; (void)c; (void)d;
    return (u32)kmalloc(size);
}

static u32 sys_memset(u32 ptr, u32 value, u32 count, u32 d) {
    (void)d;
    kmemset((void*)ptr, (int)value, (size_t)count);
    return ptr;
}

static u32 sys_echo_id(u32 id, u32 b, u32 c, u32 d) {
    (void)b; (void)c; (void)d;
    return id;
}

static void register_syscall(u32 id, syscall_fn_t fn) {
    if (id < SYSCALL_MAX) {
        syscall_table[id] = fn;
    }
}

void syscall_table_init(void) {
    u32 i;
    for (i = 0; i < SYSCALL_MAX; i++) {
        syscall_table[i] = sys_nop;
    }

    register_syscall(0, sys_nop);
    register_syscall(1, sys_write);
    register_syscall(2, sys_strlen);
    register_syscall(3, sys_alloc);
    register_syscall(4, sys_memset);
    register_syscall(5, sys_echo_id);

    log_info("syscall", "table initialized");
}

u32 syscall_table_dispatch(u32 id, u32 a, u32 b, u32 c, u32 d) {
    if (id >= SYSCALL_MAX) {
        return (u32)-1;
    }
    return syscall_table[id](a, b, c, d);
}
