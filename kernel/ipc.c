#include "ipc.h"
#include "../lib/kone_string.h"

static ipc_message_t q[IPC_QUEUE_CAP];
static k_u32 head;
static k_u32 tail;
static k_u32 count;

void ipc_init(void) {
    head = tail = count = 0;
}

int ipc_send(const ipc_message_t *msg) {
    if (!msg || count >= IPC_QUEUE_CAP) return -1;
    q[tail] = *msg;
    tail = (tail + 1) % IPC_QUEUE_CAP;
    count++;
    return 0;
}

int ipc_recv(ipc_message_t *msg) {
    if (!msg || count == 0) return -1;
    *msg = q[head];
    head = (head + 1) % IPC_QUEUE_CAP;
    count--;
    return 0;
}
