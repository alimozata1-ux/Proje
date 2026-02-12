#include "kernel_mode.h"
#include "string.h"
#include "vga.h"

typedef struct {
    const char* name;
    const char* style;
} kernel_service_t;

static kernel_mode_t g_kernel_mode = KERNEL_MODE_HYBRID;

static const kernel_service_t services[] = {
    {"scheduler", "kernel-core"},
    {"paging", "kernel-core"},
    {"syscall", "kernel-core"},
    {"driver-manager", "user-service"},
    {"browser", "user-service"},
    {"notifications", "user-service"},
    {"games", "user-service"}
};

void kernel_mode_init(void) {
    g_kernel_mode = KERNEL_MODE_HYBRID;
}

kernel_mode_t kernel_mode_get(void) {
    return g_kernel_mode;
}

const char* kernel_mode_name(void) {
    return g_kernel_mode == KERNEL_MODE_HYBRID ? "hybrid" : "monolithic";
}

int kernel_mode_set_name(const char* name) {
    if (kstrcmp(name, "hybrid") == 0) {
        g_kernel_mode = KERNEL_MODE_HYBRID;
        return 0;
    }
    if (kstrcmp(name, "monolithic") == 0) {
        g_kernel_mode = KERNEL_MODE_MONOLITHIC;
        return 0;
    }
    return -1;
}

void kernel_mode_print_services(void) {
    int i;
    vga_write_string("kernel services (hybrid profile):\n");
    for (i = 0; i < (int)(sizeof(services) / sizeof(services[0])); i++) {
        vga_write_string("  ");
        vga_write_string(services[i].name);
        vga_write_string(" -> ");
        vga_write_string(services[i].style);
        vga_write_string("\n");
    }
}
