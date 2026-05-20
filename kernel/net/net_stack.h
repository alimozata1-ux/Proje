#ifndef NET_STACK_H
#define NET_STACK_H
#include <stdint.h>

#define htons(x) (uint16_t)((((uint16_t)(x)&0x00FF)<<8)|(((uint16_t)(x)&0xFF00)>>8))
#define ntohs(x) htons(x)
#define htonl(x) (uint32_t)((((uint32_t)(x)&0x000000FF)<<24)|(((uint32_t)(x)&0x0000FF00)<<8)|(((uint32_t)(x)&0x00FF0000)>>8)|(((uint32_t)(x)&0xFF000000)>>24))
#define ntohl(x) htonl(x)

#pragma pack(push,1)
typedef struct { uint8_t dst[6]; uint8_t src[6]; uint16_t type; } eth_hdr_t;
typedef struct { uint16_t htype,ptype; uint8_t hlen,plen; uint16_t oper; uint8_t sha[6],spa[4],tha[6],tpa[4]; } arp_hdr_t;
typedef struct { uint8_t ver_ihl,tos; uint16_t total_len,id,frag_off; uint8_t ttl,proto; uint16_t check; uint32_t src_ip,dst_ip; } ip_hdr_t;
typedef struct { uint16_t src_port,dst_port,len,check; } udp_hdr_t;
typedef struct { uint8_t type,code; uint16_t checksum,id,seq; } icmp_echo_t;
#pragma pack(pop)

extern uint8_t g_net_mac[6];
extern uint8_t g_net_ip[4];
extern volatile uint8_t g_net_activity_blink;

void net_stack_init(void);
void net_handle_packet(uint8_t *buffer, uint32_t length);
uint16_t net_checksum16(const void *data, uint32_t length);

#endif
