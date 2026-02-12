#ifndef KERNEL_MODE_H
#define KERNEL_MODE_H

typedef enum {
    KERNEL_MODE_MONOLITHIC = 0,
    KERNEL_MODE_HYBRID = 1
} kernel_mode_t;

void kernel_mode_init(void);
kernel_mode_t kernel_mode_get(void);
int kernel_mode_set_name(const char* name);
const char* kernel_mode_name(void);
void kernel_mode_print_services(void);

#endif
