ENTRY(_start)

SECTIONS {
    . = 0x1000;

    __kernel_start = .;

    .text : {
        *(.text*)
    }

    .rodata : {
        *(.rodata*)
    }

    .data : {
        *(.data*)
    }

    .bss : {
        *(.bss*)
        *(COMMON)
    }

    . = ALIGN(4096);
    __user_start = .;
    .user : {
        *(.user*)
    }
    __user_end = .;

    . = ALIGN(4096);
    __heap_start = .;
    . = . + 0x20000;
    __heap_end = .;

    __kernel_end = .;
}
