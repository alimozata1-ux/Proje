#include "net_stack.h"

uint8_t g_net_mac[6]={0x52,0x54,0x00,0x12,0x34,0x56};
uint8_t g_net_ip[4]={10,0,2,15};
volatile uint8_t g_net_activity_blink=0;

void net_stack_init(void){ g_net_activity_blink=0; }

uint16_t net_checksum16(const void *data, uint32_t length){
    const uint8_t *b=(const uint8_t*)data; uint32_t sum=0;
    for(uint32_t i=0;i+1<length;i+=2) sum += (uint16_t)((b[i]<<8)|b[i+1]);
    if(length&1) sum += (uint16_t)(b[length-1]<<8);
    while(sum>>16) sum=(sum&0xFFFF)+(sum>>16);
    return (uint16_t)(~sum);
}
