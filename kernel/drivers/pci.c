#include "pci.h"

static inline void outl(uint16_t p, uint32_t v){ __asm__ __volatile__("outl %0,%1"::"a"(v),"Nd"(p)); }
static inline uint32_t inl(uint16_t p){ uint32_t r; __asm__ __volatile__("inl %1,%0":"=a"(r):"Nd"(p)); return r; }

uint32_t pci_config_read_dword(uint8_t bus, uint8_t slot, uint8_t func, uint8_t offset){
    uint32_t addr=(1u<<31)|((uint32_t)bus<<16)|((uint32_t)slot<<11)|((uint32_t)func<<8)|(offset&0xFC);
    outl(0xCF8,addr); return inl(0xCFC);
}
uint16_t pci_config_read_word(uint8_t bus, uint8_t slot, uint8_t func, uint8_t offset){
    uint32_t d=pci_config_read_dword(bus,slot,func,offset);
    return (uint16_t)((d >> ((offset&2)*8)) & 0xFFFF);
}

void pci_scan_for_rtl8139(pci_rtl8139_info_t *info){
    info->found=0;
    for(uint16_t bus=0;bus<256;bus++) for(uint8_t slot=0;slot<32;slot++) for(uint8_t fn=0;fn<8;fn++){
        uint16_t ven=pci_config_read_word(bus,slot,fn,0x00); if(ven==0xFFFF) continue;
        uint16_t dev=pci_config_read_word(bus,slot,fn,0x02);
        if(ven==0x10EC && dev==0x8139){
            uint32_t bar0=pci_config_read_dword(bus,slot,fn,0x10);
            uint8_t irq=(uint8_t)(pci_config_read_word(bus,slot,fn,0x3C)&0xFF);
            info->vendor_id=ven; info->device_id=dev; info->io_base=bar0 & ~0x3u; info->irq_line=irq;
            info->bus=bus; info->slot=slot; info->func=fn; info->found=1; return;
        }
    }
}
