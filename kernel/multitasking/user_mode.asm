BITS 32

global switch_to_user_mode

switch_to_user_mode:
    mov eax, [esp + 4]
    cli
    mov dx, 0x23
    mov ds, dx
    mov es, dx
    mov fs, dx
    mov gs, dx

    push dword 0x23
    push dword 0x800000
    pushfd
    pop ecx
    or ecx, 0x200
    push ecx
    push dword 0x1B
    push eax
    iretd
