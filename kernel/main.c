#include "kernel.h"
#include "console.h"
#include "scheduler.h"
#include "memory.h"
#include "process.h"
#include "syscall.h"
#include "ipc.h"
#include "events.h"
#include "shared_memory.h"
#include "plugin.h"
#include "audio.h"
#include "ai_cmd.h"
#include "security/permissions.h"
#include "security/sandbox.h"
#include "../drivers/hal.h"
#include "../fs/kfs.h"

void yk_keyboard_init(void);
void yk_mouse_init(void);
void yk_disk_init(void);
void yk_touch_init(void);
void zk_framebuffer_init(void);
void zk_window_manager_init(void);
void zk_render_init(void);
void zk_render_frame(void);
void zk_theme_init(void);
void zk_desktop_init(void);
void zk_notifications_init(void);
void zk_debug_panel_init(void);

/*
 * kernel_main: KONE OS çekirdek başlangıç akışı.
 * Geliştirme sırası: boot -> X -> Y -> Z -> GUI/KFS.
 */
void kernel_main(void) {
    console_clear();
    console_puts("KONE OS booting...\n");

    /* X Kernel */
    xk_memory_init();
    xk_scheduler_init();
    xk_process_init();
    xk_syscall_init();

    ipc_init();
    event_system_init();
    shm_init();
    plugin_system_init();
    audio_system_init();
    ai_cmd_init();
    security_permissions_init();
    sandbox_init();

    /* Y Kernel */
    yk_hal_init();
    yk_keyboard_init();
    yk_mouse_init();
    yk_disk_init();
    yk_touch_init();

    /* Z Kernel */
    zk_framebuffer_init();
    zk_window_manager_init();
    zk_render_init();
    zk_theme_init();
    zk_desktop_init();
    zk_notifications_init();
    zk_debug_panel_init();

    kfs_init();
    kfs_mkdir("apps");

    security_register_app("terminal", 1);
    security_grant("terminal", PERM_FS_READ);
    security_grant("terminal", PERM_UI_WINDOW);
    sandbox_configure("terminal", 4096, 20);
    plugin_register("debug.overlay", 1);
    audio_beep(880, 120);
    ai_cmd_execute("open terminal");

    console_puts("KONE OS initialized.\n");

    for (;;) {
        xk_scheduler_tick();
        zk_render_frame();
        __asm__ volatile ("hlt");
    }
}
