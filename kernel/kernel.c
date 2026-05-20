#include <stdint.h>
#include <stddef.h>
#include "graphics.h"
#include "cpu/idt.h"
#include "multitasking/task.h"
#include "gui/window.h"
#include "storage/ramdisk.h"
#include "fs/fat.h"
#include "loader/elf.h"
#include "net/net_stack.h"
#include "drivers/rtl8139.h"
#include "config/sys_env.h"

#define BOOT_INFO_ADDR 0x00009000u
#define XP_DESKTOP_BLUE 0x00245EDDu

struct boot_info { uint32_t lfb_addr, width, height, bpp; };

void timer_init(uint32_t frequency_hz); void keyboard_init(void); void mouse_init(void);
void gui_draw_mouse_cursor(void); void draw_window_frame(Window *win); void draw_taskbar(void); void syscall_init(void); void switch_to_user_mode(uint32_t entry_point);
void desktop_init(void); void desktop_draw(void);
void start_menu_init(void); void start_menu_draw(void);
void ui_event_pump(void);
void apps_render(void);
void launch_browser(void);
void launch_minesweeper(void);
void launch_terminal(void);
void launch_settings(void);
extern volatile uint8_t frame_ready;

static uint8_t elf_image[65536];

static void render_scene(void) {
    clear_screen(XP_DESKTOP_BLUE);
    desktop_draw();
    for (uint32_t i = 0; i < window_count(); ++i) { Window *w = window_get_by_index(i); if (w) draw_window_frame(w); }
    draw_taskbar();
    start_menu_draw();
    apps_render();
    gui_draw_mouse_cursor();
    screen_blit();
}

void kernel_main(void) {
    const struct boot_info *info = (const struct boot_info *)(uintptr_t)BOOT_INFO_ADDR;
    gdt_sanity_check(); graphics_init(info->lfb_addr, info->width, info->height, info->bpp);

    idt_init(); tasking_init(); timer_init(100); keyboard_init(); mouse_init(); syscall_init();
    sys_env_init();
    net_stack_init();
    (void)rtl8139_init();
    window_manager_init();
    desktop_init();
    start_menu_init();
    window_create("Dosya Gezgini", 120, 100, 360, 240, 1);
    window_create("Terminal", 280, 180, 340, 220, 1);
    launch_browser();
    launch_minesweeper();
    launch_terminal();
    launch_settings();

    ramdisk_init();
    if (fat_init() == 0) {
        uint32_t fsz = 0;
        if (fat_read_file("NOTEPAD.ELF", elf_image, &fsz) == 0 || fat_read_file("CALC.ELF", elf_image, &fsz) == 0) {
            uint32_t entry = elf_load(elf_image);
            if (entry) switch_to_user_mode(entry);
        }
    }

    __asm__ __volatile__("sti");
    for (;;) { ui_event_pump(); if (frame_ready) { frame_ready = 0; render_scene(); } __asm__ __volatile__("hlt"); }
}
