#include "rtl8139.h"
#include "pci.h"
#include "../cpu/idt.h"
#include "../net/net_stack.h"

static inline void outb(uint16_t p,uint8_t v){__asm__ __volatile__("outb %0,%1"::"a"(v),"Nd"(p));}
static inline void outw(uint16_t p,uint16_t v){__asm__ __volatile__("outw %0,%1"::"a"(v),"Nd"(p));}
static inline void outl(uint16_t p,uint32_t v){__asm__ __volatile__("outl %0,%1"::"a"(v),"Nd"(p));}
static inline uint8_t inb(uint16_t p){uint8_t r;__asm__ __volatile__("inb %1,%0":"=a"(r):"Nd"(p));return r;}
static inline uint16_t inw(uint16_t p){uint16_t r;__asm__ __volatile__("inw %1,%0":"=a"(r):"Nd"(p));return r;}

enum { REG_IDR0=0x00, REG_RBSTART=0x30, REG_CMD=0x37, REG_IMR=0x3C, REG_ISR=0x3E, REG_RCR=0x44, REG_TSD0=0x10, REG_TSAD0=0x20, REG_CONFIG1=0x52 };
static uint16_t io_base=0; static uint8_t irq_line=0;
static uint8_t rx_buffer[8192+16+1500] __attribute__((aligned(16)));
static uint8_t tx_buffer[4][2048] __attribute__((aligned(16)));
static uint32_t rx_off=0; static uint8_t tx_cur=0;

extern void net_handle_packet(uint8_t*,uint32_t);

static void rtl_irq(registers_t *r){ (void)r; rtl8139_handler(r); }

int rtl8139_init(void){
    pci_rtl8139_info_t info; pci_scan_for_rtl8139(&info); if(!info.found) return -1;
    io_base=(uint16_t)info.io_base; irq_line=info.irq_line;
    outb(io_base+REG_CONFIG1,0x00); outb(io_base+REG_CMD,0x10); while(inb(io_base+REG_CMD)&0x10){}
    outl(io_base+REG_RBSTART,(uint32_t)(uintptr_t)rx_buffer);
    outw(io_base+REG_IMR,0x0005); outw(io_base+REG_ISR,0xFFFF);
    outl(io_base+REG_RCR,0x0000F | (1<<7));
    outb(io_base+REG_CMD,0x0C);
    for(int i=0;i<6;i++) g_net_mac[i]=inb(io_base+REG_IDR0+i);
    if(irq_line>=8) irq_install_handler((uint8_t)(irq_line), rtl_irq); else irq_install_handler((uint8_t)(irq_line), rtl_irq);
    return 0;
}

void rtl8139_send_packet(void *packet, uint32_t length){
    if(!io_base||!packet||length==0||length>2048) return;
    uint8_t idx=tx_cur%4; uint8_t *dst=tx_buffer[idx]; uint8_t *src=(uint8_t*)packet;
    for(uint32_t i=0;i<length;i++) dst[i]=src[i];
    outl(io_base+REG_TSAD0+idx*4,(uint32_t)(uintptr_t)dst);
    outl(io_base+REG_TSD0+idx*4,length & 0x1FFF);
    tx_cur=(tx_cur+1)&3; g_net_activity_blink=8;
}

void rtl8139_handler(void *regs){
    (void)regs; if(!io_base) return;
    uint16_t status=inw(io_base+REG_ISR); outw(io_base+REG_ISR,status);
    if(status & 0x0001){
        while(!(inb(io_base+REG_CMD)&0x01)){
            uint8_t *pkt=rx_buffer + (rx_off % 8192);
            uint16_t pkt_status = (uint16_t)(pkt[0] | (pkt[1]<<8));
            uint16_t pkt_len = (uint16_t)(pkt[2] | (pkt[3]<<8));
            if(!(pkt_status & 0x01) || pkt_len<4 || pkt_len>1518) break;
            net_handle_packet(pkt+4, pkt_len-4);
            rx_off = (rx_off + pkt_len + 4 + 3) & ~3u;
            if(rx_off >= 8192) rx_off -= 8192;
            outw(io_base + 0x38, (uint16_t)(rx_off - 16));
            g_net_activity_blink=8;
        }
    }
}
