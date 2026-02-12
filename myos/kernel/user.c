#include "user.h"

__attribute__((section(".user"))) static const char user_msg[] = "[ring3] int 0x80 ile yazildi\n";
__attribute__((section(".user"))) static unsigned char user_stack[4096];

__attribute__((section(".user"))) static void user_program(void) {
    __asm__ __volatile__(
        "mov $1, %%eax\n"
        "mov %0, %%ebx\n"
        "int $0x80\n"
        :
        : "r"(user_msg)
        : "eax", "ebx");

    for (;;) {
        __asm__ __volatile__("nop");
    }
}

void user_mode_demo(void) {
    /* Demo çağrısı scheduler tarafından yapılır. */
}

unsigned int user_entry_point(void) {
    return (unsigned int)user_program;
}

unsigned int user_stack_top(void) {
    return (unsigned int)&user_stack[4095];
}
