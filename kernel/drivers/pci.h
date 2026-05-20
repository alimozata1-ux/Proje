#ifndef PCI_H
#define PCI_H
#include <stdint.h>

typedef struct {
    uint16_t vendor_id;
    uint16_t device_id;
    uint32_t io_base;
    uint8_t irq_line;
    uint8_t bus, slot, func;
    uint8_t found;
} pci_rtl8139_info_t;

uint16_t pci_config_read_word(uint8_t bus, uint8_t slot, uint8_t func, uint8_t offset);
uint32_t pci_config_read_dword(uint8_t bus, uint8_t slot, uint8_t func, uint8_t offset);
void pci_scan_for_rtl8139(pci_rtl8139_info_t *info);

#endif
