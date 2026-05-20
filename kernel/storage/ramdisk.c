#include "ramdisk.h"

static uint8_t g_ramdisk[RAMDISK_SIZE_BYTES];

static void write_u16(uint8_t *p, uint16_t v){ p[0]=v&0xFF; p[1]=(v>>8)&0xFF; }
static void write_u32(uint8_t *p, uint32_t v){ p[0]=v&0xFF; p[1]=(v>>8)&0xFF; p[2]=(v>>16)&0xFF; p[3]=(v>>24)&0xFF; }

static void ramdisk_seed_demo_fat16(void) {
    uint8_t *b = &g_ramdisk[0];
    b[0]=0xEB; b[1]=0x3C; b[2]=0x90;
    b[3]='M';b[4]='S';b[5]='D';b[6]='O';b[7]='S';b[8]='5';b[9]='.';b[10]='0';
    write_u16(&b[11], 512); b[13]=1; write_u16(&b[14],1); b[16]=1; write_u16(&b[17],64);
    write_u16(&b[19], RAMDISK_TOTAL_SECTORS); b[21]=0xF8; write_u16(&b[22],32); write_u16(&b[24],63); write_u16(&b[26],16);
    write_u32(&b[28],0); write_u32(&b[32],0); b[36]=0x80; b[38]=0x29; write_u32(&b[39],0x12345678);
    const char *lbl="LUNAOS     "; for(int i=0;i<11;i++) b[43+i]=lbl[i]; const char *fst="FAT16   "; for(int i=0;i<8;i++) b[54+i]=fst[i];
    b[510]=0x55; b[511]=0xAA;

    uint8_t *fat = &g_ramdisk[512*1];
    fat[0]=0xF8; fat[1]=0xFF; fat[2]=0xFF; fat[3]=0xFF; /* clus2 eof */ fat[4]=0xFF; fat[5]=0xFF;

    uint8_t *root = &g_ramdisk[512*(1+32)];
    const char *name="NOTEPAD ELF"; for(int i=0;i<11;i++) root[i]=name[i]; root[11]=0x20; write_u16(&root[26],2);

    uint8_t *file = &g_ramdisk[512*(1+32+4)];
    uint8_t elf[84]={0}; elf[0]=0x7F; elf[1]='E'; elf[2]='L'; elf[3]='F'; elf[4]=1; elf[5]=1; elf[6]=1;
    elf[16]=2; elf[18]=3; elf[20]=1; write_u32(&elf[24],0x200000); write_u32(&elf[28],52); elf[40]=52; elf[42]=32; elf[44]=1;
    elf[52]=1; write_u32(&elf[56],0x80); write_u32(&elf[60],0x200000); write_u32(&elf[64],0x200000); write_u32(&elf[68],4); write_u32(&elf[72],4);
    elf[80]=0xCD; elf[81]=0x80; elf[82]=0xEB; elf[83]=0xFE;
    for(int i=0;i<84;i++) file[i]=elf[i];
    write_u32(&root[28],84);
}

void ramdisk_init(void) {
    for (uint32_t i = 0; i < RAMDISK_SIZE_BYTES; ++i) g_ramdisk[i] = 0;
    ramdisk_seed_demo_fat16();
}

int ramdisk_read_sector(uint32_t sector_num, uint8_t *buffer) {
    if (!buffer || sector_num >= RAMDISK_TOTAL_SECTORS) return -1;
    uint32_t base = sector_num * RAMDISK_SECTOR_SIZE;
    for (uint32_t i = 0; i < RAMDISK_SECTOR_SIZE; ++i) buffer[i] = g_ramdisk[base + i];
    return 0;
}

int ramdisk_write_sector(uint32_t sector_num, const uint8_t *buffer) {
    if (!buffer || sector_num >= RAMDISK_TOTAL_SECTORS) return -1;
    uint32_t base = sector_num * RAMDISK_SECTOR_SIZE;
    for (uint32_t i = 0; i < RAMDISK_SECTOR_SIZE; ++i) g_ramdisk[base + i] = buffer[i];
    return 0;
}
