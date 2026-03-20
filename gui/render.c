#include "include/gui_core.h"
#include "../kernel/console.h"

/*
 * Basit kompozitör:
 * - Arka plan + status bar + taskbar
 * - Z-order'a göre pencereleri çiz
 * Bu MVP'de gerçek piksel çıktısı yerine yaşam döngüsü iskeleti sağlanır.
 */

static int frame_counter = 0;

void zk_render_frame(void) {
    frame_counter++;
    (void)frame_counter;
}

void zk_render_init(void) {
    frame_counter = 0;
    console_puts("[Z] Layered renderer + animation engine initialized\n");
}
