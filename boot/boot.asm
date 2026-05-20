; boot/boot.asm
; 16-bit bootloader -> VESA setup -> disk load -> protected mode -> kernel_main

BITS 16
ORG 0x7C00

KERNEL_LOAD_ADDR        EQU 0x1000
KERNEL_SECTOR_COUNT     EQU 64          ; Enough for early kernel binary (<32 KiB)
VBE_MODE_INFO_SEG       EQU 0x0000
VBE_MODE_INFO_OFF       EQU 0x8000
BOOT_INFO_SEG           EQU 0x0000
BOOT_INFO_OFF           EQU 0x9000
STACK_TOP_REAL          EQU 0x7C00

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, STACK_TOP_REAL
    sti

    mov [boot_drive], dl

    ; Query VBE mode info for 1024x768x32 (mode 0x118)
    mov ax, VBE_MODE_INFO_SEG
    mov es, ax
    mov di, VBE_MODE_INFO_OFF
    mov cx, 0x0118
    mov ax, 0x4F01
    int 0x10
    cmp ax, 0x004F
    jne vbe_fail

    ; Set VBE mode with LFB bit (0x4000 | 0x118)
    mov bx, 0x4118
    mov ax, 0x4F02
    int 0x10
    cmp ax, 0x004F
    jne vbe_fail

    ; Save boot info for kernel
    ; boot_info layout (dword aligned):
    ; +0 lfb_addr
    ; +4 width
    ; +8 height
    ; +12 bpp
    mov si, VBE_MODE_INFO_OFF

    ; PhysBasePtr @ offset 40h (dword)
    mov eax, [si + 0x28]
    mov [BOOT_INFO_OFF + 0], eax

    ; XResolution @ 12h (word)
    xor eax, eax
    mov ax, [si + 0x12]
    mov [BOOT_INFO_OFF + 4], eax

    ; YResolution @ 14h (word)
    xor eax, eax
    mov ax, [si + 0x14]
    mov [BOOT_INFO_OFF + 8], eax

    ; BitsPerPixel @ 19h (byte)
    xor eax, eax
    mov al, [si + 0x19]
    mov [BOOT_INFO_OFF + 12], eax

    ; Load kernel from disk (LBA 1..KERNEL_SECTOR_COUNT) to 0x1000
    mov ax, KERNEL_LOAD_ADDR
    mov es, ax
    xor bx, bx

    mov ah, 0x02
    mov al, KERNEL_SECTOR_COUNT
    mov ch, 0x00
    mov cl, 0x02
    mov dh, 0x00
    mov dl, [boot_drive]
    int 0x13
    jc disk_fail

    cli
    lgdt [gdt_descriptor]

    mov eax, cr0
    or eax, 0x1
    mov cr0, eax

    jmp 0x08:protected_mode_entry

vbe_fail:
    mov si, vbe_fail_msg
    call print_string
    jmp halt

disk_fail:
    mov si, disk_fail_msg
    call print_string
    jmp halt

print_string:
    mov ah, 0x0E
.print_next:
    lodsb
    test al, al
    jz .done
    int 0x10
    jmp .print_next
.done:
    ret

halt:
    cli
.hlt_loop:
    hlt
    jmp .hlt_loop

boot_drive db 0
vbe_fail_msg db 'VBE init failed', 0
disk_fail_msg db 'Kernel load failed', 0

; -------------------------
; 32-bit section
; -------------------------
BITS 32
protected_mode_entry:
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x9FC00

    ; Jump to linked kernel entry at 0x1000
    jmp 0x08:KERNEL_LOAD_ADDR

; -------------------------
; GDT
; -------------------------
BITS 16
gdt_start:
    dq 0x0000000000000000
    dq 0x00CF9A000000FFFF   ; code segment
    dq 0x00CF92000000FFFF   ; data segment
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start

times 510-($-$$) db 0
dw 0xAA55
