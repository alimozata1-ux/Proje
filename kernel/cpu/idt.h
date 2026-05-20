#ifndef IDT_H
#define IDT_H

#include <stdint.h>

typedef struct {
    uint32_t ds;
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax;
    uint32_t int_no, err_code;
    uint32_t eip, cs, eflags, useresp, ss;
} registers_t;

void idt_init(void);
void irq_install_handler(uint8_t irq, void (*handler)(registers_t *r));
void irq_uninstall_handler(uint8_t irq);
void isr_handler(registers_t *r);
void irq_handler(registers_t *r);
void isr_install_handler(uint8_t isr, void (*handler)(registers_t *r));

#endif
