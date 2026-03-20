#ifndef KONE_IPC_H
#define KONE_IPC_H

#include "../lib/kone_types.h"

#define IPC_QUEUE_CAP 32
#define IPC_MSG_SIZE  64

typedef struct {
    k_u32 from;
    k_u32 to;
    char payload[IPC_MSG_SIZE];
} ipc_message_t;

void ipc_init(void);
int ipc_send(const ipc_message_t *msg);
int ipc_recv(ipc_message_t *msg);

#endif
