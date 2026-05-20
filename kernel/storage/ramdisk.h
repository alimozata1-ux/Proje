#ifndef RAMDISK_H
#define RAMDISK_H
#include <stdint.h>

#define RAMDISK_SIZE_BYTES (4u * 1024u * 1024u)
#define RAMDISK_SECTOR_SIZE 512u
#define RAMDISK_TOTAL_SECTORS (RAMDISK_SIZE_BYTES / RAMDISK_SECTOR_SIZE)

void ramdisk_init(void);
int ramdisk_read_sector(uint32_t sector_num, uint8_t *buffer);
int ramdisk_write_sector(uint32_t sector_num, const uint8_t *buffer);

#endif
