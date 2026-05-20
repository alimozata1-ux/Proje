#include "elf.h"

uint32_t elf_load(uint8_t *elf_buffer) {
    if (!elf_buffer) return 0;
    Elf32_Ehdr *eh = (Elf32_Ehdr*)elf_buffer;
    if (eh->e_ident[0] != 0x7F || eh->e_ident[1] != 'E' || eh->e_ident[2] != 'L' || eh->e_ident[3] != 'F') return 0;
    if (eh->e_ident[4] != 1 || eh->e_ident[5] != 1) return 0;

    for (uint16_t i = 0; i < eh->e_phnum; ++i) {
        Elf32_Phdr *ph = (Elf32_Phdr*)(elf_buffer + eh->e_phoff + (uint32_t)i * eh->e_phentsize);
        if (ph->p_type != PT_LOAD) continue;
        uint8_t *src = elf_buffer + ph->p_offset;
        uint8_t *dst = (uint8_t*)(uintptr_t)(ph->p_paddr ? ph->p_paddr : ph->p_vaddr);
        for (uint32_t b = 0; b < ph->p_filesz; ++b) dst[b] = src[b];
        for (uint32_t b = ph->p_filesz; b < ph->p_memsz; ++b) dst[b] = 0;
    }
    return eh->e_entry;
}
