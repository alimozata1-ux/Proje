#include "paging.h"
#include "vga.h"

extern unsigned int __user_start;
extern unsigned int __user_end;

static unsigned int page_directory[1024] __attribute__((aligned(4096)));
static unsigned int first_page_table[1024] __attribute__((aligned(4096)));

static void load_page_directory(unsigned int* dir) {
    __asm__ __volatile__("mov %0, %%cr3" : : "r"(dir));
}

static void enable_paging(void) {
    unsigned int cr0;
    __asm__ __volatile__("mov %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000U;
    __asm__ __volatile__("mov %0, %%cr0" : : "r"(cr0));
}

void paging_init(void) {
    unsigned int i;
    unsigned int user_start_page = ((unsigned int)&__user_start) >> 12;
    unsigned int user_end_page = (((unsigned int)&__user_end) + 0xFFFU) >> 12;

    for (i = 0; i < 1024; i++) {
        page_directory[i] = 0x00000002U;
        first_page_table[i] = (i * 0x1000U) | 0x003U; /* present + rw, supervisor */
    }

    /* VGA belleği user mode'da erişilemesin. */
    first_page_table[0xB8] = (0xB8000U) | 0x003U;

    /* Sadece user kod bölgesini user-accessible yap. */
    for (i = user_start_page; i < user_end_page && i < 1024; i++) {
        first_page_table[i] = (i * 0x1000U) | 0x007U; /* present + rw + user */
    }

    page_directory[0] = ((unsigned int)first_page_table) | 0x003U;

    load_page_directory(page_directory);
    enable_paging();
}

void page_fault_handler(void) {
    vga_write_string("Page fault!\n");
}
