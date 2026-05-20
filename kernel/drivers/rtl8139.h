#ifndef RTL8139_H
#define RTL8139_H
#include <stdint.h>

int rtl8139_init(void);
void rtl8139_handler(void *regs);
void rtl8139_send_packet(void *packet, uint32_t length);

#endif
