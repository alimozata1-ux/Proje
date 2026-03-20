CC := gcc
LD := ld
AS := gcc

CFLAGS_KERNEL := -m32 -ffreestanding -fno-pic -fno-stack-protector -nostdlib -nostdinc -Wall -Wextra -I.
LDFLAGS_KERNEL := -m elf_i386 -T boot/linker.ld

HOST_CFLAGS := -Wall -Wextra -O2

BUILD := build
ISO_DIR := $(BUILD)/iso
BIN_DIR := $(BUILD)/bin
OBJ_DIR := $(BUILD)/obj

KERNEL_OBJS := \
	$(OBJ_DIR)/boot.o \
	$(OBJ_DIR)/kernel_main.o \
	$(OBJ_DIR)/kernel_console.o \
	$(OBJ_DIR)/kernel_scheduler.o \
	$(OBJ_DIR)/kernel_memory.o \
	$(OBJ_DIR)/kernel_process.o \
	$(OBJ_DIR)/kernel_syscall.o \
	$(OBJ_DIR)/kernel_panic.o \
	$(OBJ_DIR)/kernel_ipc.o \
	$(OBJ_DIR)/kernel_events.o \
	$(OBJ_DIR)/kernel_shared_memory.o \
	$(OBJ_DIR)/kernel_plugin.o \
	$(OBJ_DIR)/kernel_audio.o \
	$(OBJ_DIR)/kernel_ai_cmd.o \
	$(OBJ_DIR)/kernel_permissions.o \
	$(OBJ_DIR)/kernel_sandbox.o \
	$(OBJ_DIR)/lib_string.o \
	$(OBJ_DIR)/driver_hal.o \
	$(OBJ_DIR)/driver_keyboard.o \
	$(OBJ_DIR)/driver_mouse.o \
	$(OBJ_DIR)/driver_disk.o \
	$(OBJ_DIR)/driver_touch.o \
	$(OBJ_DIR)/gui_fb.o \
	$(OBJ_DIR)/gui_wm.o \
	$(OBJ_DIR)/gui_render.o \
	$(OBJ_DIR)/gui_theme.o \
	$(OBJ_DIR)/gui_desktop.o \
	$(OBJ_DIR)/gui_notifications.o \
	$(OBJ_DIR)/gui_debug_panel.o \
	$(OBJ_DIR)/fs_kfs.o

.PHONY: all kernel host-tools iso run-qemu clean stats py-vm

all: kernel host-tools

$(OBJ_DIR):
	@mkdir -p $(OBJ_DIR) $(BIN_DIR)

kernel: $(OBJ_DIR) $(KERNEL_OBJS)
	$(LD) $(LDFLAGS_KERNEL) -o $(BIN_DIR)/koneos.bin $(KERNEL_OBJS)

$(OBJ_DIR)/boot.o: boot/boot.s | $(OBJ_DIR)
	$(AS) -m32 -c $< -o $@

$(OBJ_DIR)/kernel_main.o: kernel/main.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_console.o: kernel/console.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_scheduler.o: kernel/scheduler.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_memory.o: kernel/memory.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_process.o: kernel/process.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_syscall.o: kernel/syscall.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_panic.o: kernel/panic.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_ipc.o: kernel/ipc.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_events.o: kernel/events.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_shared_memory.o: kernel/shared_memory.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_plugin.o: kernel/plugin.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_audio.o: kernel/audio.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_ai_cmd.o: kernel/ai_cmd.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_permissions.o: kernel/security/permissions.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/kernel_sandbox.o: kernel/security/sandbox.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/lib_string.o: lib/kone_string.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/driver_hal.o: drivers/hal.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/driver_keyboard.o: drivers/keyboard.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/driver_mouse.o: drivers/mouse.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/driver_disk.o: drivers/disk.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/driver_touch.o: drivers/touch.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_fb.o: gui/framebuffer.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_wm.o: gui/window_manager.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_render.o: gui/render.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_theme.o: gui/theme.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_desktop.o: gui/desktop.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_notifications.o: gui/notifications.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/gui_debug_panel.o: gui/debug_panel.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

$(OBJ_DIR)/fs_kfs.o: fs/kfs.c | $(OBJ_DIR)
	$(CC) $(CFLAGS_KERNEL) -c $< -o $@

host-tools: | $(OBJ_DIR)
	$(CC) $(HOST_CFLAGS) compiler/src/main.c compiler/src/lexer.c compiler/src/parser.c -o $(BIN_DIR)/konec
	$(CC) $(HOST_CFLAGS) vm/konevm.c -o $(BIN_DIR)/konevm

iso: kernel
	mkdir -p $(ISO_DIR)/boot/grub
	cp $(BIN_DIR)/koneos.bin $(ISO_DIR)/boot/koneos.bin
	cp boot/grub/grub.cfg $(ISO_DIR)/boot/grub/grub.cfg
	grub-mkrescue -o $(BUILD)/koneos.iso $(ISO_DIR)

run-qemu: iso
	qemu-system-i386 -cdrom $(BUILD)/koneos.iso -m 256 -serial stdio

py-vm:
	python3 vm/konevm_py.py build/hello.mars32 --debug

stats:
	@echo "C/Headers lines:" && wc -l $$(rg --files -g'*.c' -g'*.h' -g'*.s' -g'*.ld') | tail -n 1

clean:
	rm -rf $(BUILD)
