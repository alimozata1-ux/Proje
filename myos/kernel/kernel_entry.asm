[bits 32]

[extern kernel_main]
[extern timer_irq_handler]
[extern keyboard_irq_dispatch]
[extern page_fault_handler]
[extern syscall_handler]

global _start
global isr_irq0
global isr_irq1
global isr_page_fault
global isr_syscall
global idt_load
global enter_user_mode

_start:
    mov esp, 0x90000
    call kernel_main

.hang:
    cli
    hlt
    jmp .hang

isr_irq0:
    pusha
    call timer_irq_handler
    popa
    iretd

isr_irq1:
    pusha
    call keyboard_irq_dispatch
    popa
    iretd

isr_page_fault:
    pusha
    call page_fault_handler
    popa
    add esp, 4
    iretd

isr_syscall:
    pusha
    call syscall_handler
    popa
    iretd

idt_load:
    mov eax, [esp + 4]
    lidt [eax]
    ret

enter_user_mode:
    ; stack: [esp+4]=eip, [esp+8]=user_esp
    mov eax, [esp + 4]
    mov edx, [esp + 8]

    mov ax, 0x23
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    push dword 0x23
    push edx
    pushfd
    push dword 0x1B
    push eax
    iretd
