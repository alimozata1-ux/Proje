#include "fat.h"
#include "../storage/ramdisk.h"

static fat_bpb_t g_bpb;
static uint32_t g_root_dir_sector = 0;
static uint32_t g_root_dir_sectors = 0;
static uint32_t g_first_data_sector = 0;

static uint16_t fat16_get_entry(uint16_t cluster) {
    uint32_t fat_offset = (uint32_t)cluster * 2u;
    uint32_t fat_sector = g_bpb.reserved_sector_count + (fat_offset / g_bpb.bytes_per_sector);
    uint32_t ent_offset = fat_offset % g_bpb.bytes_per_sector;
    uint8_t sec[512];
    if (ramdisk_read_sector(fat_sector, sec) != 0) return 0xFFFF;
    return (uint16_t)(sec[ent_offset] | ((uint16_t)sec[ent_offset + 1] << 8));
}

static int name_match_83(const fat_dir_entry_t *e, const char *filename) {
    char target[11];
    for (int i=0;i<11;i++) target[i] = ' ';
    int i=0,j=0;
    while (filename[i] && filename[i] != '.' && j < 8) { char c=filename[i++]; if(c>='a'&&c<='z') c-=32; target[j++]=c; }
    if (filename[i]=='.') { i++; j=8; int k=0; while(filename[i] && k<3){ char c=filename[i++]; if(c>='a'&&c<='z') c-=32; target[j++]=c; k++; }}
    for (int n=0;n<8;n++) if ((char)e->name[n] != target[n]) return 0;
    for (int n=0;n<3;n++) if ((char)e->ext[n] != target[8+n]) return 0;
    return 1;
}

int fat_init(void) {
    uint8_t sec[512];
    if (ramdisk_read_sector(0, sec) != 0) return -1;
    fat_bpb_t *bpb = (fat_bpb_t*)sec;
    g_bpb = *bpb;
    if (g_bpb.bytes_per_sector != 512 || g_bpb.fat_size_16 == 0 || g_bpb.sectors_per_cluster == 0) return -1;

    g_root_dir_sectors = ((uint32_t)g_bpb.root_entry_count * 32u + (g_bpb.bytes_per_sector - 1u)) / g_bpb.bytes_per_sector;
    g_root_dir_sector = g_bpb.reserved_sector_count + ((uint32_t)g_bpb.fat_count * g_bpb.fat_size_16);
    g_first_data_sector = g_root_dir_sector + g_root_dir_sectors;
    return 0;
}

void fat_read_directory(void) {
    uint8_t sec[512];
    for (uint32_t s=0; s<g_root_dir_sectors; ++s) {
        if (ramdisk_read_sector(g_root_dir_sector + s, sec) != 0) break;
        for (uint32_t off=0; off<512; off += sizeof(fat_dir_entry_t)) {
            fat_dir_entry_t *e = (fat_dir_entry_t*)(sec + off);
            if (e->name[0] == 0x00) return;
            if (e->name[0] == 0xE5 || (e->attr & 0x0F) == 0x0F) continue;
        }
    }
}

int fat_read_file(const char *filename, uint8_t *buffer, uint32_t *out_size) {
    if (!filename || !buffer) return -1;
    uint8_t sec[512];
    fat_dir_entry_t found; int ok=0;
    for (uint32_t s=0; s<g_root_dir_sectors && !ok; ++s) {
        if (ramdisk_read_sector(g_root_dir_sector + s, sec) != 0) return -1;
        for (uint32_t off=0; off<512; off += sizeof(fat_dir_entry_t)) {
            fat_dir_entry_t *e = (fat_dir_entry_t*)(sec + off);
            if (e->name[0] == 0x00) break;
            if (e->name[0] == 0xE5 || (e->attr & 0x0F) == 0x0F) continue;
            if (name_match_83(e, filename)) { found = *e; ok = 1; break; }
        }
    }
    if (!ok) return -1;

    uint16_t cluster = found.fst_clus_lo;
    uint32_t remaining = found.file_size;
    uint32_t out_off = 0;
    while (cluster >= 2 && cluster < 0xFFF8 && remaining > 0) {
        uint32_t first_sector = g_first_data_sector + (uint32_t)(cluster - 2u) * g_bpb.sectors_per_cluster;
        for (uint32_t sc=0; sc<g_bpb.sectors_per_cluster && remaining > 0; ++sc) {
            if (ramdisk_read_sector(first_sector + sc, sec) != 0) return -1;
            uint32_t to_copy = remaining > 512 ? 512 : remaining;
            for (uint32_t i=0;i<to_copy;i++) buffer[out_off + i] = sec[i];
            out_off += to_copy;
            remaining -= to_copy;
        }
        cluster = fat16_get_entry(cluster);
    }
    if (out_size) *out_size = found.file_size;
    return 0;
}
