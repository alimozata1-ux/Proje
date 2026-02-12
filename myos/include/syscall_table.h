#ifndef SYSCALL_TABLE_H
#define SYSCALL_TABLE_H

#include "types.h"

typedef u32 (*syscall_fn_t)(u32, u32, u32, u32);

void syscall_table_init(void);
u32 syscall_table_dispatch(u32 id, u32 a, u32 b, u32 c, u32 d);

#endif
